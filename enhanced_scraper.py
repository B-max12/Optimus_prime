import requests
from bs4 import BeautifulSoup
from smart_url_handler import SmartURLHandler
import re
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class EnhancedScraper:
    def __init__(self):
        self.url_handler = SmartURLHandler()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def setup_selenium_driver(self, headless=False):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Driver setup error: {e}")
            return None
    
    def scrape_shopping_products(self, url, product_name):
        """Scrape products from shopping websites with visible browser"""
        driver = self.setup_selenium_driver(headless=False)
        if not driver:
            return None
        
        try:
            # Open the website
            driver.get(url)
            time.sleep(3)
            
            # Different search strategies for different websites
            if 'amazon' in url:
                search_box = driver.find_element(By.ID, "twotabsearchtextbox")
                search_box.send_keys(product_name)
                search_box.submit()
                time.sleep(3)
                
                # Extract product data
                products = []
                product_elements = driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
                
                for product in product_elements[:10]:  # First 10 products
                    try:
                        name = product.find_element(By.CSS_SELECTOR, "h2 a span").text
                        price = product.find_element(By.CSS_SELECTOR, ".a-price-whole").text
                        rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("innerHTML")
                        
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'website': 'Amazon'
                        })
                    except:
                        continue
                
                return products
                
            elif 'daraz' in url:
                search_box = driver.find_element(By.ID, "q")
                search_box.send_keys(product_name)
                search_box.submit()
                time.sleep(3)
                
                products = []
                product_elements = driver.find_elements(By.CSS_SELECTOR, ".c2prKC")
                
                for product in product_elements[:10]:
                    try:
                        name = product.find_element(By.CSS_SELECTOR, ".c16H9d a").text
                        price = product.find_element(By.CSS_SELECTOR, ".c3gUW0").text
                        rating = product.find_element(By.CSS_SELECTOR, ".c2X1Wt").text
                        
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': rating,
                            'website': 'Daraz'
                        })
                    except:
                        continue
                
                return products
                
            else:
                # Generic scraping for other shopping sites
                products = []
                product_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='product'], [class*='item']")
                
                for product in product_elements[:15]:
                    try:
                        name = product.find_element(By.CSS_SELECTOR, "h1, h2, h3, [class*='title'], [class*='name']").text
                        
                        # Try to find price
                        price_selectors = [".price", ".cost", ".amount", "[class*='price']"]
                        price = "Not found"
                        for selector in price_selectors:
                            try:
                                price = product.find_element(By.CSS_SELECTOR, selector).text
                                break
                            except:
                                continue
                        
                        products.append({
                            'name': name,
                            'price': price,
                            'rating': "Not available",
                            'website': url
                        })
                    except:
                        continue
                
                return products
                
        except Exception as e:
            print(f"Shopping scrape error: {e}")
            return None
        finally:
            # Don't close driver - keep browser open
            pass
    
    def save_to_excel(self, data, filename):
        """Save data to Excel file"""
        try:
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False)
            print(f"Data saved to {filename}")
            return True
        except Exception as e:
            print(f"Excel save error: {e}")
            return False
    
    def save_to_html_report(self, data, filename):
        """Save data as HTML report"""
        try:
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Product Scraping Report</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    tr:nth-child(even) { background-color: #f9f9f9; }
                    .best-product { background-color: #e8f5e8 !important; }
                </style>
            </head>
            <body>
                <h1>🛍️ Product Scraping Report</h1>
                <p>Generated on: """ + time.strftime("%Y-%m-%d %H:%M:%S") + """</p>
                <table>
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th>Price</th>
                            <th>Rating</th>
                            <th>Website</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Find best rated product
            best_rating = 0
            best_product = None
            for product in data:
                try:
                    rating_text = str(product.get('rating', '0'))
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        if rating > best_rating:
                            best_rating = rating
                            best_product = product
                except:
                    continue
            
            # Add products to HTML
            for product in data:
                is_best = product == best_product
                row_class = "class='best-product'" if is_best else ""
                
                html_content += f"""
                <tr {row_class}>
                    <td>{product.get('name', 'N/A')}</td>
                    <td>{product.get('price', 'N/A')}</td>
                    <td>{product.get('rating', 'N/A')}</td>
                    <td>{product.get('website', 'N/A')}</td>
                </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            """
            
            # Add best product highlight
            if best_product:
                html_content += f"""
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>🏆 Best Rated Product</h3>
                    <p><strong>Name:</strong> {best_product.get('name', 'N/A')}</p>
                    <p><strong>Price:</strong> {best_product.get('price', 'N/A')}</p>
                    <p><strong>Rating:</strong> {best_product.get('rating', 'N/A')}</p>
                    <p><strong>Website:</strong> {best_product.get('website', 'N/A')}</p>
                </div>
                """
            
            html_content += """
            </body>
            </html>
            """
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML report saved to {filename}")
            return True
            
        except Exception as e:
            print(f"HTML save error: {e}")
            return False