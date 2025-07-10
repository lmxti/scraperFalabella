
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

        
def scrape_productsOLD(pages=1):
    # Configuración del driver del navegador
    options = get_chrome_options()
    service, options = get_chrome_driver(options)
    # Instancia del navegador
    driver = webdriver.Chrome(service=service, options=options)
    # Scripts anti-detección de automatización
    ejecutar_scripts_anti_detec(driver)
    
    # Lista de productos scrapeados
    scrape_products = []
    brands = [
        "Apple", "Alcatel", "Asus",
        "Baofeng", "Blackview", "Blu", "Bmobile",
        "Cubot", "Claro",
        "Doogee", "Daewoo", "Dblue",
        "Electrolux",
        "Fossibot",
        "Generico",
        "Google",
        "Honor", "Huawei",
        "Infinix", "Introtech", "Irt",
        "Logic",
        "Motorola", "Maceratta", "Microlab", "Mlab", "Movistar",
        "Nothing", "Nubia", "Oneplus", "Oppo",
        "Oscal", "Oukitel", "Own",
        "Philco", "Punto store",
        "Realme", "Redmi",
        "Samsung", "Sony", "Soymomo",
        "Tcl", "Tecno mobile", "Tecnolab",
        "Ulefone", "Umidigi", "Uniden", "Unihertz",
        "Vivo",
        "Xiaomi", "Xtorm",
        "Zte"
    ]
    # -------------------------------------------------------------------------------------------------------------------------
    brands = ['apple', 'samsung','xiaomi', 'motorola', 'honor', 'vivo', 'huawei', 'redmi',]  # Puedes agregar todas las marcas que necesites
    condition = "nuevo"            # 'nuevo' o 'reacondicionado'
    min_price = None               # Ejemplo: 300000
    max_price = None               # Ejemplo: 500000
    storage = None                 # Ejemplo: '128 GB'
    # Base de la URL
    base_url = "https://www.falabella.com/falabella-cl/category/cat2018/Celulares-y-Telefonos"
    
    # Parámetros fijos
    base_params = {
        "facetSelected": "true",
        "f.product.L2_category_paths": "cat7090034||Tecnología/cat16400010||Telefonía/cat2018||Celulares+y+Teléfonos",
        "f.product.attribute.Condicion_del_producto": condition
    }
    # Agregar marcas (si hay)
    if brands:
        # Unir marcas con :: como hace Falabella
        base_params["f.product.brandName"] = "::".join(brands)
    
    # Agregar otros filtros
    if storage:
        base_params["f.product.attribute.Memoria_Interna"] = storage
    if min_price or max_price:
        price_range = f"{min_price if min_price else ''}-{max_price if max_price else ''}"
        base_params["f.product.attribute.Rango_de_Precios"] = price_range
    # -------------------------------------------------------------------------------------------------------------------------
    
    # Bucle para recorrer cantidad de paginas
    for page in range(1, pages + 1):
                # -------------------------------------------------------------------------------------------------------------------------
        # Agregar número de página
        params = base_params.copy()
        params["page"] = str(page)
        
        # Construir URL
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{base_url}?{query_string}"
        # -------------------------------------------------------------------------------------------------------------------------
        # url = f"https://www.falabella.com/falabella-cl/category/cat2018/Celulares-y-Telefonos?facetSelected=true&f.product.L2_category_paths=cat7090034%7C%7CTecnolog%C3%ADa%2Fcat16400010%7C%7CTelefon%C3%ADa%2Fcat2018%7C%7CCelulares+y+Tel%C3%A9fonos&f.product.attribute.Condicion_del_producto=nuevo&page={page}"
        # print(f"Scrapeando página {page}...")
        
        try:
            # Apertura de enlace en la instancia del navegador
            driver.get(url)
            # Tiempo de espera randomizado para simular comportamiento humano
            # time.sleep(random.uniform(3, 7))
            
            # Desplazamiento aleatorio para simular scroll
            # driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 500));")
            # Tiempo de espera adicional randomizado para simular comportamiento humano
            # time.sleep(random.uniform(0.5, 1.5))

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
                    if i % 5 == 0:
                        time.sleep(random.uniform(0.2, 0.8))
                    
                    product_url = elemento.get_attribute('href')

                    # Ahora sí: dentro del producto
                    product_brand = elemento.find_element(By.CSS_SELECTOR, '.pod-title').text
                    product_model = elemento.find_element(By.CSS_SELECTOR, '.pod-subTitle').text

                    # img = elemento.find_element(By.TAG_NAME, "img").get_attribute("src")

                    # Precios
                    try:
                        product_price_normal = elemento.find_element(By.CSS_SELECTOR, 'li[data-normal-price]').get_attribute("data-normal-price")
                        product_price_normal = parse_price(product_price_normal)
                    except:
                        product_price_normal = None

                    try:
                        product_price_internet = elemento.find_element(By.CSS_SELECTOR, 'li[data-internet-price]').get_attribute("data-internet-price")
                        product_price_internet = parse_price(product_price_internet)
                    except:
                        product_price_internet = None

                    try:
                        product_price_card = elemento.find_element(By.CSS_SELECTOR, 'li[data-cmr-price]').get_attribute("data-cmr-price")
                        product_price_card = parse_price(product_price_card)
                    except:
                        product_price_card = None

                    try:
                        product_price_offer = elemento.find_element(By.CSS_SELECTOR, 'li[data-event-price]').get_attribute("data-event-price")
                        product_price_offer = parse_price(product_price_offer)
                    except:
                        product_price_offer = None

                    product_data = {
                        "store": "FALABELLA",
                        "category": "CELULARES",
                        "brand": product_brand,
                        "model": product_model,
                        "image": "",
                        "price_normal": product_price_normal,
                        "price_internet": product_price_internet,
                        "price_card": product_price_card,
                        "price_offer": product_price_offer,
                        "product_url": product_url
                    }

                    product.append(product_data)
                    print(f"[{i}/{len(elementos)}] {product_brand} - {product_model}")
                    save_raw_data(product_data)

                except Exception as e:
                    print(f"Error al procesar producto {i}: {e}")
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