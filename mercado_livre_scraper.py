import requests
from bs4 import BeautifulSoup
import time
import csv
import json
from datetime import datetime
import random
import re

class MercadoLivreScraper:
    def __init__(self):
        self.session = requests.Session()
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)

    def search_products(self, query):
        """Search for products on Mercado Livre"""
        # Format the search URL
        search_url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
        
        try:
            # Random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(search_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            return response.text
        except requests.RequestException as e:
            print(f"Error accessing Mercado Livre: {e}")
            return None

    def parse_product_listings(self, html_content):
        """Parse the HTML content to extract product information"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find product containers - Mercado Livre typically uses specific classes for product listings
        product_containers = soup.find_all('li', class_=re.compile(r'ui-search-layout__item|search-item|results-item'))
        
        products = []
        
        for container in product_containers:
            product = self.extract_product_info(container)
            if product:
                products.append(product)
        
        # Alternative approach if the above doesn't work
        if not products:
            # Look for items with specific data attributes
            items = soup.find_all('div', attrs={'data-unit-shopping-card': True})
            for item in items:
                product = self.extract_product_info(item)
                if product:
                    products.append(product)
        
        # If still no products found, try another approach
        if not products:
            # Try to find by common price selectors
            price_elements = soup.find_all('span', class_=re.compile(r'price__currency-symbol|andes-money-amount__currency-symbol'))
            for price_element in price_elements[:5]:  # Limit to first 5 to avoid duplicates
                parent = price_element.find_parent()
                product = self.extract_product_from_price_element(parent)
                if product:
                    products.append(product)

        return products

    def extract_product_info(self, container):
        """Extract individual product information from a container"""
        try:
            # Extract title
            title_element = container.find('h2', class_=re.compile(r'title|main-title|item-title'))
            if not title_element:
                title_element = container.find('a', class_=re.compile(r'title|main-title|item-title'))
            if not title_element:
                title_element = container.find('span', class_=re.compile(r'title|main-title|item-title'))
            
            title = title_element.get_text(strip=True) if title_element else "Título não encontrado"
            
            # Extract price
            price_element = container.find('span', class_=re.compile(r'price__fraction|andes-money-amount__fraction'))
            if not price_element:
                price_element = container.find('div', class_=re.compile(r'price__fraction|andes-money-amount__fraction'))
            
            price = "Preço não encontrado"
            if price_element:
                price_text = price_element.get_text(strip=True)
                # Remove any non-numeric characters except decimal separator
                price_clean = re.sub(r'[^\d,\.]', '', price_text)
                if price_clean:
                    price = f"R$ {price_clean}"
            
            # Extract link
            link_element = container.find('a', class_=re.compile(r'title|main-title|item-title'))
            if not link_element:
                link_element = container.find('a', href=True)
            
            link = link_element['href'] if link_element else "Link não encontrado"
            if link and not link.startswith('http'):
                link = 'https://www.mercadolivre.com.br' + link
            
            # Check if this product matches our target (Samsung Galaxy A05s 128GB 6GB RAM) and is new
            if ('galaxy' in title.lower() and 
                'a05s' in title.lower() and 
                '128' in title.lower() and 
                ('6gb' in title.lower() or '6 gb' in title.lower()) and
                'recondicionado' not in title.lower() and
                'recond' not in title.lower() and
                'usado' not in title.lower() and
                'segunda mão' not in title.lower() and
                'desbloqueado' not in title.lower()):
                return {
                    'title': title,
                    'price': price,
                    'link': link,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        
        except Exception as e:
            print(f"Error extracting product info: {e}")
            return None
        
        return None

    def extract_product_from_price_element(self, element):
        """Alternative method to extract product info from price element"""
        try:
            # Look for product title near the price element
            title_element = element.find_previous('h2') or element.find_previous('a')
            title = title_element.get_text(strip=True) if title_element else "Título não encontrado"
            
            # Extract price
            price_element = element.find('span', class_=re.compile(r'price__fraction|andes-money-amount__fraction'))
            if not price_element:
                price_element = element.find('div', class_=re.compile(r'price__fraction|andes-money-amount__fraction'))
            
            price = "Preço não encontrado"
            if price_element:
                price_text = price_element.get_text(strip=True)
                price_clean = re.sub(r'[^\d,\.]', '', price_text)
                if price_clean:
                    price = f"R$ {price_clean}"
            
            # Extract link
            link_element = element.find_parent('a') or element.find('a', href=True)
            link = link_element['href'] if link_element else "Link não encontrado"
            if link and not link.startswith('http'):
                link = 'https://www.mercadolivre.com.br' + link
            
            # Check if this product matches our target (Samsung Galaxy A05s 128GB 6GB RAM) and is new
            if ('galaxy' in title.lower() and 
                'a05s' in title.lower() and 
                '128' in title.lower() and 
                ('6gb' in title.lower() or '6 gb' in title.lower()) and
                'recondicionado' not in title.lower() and
                'recond' not in title.lower() and
                'usado' not in title.lower() and
                'segunda mão' not in title.lower() and
                'desbloqueado' not in title.lower()):
                return {
                    'title': title,
                    'price': price,
                    'link': link,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        
        except Exception as e:
            print(f"Error in alternative extraction: {e}")
            return None
        
        return None

    def search_galaxy_a05s(self):
        """Specific search for Samsung Galaxy A05s"""
        print("Procurando por Samsung Galaxy A05s...")
        
        # Try different query formats
        queries = [
            "samsung galaxy a05s",
            "galaxy a05s",
            "samsung a05s",
            "celular samsung galaxy a05s"
        ]
        
        all_products = []
        
        for query in queries:
            print(f"Tentando busca com: {query}")
            html_content = self.search_products(query)
            
            if html_content:
                products = self.parse_product_listings(html_content)
                all_products.extend(products)
                
                if products:
                    break  # If we found products, stop searching
        
        # Remove duplicates
        seen_links = set()
        unique_products = []
        for product in all_products:
            if product['link'] not in seen_links:
                seen_links.add(product['link'])
                unique_products.append(product)
        
        return unique_products

    def save_results(self, products, filename='precos_galaxy_a05s.csv'):
        """Save results to a CSV file"""
        # Limit to top 5 products
        top_5_products = products[:5] if len(products) > 5 else products
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'price', 'link', 'timestamp']
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
        print("-" * 80)
        
        for i, product in enumerate(top_5_products, 1):
            print(f"{i}. {product['title']}")
            print(f"   Preço: {product['price']}")
            print(f"   Link: {product['link']}")
            print(f"   Data/Hora: {product['timestamp']}")
            print("-" * 80)


def main():
    scraper = MercadoLivreScraper()
    
    print("Iniciando monitoramento de preços do Samsung Galaxy A05s...")
    print("Este processo pode levar alguns minutos.\n")
    
    products = scraper.search_galaxy_a05s()
    
    scraper.print_results(products)
    
    if products:
        scraper.save_results(products)
        
        # Also save to JSON for additional format
        with open('precos_galaxy_a05s.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, ensure_ascii=False, indent=2)
        
        print("\nDados também salvos em precos_galaxy_a05s.json")
    else:
        print("\nNenhum produto correspondente encontrado.")


if __name__ == "__main__":
    main()