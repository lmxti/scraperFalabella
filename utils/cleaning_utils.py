import re
from typing import List, Optional
from utils.constants import COLOR_LIST, GENERIC_TERMS, CONNECTIVITIES, ACCESSORY_KEYWORDS
from rapidfuzz import process, fuzz 
from utils.nlp_utils import load_spacy_model
from utils.nlp_utils import ModelLearner

nlp_model = load_spacy_model()

def get_brand_pattern(brand: str) -> re.Pattern:
    return re.compile(rf'\b{re.escape(brand.lower())}\b', re.IGNORECASE)

# Terminos genericos para referirse a la memoria ram
MEMORY_TERMS_PATTERN = re.compile(r'\b(ram|rom|memoria|memory)\b', re.IGNORECASE)
# Terminos genericos de conectividad(5g,4g,...)
CONNECTIVITY_PATTERN = re.compile( rf'\b(?:{"|".join(re.escape(conn) for conn in CONNECTIVITIES)})\b', re.IGNORECASE )
# Patron de colores
COLORS_PATTERN = re.compile(rf'(?:{"|".join(re.escape(color) for color in COLOR_LIST)})\b', re.IGNORECASE)
# Patron basico de almacenamiento
STORAGE_PATTERN = re.compile(r'\b(?:16|32|64|128|256|512|1024)[gbt]\w*\b|\b(?:1|1\.5|2)t\w*\b', re.IGNORECASE)
# Patron basico de memoria ram
RAM_PATTERN = re.compile(r'\b(?:3|4|6|8|12|16|24|32)\s*(?:g|gb)\s*(?:ram)?\b', re.IGNORECASE)
# Patrón de palabras innecesarias
GENERIC_WORDS_PATTERN = re.compile(rf'\b(?:{"|".join(re.escape(word) for word in GENERIC_TERMS if not word.startswith(r"\d"))})\b', re.IGNORECASE)
# Patron de capacidad de megapixeles de camara
CAMERA_MP_PATTERN = re.compile(r'\b\d+\s*mpx?\b', re.IGNORECASE)
# Patron grado proteccion
IP_RATING_PATTERN = re.compile(r'\bIP[0-9]{2}\b', re.IGNORECASE)
# Patron de tamaño de pantalla
# SCREEN_SIZE_PATTERN = re.compile(r'\b[6-7][\.,][5-7]\s*["”]\b', re.IGNORECASE)
SCREEN_SIZE_PATTERN = re.compile(
    r'\b[4-9](?:[\.,]\d{1,2})?\s*(?:["”]|pulgadas?)'
    r'|'
    r'\b(?:65|66|67)\s*(?:["”])\b',
    re.IGNORECASE
)



# Patrones genericos y reutilizables
PARENTHESES_PATTERN = re.compile(r'\([^)]*\)') # Contenido entre parentesis
BRACKETS_PATTERN = re.compile(r'\[[^\]]*\]') # Contenido entre corchetes
# Puntuacion y caracteres especiales (Editado, le borre el '+')
PUNCTUATION_PATTERN = re.compile(r'\s*[\-\/\.\,\;\:\(\)\[\]\'\"\“\”\–]\s*')

WHITESPACE_PATTERN = re.compile(r'\s+') # Uno o mas espacios ( )

