import subprocess
import sys
import os

def run_scraper(scraper_file, store_name):
    """Run a scraper file and return the results"""
    print(f"\nExecutando o scraper para {store_name}...")
    try:
        result = subprocess.run([sys.executable, scraper_file], 
                                capture_output=True, 
                                text=True, 
                                timeout=120)  # 2 minute timeout
        
        if result.returncode == 0:
            print(f"Scraper para {store_name} executado com sucesso!")
            print(result.stdout)
        else:
            print(f"Erro ao executar scraper para {store_name}:")
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print(f"O scraper para {store_name} excedeu o tempo limite de 2 minutos.")
    except Exception as e:
        print(f"Ocorreu um erro ao executar o scraper para {store_name}: {e}")

def main():
    print("Iniciando monitoramento de preços do Samsung Galaxy A05s em todas as lojas...")
    
    # Run Mercado Livre scraper
    run_scraper('mercado_livre_scraper.py', 'Mercado Livre')
    
    # Run Magazine Luiza scraper
    run_scraper('magazine_luiza_scraper.py', 'Magazine Luiza')
    
    # Run Kabum scraper
    run_scraper('kabum_scraper.py', 'Kabum')
    
    print("\nProcesso de monitoramento concluído!")
    print("Verifique os arquivos CSV e JSON gerados para cada loja.")

if __name__ == "__main__":
    main()