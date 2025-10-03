# Monitoramento de Preços - Samsung Galaxy A05s

Este projeto foi desenvolvido para monitorar preços do Samsung Galaxy A05s (128GB, 6GB RAM) novo nas principais lojas online do Brasil usando web scraping.

## Funcionalidades

- Busca automática por Samsung Galaxy A05s com 128GB de armazenamento e 6GB de RAM
- Filtragem específica para modelos 128GB/6GB RAM (excluindo modelos com 4GB RAM)
- Exclusão de produtos usados, recondicionados ou desbloqueados (apenas produtos novos)
- Monitoramento em múltiplas lojas:
  - Mercado Livre
  - Magazine Luiza
  - Kabum
- Extração de informações dos produtos (título, preço, link)
- Salvamento dos dados em formatos CSV e JSON
- Implementação de técnicas para evitar detecção de robôs

## Arquivos

- `mercado_livre_scraper.py` - Web scraper para o Mercado Livre
- `magazine_luiza_scraper.py` - Web scraper para a Magazine Luiza
- `kabum_scraper.py` - Web scraper para a Kabum
- `run_all_scrapers.py` - Script para executar todos os scrapers
- `requirements.txt` - Dependências do projeto
- `README.md` - Documentação do projeto
- `.gitignore` - Configuração de arquivos a serem ignorados pelo Git

## Como usar

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute os scrapers individualmente:
```bash
python mercado_livre_scraper.py                    # Apenas Mercado Livre
python magazine_luiza_scraper.py  # Apenas Magazine Luiza
python kabum_scraper.py          # Apenas Kabum
```

3. Ou execute todos de uma vez:
```bash
python run_all_scrapers.py
```

4. Os resultados serão exibidos no console e salvos nos arquivos CSV e JSON correspondentes

## Estrutura do código

Cada scraper contém:
- Métodos para fazer requisições HTTP com cabeçalhos realistas
- Funções para parsear o HTML e extrair informações relevantes
- Lógica para identificar e filtrar produtos Samsung Galaxy A05s com 128GB e 6GB RAM (novos)
- Métodos para salvar os dados em diferentes formatos

## Considerações

- O código inclui atrasos aleatórios para evitar ser bloqueado
- O scraping respeita os padrões de comportamento de um usuário real
- Filtro específico para garantir que apenas modelos 128GB/6GB RAM novos sejam incluídos
- O projeto pode ser estendido para monitorar outros produtos
- Os scrapers para Magazine Luiza e Kabum podem não encontrar todos os produtos devido à disponibilidade de estoque