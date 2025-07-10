# selenium_config.py
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config.settings import BRAVE_PATH, CHROMEDRIVER_PATH

def get_chrome_options(stealth=False, disable_images=False):
    options = Options()
    options.binary_location = BRAVE_PATH

    # Argumentos comunes
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    if disable_images:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

    return options

def get_chrome_driver(options=None):
    service = Service(CHROMEDRIVER_PATH)
    return Service(CHROMEDRIVER_PATH), options or get_chrome_options()

def ejecutar_scripts_anti_detec(driver):
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']})")
