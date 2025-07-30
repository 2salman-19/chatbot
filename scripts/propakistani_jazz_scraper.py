import os
import json
import time
import re
from dotenv import load_dotenv
from agentql import wrap
from playwright.sync_api import sync_playwright

def human_delay(a=1, b=2):
    time.sleep(a + (b - a) * 0.5)

def extract_package_from_row(row):
    """Extract package details from a table row"""
    try:
        # Get package name and link
        name_cell = row.query_selector('.package-name a')
        package_name = name_cell.inner_text().strip() if name_cell else "Unknown Package"
        package_url = name_cell.get_attribute('href') if name_cell else None
        
        # Get all cells
        cells = row.query_selector_all('td')
        if len(cells) < 8:
            return None
        
        # Extract data from cells
        onnet_mins = cells[2].inner_text().strip() if len(cells) > 2 else "--"
        offnet_mins = cells[3].inner_text().strip() if len(cells) > 3 else "--"
        sms = cells[4].inner_text().strip() if len(cells) > 4 else "--"
        data_mb = cells[5].inner_text().strip() if len(cells) > 5 else "--"
        validity = cells[6].inner_text().strip() if len(cells) > 6 else "--"
        
        # Extract price
        price_cell = cells[7] if len(cells) > 7 else None
        price = "0"
        if price_cell:
            price_elem = price_cell.query_selector('.pack-price')
            if price_elem:
                price_text = price_elem.inner_text().strip()
                # Extract numeric price
                price_match = re.search(r'Rs\.(\d+(?:\.\d+)?)', price_text)
                if price_match:
                    price = price_match.group(1)
        
        # Get subscription link and check for subscription code
        subscribe_link = None
        subscription_code = None
        if price_cell:
            subscribe_elem = price_cell.query_selector('a.btn')
            if subscribe_elem:
                subscribe_link = subscribe_elem.get_attribute('href')
                # Check if subscription code is in the button text
                button_text = subscribe_elem.inner_text().strip()
                if '*' in button_text and '#' in button_text:
                    subscription_code = button_text
        
        return {
            'package_name': package_name,
            'package_url': package_url,
            'onnet_mins': onnet_mins,
            'offnet_mins': offnet_mins,
            'sms': sms,
            'data_mb': data_mb,
            'validity': validity,
            'price_rs': price,
            'subscribe_url': subscribe_link,
            'subscription_code': subscription_code
        }
    except Exception as e:
        print(f"Error extracting package from row: {e}")
        return None

