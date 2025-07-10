
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from services.raw_saver import save_raw_data

from config.selenium_config import get_chrome_options, get_chrome_driver, ejecutar_scripts_anti_detec

from services.raw_saver import save_raw_data

def parse_price(price_str):
    if price_str is None:
        return None
    return float(price_str.replace('.', '').replace(',', '.'))


def scrape_product_details(driver, url):
    
    product_brand = "Desconocida"
    product_model = ""
    product_image = None
    product_price_normal = None
    product_price_internet = None
    product_price_card = None
    product_price_offer = None
    
    try:
        # Apertura de enlace en una nueva pestaña
        driver.execute_script("window.open(arguments[0]);", url)
        # Cambio de enfoque de pestaña a la nueva pestaña abierta (ultima)
        driver.switch_to.window(driver.window_handles[-1])
        
        # Tiempo de espera randomizado para simular comportamiento humano
        time.sleep(random.uniform(3, 6))
        # Tiempo de espera explícito para que los elementos estén presentes
        wait_detalle = WebDriverWait(driver, 10)
        # Espera de presencia de elemento que coincida con el selector CSS
        wait_detalle.until(EC.presence_of_element_located((By.ID, 'pdp-product-brand-link')))
        
        # Busqueda y extracion de nombre de marca de elemento(producto) por su selector ID.
        product_brand = driver.find_element(By.ID, 'pdp-product-brand-link').text
        # Busqueda y extracion de nombre de modelo de elemento(producto) por su selector CSS.
        product_model = driver.find_element(By.CSS_SELECTOR, 'h1.product-name').text
        # Busqueda y extracion de imagen de elemento(producto) por su selector CSS.
        image_element = driver.find_element(By.CSS_SELECTOR, 'img[id^="testId-pod-image"]')
        product_image = image_element.get_attribute('src')
        # Busqueda y extracion de precio normal de elemento(producto) por su selector CSS.
        try:
            product_price_normal = driver.find_element(By.CSS_SELECTOR, 'li[data-normal-price]').get_attribute("data-normal-price")
            product_price_normal = parse_price(product_price_normal)
        except:
            product_price_normal = None
        # Busqueda y extracion de precio internet de elemento(producto) por su selector CSS.
        try:
            product_price_internet = driver.find_element(By.CSS_SELECTOR, 'li[data-internet-price]').get_attribute("data-internet-price")
            product_price_internet = parse_price(product_price_internet)
        except:
            product_price_internet = None
        # Busqueda y extracion de precio tarjeta de elemento(producto) por su selector CSS.
        try:
            product_price_card = driver.find_element(By.CSS_SELECTOR, 'li[data-cmr-price]').get_attribute("data-cmr-price")
            product_price_card = parse_price(product_price_card)
        except:
            product_price_card = None
        # Busqueda y extracion de precio oferta de elemento(producto) por su selector CSS.
        try:
            product_price_offer = driver.find_element(By.CSS_SELECTOR, 'li[data-event-price]').get_attribute("data-event-price")
            product_price_offer = parse_price(product_price_offer)
        except:
            product_price_offer = None

        # Devuelve TODOS los valores siempre
        return product_brand, product_model, product_image, product_price_normal, product_price_internet, product_price_card, product_price_offer

    except Exception as e:
        print(f"Error al extraer detalle: {e}")
    finally:
        # Cierre de pestaña actual
        driver.close()
        # Cambio de enfoque de pestaña a la pestaña original (principal)
        driver.switch_to.window(driver.window_handles[0])
        
    return product_brand, product_model, product_image
        
def scrape_products(pages=1):
    # Configuración del driver del navegador
    options = get_chrome_options()
    service, options = get_chrome_driver(options)
    # Instancia del navegador
    driver = webdriver.Chrome(service=service, options=options)
    # Scripts anti-detección de automatización
    ejecutar_scripts_anti_detec(driver)
    
    # Lista de productos scrapeados
    scrape_products = []

    # Bucle para recorrer cantidad de paginas
    for page in range(1, pages + 1):
        url = f"https://www.falabella.com/falabella-cl/category/cat2018/Celulares-y-Telefonos?f.product.L2_category_paths=cat7090034%7C%7CTecnolog%C3%ADa%2Fcat16400010%7C%7CTelefon%C3%ADa%2Fcat2018%7C%7CCelulares+y+Tel%C3%A9fonos&page={page}"
        print(f"Scrapeando página {page}...")
        
        try:
            # Apertura de enlace en la instancia del navegador
            driver.get(url)
            # Tiempo de espera randomizado para simular comportamiento humano
            time.sleep(random.uniform(3, 7))
            
            # Desplazamiento aleatorio para simular scroll
            driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 500));")
            # Tiempo de espera adicional randomizado para simular comportamiento humano
            time.sleep(random.uniform(0.5, 1.5))

            # Tiempo de espera explícito para que los elementos estén presentes
            wait = WebDriverWait(driver, 15)
            # Espera de presencia de elemento que coincida con el selector CSS
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.pod-link')))
            # Busqueda de elementos que coincidan con el selector CSS
            elementos = driver.find_elements(By.CSS_SELECTOR, 'a.pod-link')

            product = []
            # Iteracion de elementos(que coincidan con el selector CSS) encontrados
            # for i, elemento in enumerate(elementos[:4], 1):
            for i, elemento in enumerate(elementos, 1):
                try:
                    if i % 5 == 0: time.sleep(random.uniform(0.2, 0.8))
                    # Busqueda y extracion de enlace url del elemento(producto) por su href.
                    product_url = elemento.get_attribute('href')
                    # Extracción de informacion detallada por cada elemento(producto) encontrado.
                    (
                        product_brand,
                        product_model,
                        product_image,
                        product_price_normal,
                        product_price_internet,
                        product_price_card,
                        product_price_offer
                        
                    ) = scrape_product_details(driver, product_url)

                    product_data = {
                        "store": "FALABELLA",
                        "category": "CELULARES",
                        "brand": product_brand,
                        "model": product_model,
                        "image": product_image,
                        "price_normal": product_price_normal,
                        "price_internet": product_price_internet,
                        "price_card": product_price_card,
                        "price_offer": product_price_offer,
                        "product_url": product_url
                    }
                    product.append(product_data)
                    # Informacion de progreso, elemento scrapeado.
                    print(f"[{i}/{len(elementos)}] {product_brand} - {product_model}")
                    # Incorporar elemento a la base de datos
                    save_raw_data(product_data)

                except Exception as e:
                    print(f"Error al procesar producto {i}: {e}")
                    # Intentar volver a la pestaña original si hay error
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # Informacion de cantidad de elementos(productos) encontrados en la pagina.
            print(f"Productos en página {page}: {len(product)}")
            # Tiempo de espera randomizado para simular comportamiento humano si no es la última página.
            if page < pages:
                time.sleep(random.uniform(2, 5))
        except Exception as e:
            print(f"Error en página {page}: {e}")
            continue
    else:
        print("❌ No se encontraron productos para guardar")
    driver.quit()