STORAGE_MEMORY_PATTERN = re.compile(
    r'(?:'
    # 1. Formatos explícitos ROM/RAM - Ej: "64GB ROM 8GB RAM", "8GB RAM 64GB ROM" 
    r'(?:16|32|64|128|256|512|1024)\s*(?:g|gb|tb)\s+rom\s+(?:2|3|4|6|8|12|16|24|32)\s*(?:g|gb|tb)\s+(ram|memoria)\b'
    r'|'
    r'(?:2|3|4|6|8|12|16|24|32)\s*(?:g|gb|tb)\s+(ram|memoria)\s+(?:16|32|64|128|256|512|1024)\s*(?:g|gb|tb)\s+rom'
    r'|'
    # 2. Formatos con "y" - Ej: "8GB RAM y 128GB ROM"
    r'(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s+(?:ram|memoria)\s+y\s+(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb)\s+(?:rom|almacenamiento)\b'
    r'|'
    # Formato RAM + almacenamiento - Ej: "RAM 8GB + 256GB"
    r'(?:ram|memoria)\s+(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
    r'|'
    # Formato RAM + almacenamiento - Ej: "4GB RAM + 128GB ROM"
    r'(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s*(?:ram|memoria)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\s*rom\b'
    r'|'
    # 3. Formato almacenamiento + memroia con unidades en ambos lados - Ej: "128GB + 8GB", "64GB + 1TB"
    r'(?<![a-zA-Z0-9])(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\s*\+\s*(?:1|16|32|64|128|256|512|1024)\s*(?:gb|g|t|tb)\b'
    r'|'
    # Formato X/Y con RAM especificada - Ej: "512/12GB RAM" 
    r'(?<![a-zA-Z0-9])(?:16|32|64|128|256|512|1024)\s*/\s*(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s*(?:ram|memoria)\b'
    r'|'
    # Formato Y/X con RAM opcional - Ej: "4/128GB RAM"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*/\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\s*(?:ram|memoria)?\b'
    r'|'
    # 4. Formatos X+Y o X/Y con unidades mixtas - Ej: "256GB + 8GB RAM", "128GB/8GB"
    r'(?:(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)?\s*[\+/]\s*(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g|ram|memoria))'
    r'|'
    # Formato Y+X con RAM opcional - Ej: "8GB + 256GB"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|t|tb)\s*(?:ram|memoria)?\b'
    r'|'
    # Formato Y+X o Y/X con unidades - Ej: "8GB + 128GB", "4GB/64GB"
    r'(?<![a-zA-Z0-9])(?:(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g|ram|memoria)?\s*[\+/]\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t))'
    r'|'
    # 5. Formatos Y+X con unidad al final - Ej: "8+256GB", "4+128TB"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*\+\s*(?:1|16|32|64|128|256|512|1024)\s*(?:gb|g|t|tb)\b'
    r'|'
    # Formato Y+X con RAM especificada - Ej: "8+256GB RAM"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*\+\s*(?:1|16|32|64|128|256|512|1024)\s*(?:gb|g|t|tb)(ram|memoria)?\b'
    r'|'
    # Formato YGB RAM + XGB - Ej: "12GB RAM + 256GB"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s*(?:ram|memoria)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
    r'|'
    # 6. Formatos sin conectores con unidades - Ej: "128GB 8GB RAM", "256GB 4GB"
    r'(?<![a-zA-Z0-9])(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)?\s*(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g|ram)\s*(?:ram|memoria)?\b'
    r'|'
    # Formato YGB XGB - Ej: "8GB 256GB" o 8GB 256B"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*(?:gb|g)\s+(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t|b)\b'
    r'|'
    # Formato Y XGB - Ej: "8 256GB" o 8 256B"
    # r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t|b)\b'
    # r'|'
    # 7. Almacenamiento TB básico - Ej: "1TB", "2TB"
    r'\b(?:1|1\.5|2)\s*tb?\b'
    r'|'
    # 8. Almacenamiento básico - Ej: "128GB", "256GB", "1TB"
    r'(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
    r'|'
    # 9. Formato Y+X sin unidades - Ej: "8+128", "4+64"
    r'(?<![a-zA-Z0-9])(?:2|3|4|6|8|12|16|24|32)\s*\+\s*(?:16|32|64|128|256|512|1024)\b'
    r'|'
    # 10. Memoria básica - Ej: "8GB RAM", "4GB", "12GB"
    r'(?:2|3|4|6|8|12|16|24|25|32)\s*(?:gb|g)\s*(?:ram|memoria)?\b'
    r')',
    re.IGNORECASE
)

BATTERY_PATTERN = re.compile(
    r'\b\d{1,4}(?:[.,]\d{3})?\s*(?:m?a?h|mah|milliampere-hour|milliamperio-hora)\b',
    re.IGNORECASE
)

def basic_cleanup(text: str) -> str:
    if not text: return ""
    text = text.lower().strip()
    text = PARENTHESES_PATTERN.sub('', text)
    text = BRACKETS_PATTERN.sub('', text)
    return text

def remove_model_noise_with_patterns(text: str, brand: str) -> str:
    if not text: return ""
        
    brand_pattern = get_brand_pattern(brand)
    # Quitar nombre de marca del texto
    text = brand_pattern.sub('', text) 
    text = text.replace('“', '"').replace('”', '"')
    # Quitar valores de conectividad(5g,4g,3g,2g,lte)
    text = CONNECTIVITY_PATTERN.sub('', text)
    #Quitar valores de almacenamiento y memoria complejos (combinaciones y basicos)
    text = STORAGE_MEMORY_PATTERN.sub('', text)
    # Quitar patrones de megapixeles
    text = CAMERA_MP_PATTERN.sub('', text)
    # Quitar colores
    text = COLORS_PATTERN.sub('', text)
    # Quitar palabras genericas
    text = GENERIC_WORDS_PATTERN.sub('', text)
    # Quitar grado de proteccion
    text = IP_RATING_PATTERN.sub('', text)
    # Quitar tamaño de pantalla
    text = SCREEN_SIZE_PATTERN.sub('', text)
    # Quitar capacidad de bateria
    text = BATTERY_PATTERN.sub('', text)
    
    # # 12. Eliminar puntos, simbolos extras
    text = PUNCTUATION_PATTERN.sub(' ', text)
    # # 13. Eliminar espacios en blanco extras
    text = WHITESPACE_PATTERN.sub(' ', text).strip()
    
    return text

def remove_duplicate_tokens(text: str) -> str:
    tokens = text.split()
    seen = set()
    unique_tokens = []
    for token in tokens:
        if token not in seen:
            seen.add(token)
            unique_tokens.append(token)
    return " ".join(unique_tokens)


def normalize_model_name(brand: str, model: str, learner: Optional[ModelLearner] = None) -> str:
    if not model or not brand: return model or ""
    
    # 1. Limpieza básica inicial
    cleaned_text = basic_cleanup(model)
    # 2. Limpieza más agresiva solo si no encontramos match
    cleaned_text = remove_model_noise_with_patterns(cleaned_text, brand)
    final_cleaned = remove_duplicate_tokens(cleaned_text)
        
    if learner:
        best_match = learner.find_best_match(brand, final_cleaned)
        
        if best_match:
            print(f'ENTRADA: {final_cleaned} - SALIDA: {best_match}')    
            return best_match

        # Aprender si no se encontró nada
        learner.learn_from_clean_model(brand, final_cleaned)

    return final_cleaned.strip()
    