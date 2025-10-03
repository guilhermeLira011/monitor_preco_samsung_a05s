import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from datetime import datetime
import random
import re

class MagazineLuizaScraper:
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
        }
        self.session.headers.update(self.headers)

    def scrape_products(self):
        """Scrape products from Magazine Luiza"""
        print("Procurando por Samsung Galaxy A05s na Magazine Luiza...")
        
        # Try multiple search URLs to increase chances of finding products
        search_urls = [
            "https://www.magazineluiza.com.br/busca/samsung+galaxy+a05s/",
            "https://www.magazineluiza.com.br/busca/samsung+a05s/",
            "https://www.magazineluiza.com.br/busca/galaxy+a05s/",
        ]
        
        products = []
        
        for search_url in search_urls:
            try:
                print(f"Tentando busca com: {search_url}")
                
                # Random delay to avoid being blocked
                time.sleep(random.uniform(3, 6))
                
                response = self.session.get(search_url)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors based on our analysis of Magazine Luiza
                selectors = [
                    '[data-testid="product-card-container"]',
                    '[data-testid="product-card-content"]',
                    '[data-testid="product-card"]',
                    '[data-testid="product-list"] [class*="product"]',
                    'article[data-testid*="product"]',
                    'div[data-testid*="product"]',
                    'li[data-testid*="product"]',
                    'div[data-testid="mod-productlist"]',
                    'div[data-testid="product-list"]'
                ]
                
                product_containers = []
                for selector in selectors:
                    elements = soup.select(selector)
                    if elements:
                        product_containers = elements
                        break
                
                # If no containers found with selectors, try a more general approach
                if not product_containers:
                    product_containers = soup.find_all(['article', 'div', 'li'], attrs={'data-testid': lambda x: x and ('product' in x or 'card' in x)})
                
                for container in product_containers:
                    product = self.extract_product_info(container)
                    if product:
                        products.append(product)
                
                # If we found products, break out of the loop
                if products:
                    break
            
            except requests.RequestException as e:
                print(f"Error accessing Magazine Luiza with URL {search_url}: {e}")
                continue
            except Exception as e:
                print(f"Error processing Magazine Luiza page: {e}")
                continue
        
        return products

    def extract_product_info(self, container):
        """Extract product info from Magazine Luiza"""
        try:
            # Extract title - try multiple selectors
            title_selectors = [
                'h2',
                'h3', 
                'h4',
                'a',
                '[data-testid="title"]',
                '.product-title',
                '.productDescription'
            ]
            
            title = "Título não encontrado"
            for selector in title_selectors:
                title_element = container.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    break
            
            if title == "Título não encontrado":
                # Last resort: look for any text that might contain the product name
                all_text = container.get_text()
                lines = all_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if len(line) > 10:  # Reasonable length for a product title
                        title = line
                        break
            
            # Extract price - try multiple selectors
            price_selectors = [
                '[data-testid="price-value"]',
                '.price__sales',
                '.price__listing',
                '.sc-kpDqfm',
                'span',
                'p'
            ]
            
            price = "Preço não encontrado"
            for selector in price_selectors:
                price_elements = container.select(selector)
                for price_element in price_elements:
                    price_text = price_element.get_text(strip=True)
                    # Look for price format (R$ followed by numbers)
                    price_match = re.search(r'R\$[\s\d,.]+', price_text)
                    if price_match:
                        price = price_match.group()
                        break
                if price != "Preço não encontrado":
                    break
            
            # Extract link - try multiple ways to find the product link
            link = "Link não encontrado"
            
            # Look for the main link in the product card
            # First, try to find any link inside the container
            all_links = container.find_all('a', href=True)
            for a_tag in all_links:
                href = a_tag.get('href', '')
                if href:
                    # Check if this is likely a product link
                    if any(keyword in href.lower() for keyword in ['/produto/', '/p/', 'produto', '/pp/', '/product/']):
                        if href.startswith('http'):
                            link = href
                        else:
                            # Ensure it's a proper path
                            if not href.startswith('/'):
                                href = '/' + href
                            link = 'https://www.magazineluiza.com.br' + href
                        break
            
            # If still no link found, try finding the first link in the container
            if link == "Link não encontrado" and all_links:
                first_link = all_links[0]
                href = first_link.get('href', '')
                if href.startswith('http'):
                    link = href
                elif href.startswith('/'):
                    link = 'https://www.magazineluiza.com.br' + href
                else:
                    link = 'https://www.magazineluiza.com.br/' + href
            
            # Check if this product matches our target (Samsung Galaxy A05s 128GB 6GB RAM) and is new
            if ('galaxy' in title.lower() and 
                'a05s' in title.lower() and 
                '128' in title.lower() and 
                ('6gb' in title.lower() or '6 gb' in title.lower()) and
                'recondicionado' not in title.lower() and
                'recond' not in title.lower() and
                'usado' not in title.lower() and
                'segunda mão' not in title.lower()):
                return {
                    'title': title,
                    'price': price,
                    'link': link,
                    'store': 'Magazine Luiza',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        
        except Exception as e:
            print(f"Error extracting Magazine Luiza product info: {e}")
            return None
        
        return None

    def save_results(self, products, filename='precos_magazine_luiza_galaxy_a05s.csv'):
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


def main():
    scraper = MagazineLuizaScraper()
    
    print("Iniciando monitoramento de preços do Samsung Galaxy A05s na Magazine Luiza...")
    print("Este processo pode levar alguns minutos.\n")
    
    products = scraper.scrape_products()
    
    scraper.print_results(products)
    
    if products:
        scraper.save_results(products)
        
        # Also save to JSON for additional format
        with open('precos_magazine_luiza_galaxy_a05s.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, ensure_ascii=False, indent=2)
        
        print("\nDados também salvos em precos_magazine_luiza_galaxy_a05s.json")
    else:
        print("\nNenhum produto correspondente encontrado na Magazine Luiza.")


if __name__ == "__main__":
    main()