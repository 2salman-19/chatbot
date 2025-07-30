import pdfplumber
import json
import os

pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'jazz_packages.pdf'))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'jazz_packages.json'))

def extract_pdf_data(pdf_path):
    packages = []
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {os.path.abspath(pdf_path)}. Please check the path and ensure the file exists.")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            current_package = {}
            for line in lines:
                if line.startswith("Name:"):
                    if current_package:
                        packages.append(current_package)
                    current_package = {"Name": line.replace("Name:", "").strip()}
                elif line.startswith("Description:"):
                    current_package["Description"] = line.replace("Description:", "").strip()
                elif line.startswith("Validity:"):
                    current_package["Validity"] = line.replace("Validity:", "").strip()
                elif line.startswith("Price:"):
                    current_package["Price"] = line.replace("Price:", "").strip()
                elif line.startswith("Activation Code:"):
                    current_package["Activation Code"] = line.replace("Activation Code:", "").strip()
            if current_package:
                packages.append(current_package)
    return packages

if __name__ == "__main__":
    try:
        packages = extract_pdf_data(pdf_path)
        print(f"Extracted {len(packages)} packages.")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(packages, f, ensure_ascii=False, indent=2)
        print(f"Saved to {output_path}")
        # print(packages)
    except Exception as e:
        print(f"Error: {e}")