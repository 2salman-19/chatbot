import os
import json
import base64
import cv2
from dotenv import load_dotenv
from mistralai import Mistral
from PIL import Image
from langchain.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI

# Setup parser fallback
try:
    from langchain_core.output_parsers import JsonOutputParser
except ImportError:
    try:
        from langchain_community.output_parsers import JsonOutputParser
    except ImportError:
        class JsonOutputParser:
            def __init__(self, pydantic_object=None):
                self.pydantic_object = pydantic_object
            def get_format_instructions(self):
                return "Respond with a valid JSON object."
            def __call__(self, text):
                return json.loads(text)
            def parse(self, text):
                return json.loads(text)

# Load environment variables
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# Initialize clients
client = Mistral(api_key=api_key)
llm = ChatMistralAI(api_key=api_key, model="mistral-ocr-latest", temperature=0.2)
parser = JsonOutputParser()

# Prompt for extracting structured data
prompt = PromptTemplate(
    input_variables=["ocr_text"],
    template="""
You are given the raw text extracted from a mobile package image.

Extract the following JSON fields:
- package_name: the name of the package (e.g., 'Monthly Star')
- description: list of features (data, minutes, etc.)
- price: the price including currency

Text:
{ocr_text}

{format_instructions}
""",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Directory setup - Fixed path with raw string
screenshots_dir = r"D:\Cloudpacer\chatbot\jazz_packeges"
output_json = []

# Helper functions
def upscale_image_2x(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    upscaled = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    upscaled_path = os.path.join("upscaled_images", os.path.basename(image_path))
    os.makedirs("upscaled_images", exist_ok=True)
    cv2.imwrite(upscaled_path, upscaled)
    return upscaled_path

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_from_image(image_path):
    upscaled_path = upscale_image_2x(image_path)
    base64_image = encode_image(upscaled_path)
    try:
        # Use the correct OCR model name
        response = client.ocr.process(
            model="mistral-ocr-latest",
            document={"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
        )
        # Handle response properly
        if hasattr(response, 'model_dump_json'):
            data = json.loads(response.model_dump_json())
        elif hasattr(response, 'json'):
            data = json.loads(response.json())
        else:
            data = response if isinstance(response, dict) else json.loads(response)
        
        pages = data.get('pages', [])
        text = "\n\n".join([p.get("markdown", "") for p in pages])
        return text
    except Exception as e:
        print(f"❌ OCR error for {image_path}: {e}")
        return ""

def extract_package_info(ocr_text):
    """Extract package information using LLM"""
    try:
        # Use the modern invoke method instead of deprecated run
        result = prompt.invoke({"ocr_text": ocr_text})
        response = llm.invoke(result)
        json_data = parser.parse(response.content)
        return json_data
    except Exception as e:
        print(f"⚠️ LLM extraction error: {e}")
        return None

# Loop through all images
for filename in os.listdir(screenshots_dir):
    if filename.lower().endswith((".png", ".jpg", ".jpeg",".PNG")):
        image_path = os.path.join(screenshots_dir, filename)
        print(f"🔍 Processing: {filename}")

        ocr_text = ocr_from_image(image_path)
        if not ocr_text.strip():
            print(f"⚠️ Skipped {filename} (no text)")
            continue

        try:
            json_data = extract_package_info(ocr_text)
            if json_data:
                output_json.append({
                    "image": filename,
                    "extracted_data": json_data
                })
        except Exception as e:
            print(f"⚠️ JSON extraction failed for {filename}: {e}")

# Save results to a file
with open("extracted_packages.json", "w", encoding="utf-8") as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)

print("\n✅ Extraction complete! Results saved to 'extracted_packages.json'")
