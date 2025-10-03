import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from datetime import datetime
import random
import re
from urllib.parse import quote

class KabumScraper:
    def __init__(self):
        self.session = requests.Session()
        # Enhanced headers to mimic a real browser more closely
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.kabum.com.br/',
        }
        self.session.headers.update(self.headers)

    def scrape_products(self):
        """Scrape products from Kabum"""
        print("Procurando por Samsung Galaxy A05s na Kabum...")
        
        # Try multiple search approaches
        search_terms = ['samsung galaxy a05s', 'samsung a05s', 'galaxy a05s', 'celular samsung a05s']
        
        products = []
        
        for term in search_terms:
            print(f"Tentando busca com: {term}")
            
            # Method 1: Using the standard search URL
            search_url = f"https://www.kabum.com.br/cgi-local/site/listagem/listagem.cgi?string={quote(term)}&btnG="
            
            try:
                # Random delay to avoid being blocked
                time.sleep(random.uniform(3, 6))
                
                response = self.session.get(search_url)
                
                # If the standard search doesn't work, try the API approach
                if response.status_code != 200 or "products" not in response.text.lower():
                    # Method 2: Direct search page
                    search_url = f"https://www.kabum.com.br/busca?s={quote(term)}"
                    response = self.session.get(search_url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to find product containers with multiple selector approaches
                    selectors = [
                        '[data-testid="product-card"]',
                        '.product-card',
                        '.card',
                        '[class*="product"]',
                        '.listagem-container .item',
                        'article',
                        '.item',
                        '[data-cy="product-card"]'
                    ]
                    
                    product_containers = []
                    for selector in selectors:
                        elements = soup.select(selector)
                        if elements:
                            product_containers = elements
                            print(f"Found {len(elements)} elements with selector: {selector}")
                            break
                    
                    # If still no containers, try a more general approach
                    if not product_containers:
                        product_containers = soup.find_all(['div', 'article'], attrs={'data-testid': True})
                    
                    # If still no containers, try to find anything that might be a product
                    if not product_containers:
                        product_containers = soup.find_all(['div', 'article'], class_=re.compile(r'product|card|item'))
                    
                    for container in product_containers:
                        product = self.extract_product_info(container)
                        if product:
                            products.append(product)
                    
                    # If we found products, break out of the loop
                    if products:
                        break
                else:
                    print(f"Failed to access page with status code: {response.status_code}")
            
            except requests.RequestException as e:
                print(f"Error accessing Kabum with term {term}: {e}")
                continue
            except Exception as e:
                print(f"Error processing Kabum page for term {term}: {e}")
                continue
        
        return products

    def extract_product_info(self, container):
        """Extract product info from Kabum"""
        try:
            # Extract title - try multiple approaches
            title = "Título não encontrado"
            
            # Try different selectors for the title
            title_selectors = [
                '[data-testid*="title"]',
                '[class*="name"]',
                '[class*="title"]',
                '.nameCard',
                '.productName',
                '.product-name',
                'h2',
                'h3',
                'a'
            ]
            
            for selector in title_selectors:
                title_element = container.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    if title and len(title) > 5:  # Ensure it's a reasonable title
                        break
            
            # If still not found, try to get text content
            if title == "Título não encontrado" or len(title) <= 5:
                for tag in container.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'div', 'span']):
                    text = tag.get_text(strip=True)
                    if len(text) > 10 and ('galaxy' in text.lower() or 'a05s' in text.lower()):
                        title = text
                        break
            
            # Extract price - try multiple approaches
            price = "Preço não encontrado"
            
            # Try different selectors for the price
            price_selectors = [
                '[data-testid*="price"]',
                '.priceCard',
                '[class*="price"]',
                '.money'
            ]
            
            for selector in price_selectors:
                price_element = container.select_one(selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
                    # Look for price format (R$ followed by numbers)
                    price_match = re.search(r'R\$[\s\d,.]+', price_text)
                    if price_match:
                        price = price_match.group()
                        break
            
            # If still not found, look for any price-like text
            if price == "Preço não encontrado":
                all_text = container.get_text()
                price_matches = re.findall(r'R\$[\s\d,.]+', all_text)
                if price_matches:
                    price = price_matches[0]
            
            # Extract link - try multiple approaches
            link = "Link não encontrado"
            
            # Look for link in the product container
            for a_tag in container.find_all('a', href=True):
                href = a_tag.get('href', '')
                if href and any(keyword in href.lower() for keyword in ['produto', '/p/', 'product']):
                    if href.startswith('http'):
                        link = href
                    elif href.startswith('/'):
                        link = 'https://www.kabum.com.br' + href
                    else:
                        link = 'https://www.kabum.com.br/' + href
                    break
            
            # If still no link, try to find any href attribute
            if link == "Link não encontrado":
                all_links = container.find_all('a', href=True)
                if all_links:
                    href = all_links[0].get('href', '')
                    if href.startswith('http'):
                        link = href
                    elif href.startswith('/'):
                        link = 'https://www.kabum.com.br' + href
                    else:
                        link = 'https://www.kabum.com.br/' + href
            
            # Check if this product matches our target (Samsung Galaxy A05s 128GB 6GB RAM) and is new
            title_lower = title.lower()
            if ('galaxy' in title_lower and 
                'a05s' in title_lower and 
                '128' in title_lower and 
                ('6gb' in title_lower or '6 gb' in title_lower) and
                'recondicionado' not in title_lower and
                'recond' not in title_lower and
                'usado' not in title_lower and
                'segunda m' not in title_lower):
                return {
                    'title': title,
                    'price': price,
                    'link': link,
                    'store': 'Kabum',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        
        except Exception as e:
            print(f"Error extracting Kabum product info: {e}")
            return None
        
        return None

    def print_results(self, products):
        """Print results in a formatted way"""
        # Limit to top 5 products
        top_5_products = products[:5] if len(products) > 5 else products
        
        if not top_5_products:
            print("Nenhum produto encontrado.")
            return
        
        print(f"\nEncontrados {len(products)} produtos. Exibindo os 5 primeiros:\n")
        print("-" * 100)
        
        for i, product in enumerate(top_5_products, 1):
            print(f"{i}. {product['title']}")
            print(f"   Preço: {product['price']}")
            print(f"   Loja: {product['store']}")
            print(f"   Link: {product['link']}")
            print(f"   Data/Hora: {product['timestamp']}")
            print("-" * 100)

    def save_results(self, products, filename='precos_kabum_galaxy_a05s.csv'):
        """Save results to a CSV file"""
        # Limit to top 5 products
        top_5_products = products[:5] if len(products) > 5 else products
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'price', 'link', 'store', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in top_5_products:
                writer.writerow(product)
        
        print(f"Resultados salvos em {filename}")


def main():
    scraper = KabumScraper()
    
    print("Iniciando monitoramento de preços do Samsung Galaxy A05s na Kabum...")
    print("Este processo pode levar alguns minutos.\n")
    
    products = scraper.scrape_products()
    
    scraper.print_results(products)
    
    if products:
        scraper.save_results(products)
        
        # Also save to JSON for additional format
        with open('precos_kabum_galaxy_a05s.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, ensure_ascii=False, indent=2)
        
        print("\nDados também salvos em precos_kabum_galaxy_a05s.json")
    else:
        print("\nNenhum produto correspondente encontrado na Kabum.")


if __name__ == "__main__":
    main()