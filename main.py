from scrapers.falabella_scraper import scrape_products
from scrapers.falabella_scraperOLD import scrape_productsOLD

from services.cleaner.service import clean_products
from db.init_db import init_db, truncate_products_clean, create_index_and_cluster
# from spacy.lang.es.stop_words import STOP_WORDS

def main():
    print("Inicializando base de datos...")
    init_db()  # Crear tablas si no existen
    
    
    # print("Iniciando scraping...")
    # scrape_productsOLD(pages=10)
    # print("Scraping completado.")

    truncate_products_clean()
    clean_products()
    create_index_and_cluster()
    

    # print(STOP_WORDS)
    
    
if __name__ == "__main__":  
    main()