def extract_subscription_code_from_page(page):
    """Extract subscription code from the Mechanics section"""
    try:
        # Look for Mechanics section
        mechanics_selectors = [
            'h2:contains("Mechanics")',
            'h3:contains("Mechanics")',
            'h4:contains("Mechanics")',
            '.mechanics',
            '[class*="mechanics"]',
            'div:contains("Mechanics")'
        ]
        
        # Also look for subscription code patterns
        code_patterns = [
            r'SUB\s*\*\d+#',
            r'\*\d+#',
            r'Dial\s*\*\d+#',
            r'Code:\s*\*\d+#',
            r'Subscription:\s*\*\d+#',
            r'Activation:\s*\*\d+#',
            r'Subscribe:\s*\*\d+#'
        ]
        
        page_content = page.content()
        
        # First try to find Mechanics section
        for selector in mechanics_selectors:
            try:
                mechanics_elem = page.query_selector(selector)
                if mechanics_elem:
                    mechanics_text = mechanics_elem.inner_text()
                    # Look for subscription code in mechanics text
                    for pattern in code_patterns:
                        match = re.search(pattern, mechanics_text, re.IGNORECASE)
                        if match:
                            return match.group(0).strip()
            except:
                continue
        
        # If no mechanics section found, search entire page content
        for pattern in code_patterns:
            match = re.search(pattern, page_content, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # Look for any text that contains subscription instructions
        subscription_texts = page.query_selector_all('p, div, span')
        for elem in subscription_texts:
            try:
                text = elem.inner_text()
                if any(keyword in text.lower() for keyword in ['dial', 'code', 'subscription', 'activate', 'subscribe']):
                    for pattern in code_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            return match.group(0).strip()
            except:
                continue
        
        return None
    except Exception as e:
        print(f"Error extracting subscription code: {e}")
        return None

def scrape_propakistani_jazz():
    load_dotenv()
    api_key = os.getenv('AGENTQL_API_KEY')
    if not api_key:
        raise RuntimeError('AGENTQL_API_KEY not set in environment variables or .env file.')

    url = 'https://propakistani.pk/packages/mobilink-jazz-packages/'
    all_packages = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = wrap(browser.new_page())
        
        print(f"Scraping: {url}")
        page.goto(url)
        human_delay(3, 5)
        
        # Get page info
        print(f"Page title: {page.title()}")
        
        # Find all package categories (including 3-day packages)
        categories = ['Daily', 'Weekly', 'Monthly', 'Others']
        
        # First, let's find all available categories on the page
        nav_items = page.query_selector_all('#myScrollspy li a')
        available_categories = []
        for item in nav_items:
            try:
                href = item.get_attribute('href')
                if href and href.startswith('#'):
                    category_name = href[1:]  # Remove the #
                    available_categories.append(category_name)
            except:
                continue
        
        print(f"Available categories: {available_categories}")
        
        # Use available categories or fallback to default
        categories_to_scrape = available_categories if available_categories else categories
        
        for category in categories_to_scrape:
            print(f"\n=== SCRAPING {category.upper()} PACKAGES ===")
            
            try:
                # Click on category tab if it exists
                category_tab = page.query_selector(f'a[href="#{category}"]')
                if category_tab:
                    category_tab.click()
                    human_delay(2, 3)
                
                # Find the table for this category
                table = page.query_selector(f'#{category} table#list-view')
                if not table:
                    print(f"No table found for {category} category")
                    continue
                
                # Get all package rows (skip header and ad rows)
                rows = table.query_selector_all('tbody tr')
                category_packages = []
                
                for row in rows:
                    # Skip ad rows (they have colspan=8)
                    if row.query_selector('td[colspan="8"]'):
                        continue
                    
                    # Skip if not a package row
                    if not row.get_attribute('data-row'):
                        continue
                    
                    package = extract_package_from_row(row)
                    if package:
                        package['category'] = category
                        category_packages.append(package)
                        
                        # Show subscription code if found in table
                        if package.get('subscription_code'):
                            print(f"  ✓ {package['package_name']} - Rs.{package['price_rs']} - Code: {package['subscription_code']}")
                        else:
                            print(f"  ✓ {package['package_name']} - Rs.{package['price_rs']}")
                
                all_packages.extend(category_packages)
                print(f"  Found {len(category_packages)} {category} packages")
                
            except Exception as e:
                print(f"Error processing {category} category: {e}")
                continue
        
        # Get detailed information for ALL packages by visiting their detail pages
        print(f"\n=== GETTING DETAILED INFORMATION FOR ALL PACKAGES ===")
        detailed_packages = []
        
        for i, package in enumerate(all_packages):
            if package.get('package_url'):
                try:
                    print(f"Getting details for: {package['package_name']} ({i+1}/{len(all_packages)})")
                    
                    # Open package page in new tab
                    new_page = browser.new_page()
                    new_page.goto(package['package_url'])
                    human_delay(2, 3)
                    
                    # Extract additional details
                    details = {}
                    
                    # Extract subscription code from Mechanics section
                    subscription_code = extract_subscription_code_from_page(new_page)
                    if subscription_code:
                        details['subscription_code'] = subscription_code
                        print(f"    ✓ Found subscription code: {subscription_code}")
                    else:
                        details['subscription_code'] = "Not found"
                        print(f"    ✗ No subscription code found")
                    
                    # Look for description
                    desc_selectors = [
                        '.package-description',
                        '.description', 
                        '.entry-content p',
                        '.post-content p',
                        'p'
                    ]
                    
                    for selector in desc_selectors:
                        desc_elem = new_page.query_selector(selector)
                        if desc_elem:
                            desc_text = desc_elem.inner_text().strip()
                            if len(desc_text) > 50:  # Only if it's substantial
                                details['description'] = desc_text
                                break
                    
                    # Look for terms and conditions
                    terms_selectors = [
                        '.terms',
                        '.conditions', 
                        '[class*="terms"]',
                        '[class*="conditions"]'
                    ]
                    
                    for selector in terms_selectors:
                        terms_elem = new_page.query_selector(selector)
                        if terms_elem:
                            details['terms_conditions'] = terms_elem.inner_text().strip()
                            break
                    
                    # Add details to package
                    package.update(details)
                    detailed_packages.append(package)
                    
                    new_page.close()
                    human_delay(1, 2)
                    
                except Exception as e:
                    print(f"Error getting details for {package['package_name']}: {e}")
                    detailed_packages.append(package)
            else:
                detailed_packages.append(package)
        
        browser.close()
    
    # Save results
    with open('propakistani_jazz_packages.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_packages, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== SCRAPING COMPLETE ===")
    print(f"Total packages found: {len(all_packages)}")
    print(f"Detailed packages: {len(detailed_packages)}")
    print(f"Results saved to: propakistani_jazz_packages.json")
    
    # Print summary
    print(f"\n=== PACKAGE SUMMARY ===")
    for category in categories_to_scrape:
        category_packages = [p for p in all_packages if p.get('category') == category]
        print(f"{category}: {len(category_packages)} packages")
    
    # Print subscription codes found
    packages_with_codes = [p for p in detailed_packages if p.get('subscription_code') and p['subscription_code'] != "Not found"]
    print(f"\nPackages with subscription codes: {len(packages_with_codes)}")
    
    # Show some examples of subscription codes
    if packages_with_codes:
        print(f"\n=== SUBSCRIPTION CODE EXAMPLES ===")
        for i, package in enumerate(packages_with_codes[:10]):
            print(f"{i+1}. {package['package_name']}: {package['subscription_code']}")
    
    return detailed_packages

if __name__ == '__main__':
    scrape_propakistani_jazz()