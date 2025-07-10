import re
from typing import List, Optional
from utils.constants import COLOR_LIST, GENERIC_TERMS, CONNECTIVITIES #KNOWN_MODELS
from rapidfuzz import process, fuzz 
from utils.nlp_utils import load_spacy_model
from utils.nlp_utils import ModelLearner

nlp_model = load_spacy_model()

def get_brand_pattern(brand: str) -> re.Pattern:
    return re.compile(rf'\b{re.escape(brand.lower())}\b', re.IGNORECASE)

# Terminos genericos para referirse a celular
CELLPHONE_TERMS_PATTERN = re.compile(r'\b(celular|smartphone|móvil|movil|telefono|teléfono|teléfono inteligente|tablet)\b', re.IGNORECASE)
# Terminos genericos para referirse a la memoria ram
MEMORY_TERMS_PATTERN = re.compile(r'\b(ram|rom|memoria|memory)\b', re.IGNORECASE)
# Terminos genericos de conectividad(5g,4g,...)
CONNECTIVITY_PATTERN = re.compile( rf'\b(?:{"|".join(re.escape(conn) for conn in CONNECTIVITIES)})\b', re.IGNORECASE )
# Patron de colores
COLORS_PATTERN = re.compile(rf'(?:{"|".join(re.escape(color) for color in COLOR_LIST)})\b', re.IGNORECASE)
# Patron basico de almacenamiento
STORAGE_PATTERN = re.compile(r'\b(?:16|32|64|128|256|512|1024)[gbt]\w*\b|\b(?:1|1\.5|2)t\w*\b', re.IGNORECASE)
# Patron basico de memoria ram
RAM_PATTERN = re.compile(
    r'\b(?:3|4|6|8|12|16|24|32)\s*(?:g|gb)\s*(?:ram)?\b',
    re.IGNORECASE
)
# Patrón de palabras innecesarias
UNNECESSARY_WORDS_PATTERN = re.compile(rf'\b(?:{"|".join(re.escape(word) for word in GENERIC_TERMS if not word.startswith(r"\d"))})\b', re.IGNORECASE)
# Patron de capacidad de megapixeles de camara
CAMERA_MP_PATTERN = re.compile(r'\b\d+\s*mpx?\b', re.IGNORECASE)
# Patron grado proteccion
IP_RATING_PATTERN = re.compile(r'\bIP[0-9]{2}\b', re.IGNORECASE)

# Patrones genericos y reutilizables
PARENTHESES_PATTERN = re.compile(r'\([^)]*\)') # Contenido entre parentesis
BRACKETS_PATTERN = re.compile(r'\[[^\]]*\]') # Contenido entre corchetes
# Puntuacion y caracteres especiales (Editado, le borre el '+')
PUNCTUATION_PATTERN = re.compile(r'\s*[\-\/\.\,\;\:\(\)\[\]\'\"]\s*') 
WHITESPACE_PATTERN = re.compile(r'\s+') # Uno o mas espacios ( )

STORAGE_MEMORY_PATTERN = re.compile(
        r'(?:'
        # formatos estándar (ej. "128gb 8gb", "256gb+12gb")
        r'(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)?\b[\s\+/]*(?:4|6|8|12|16|32)\s*(?:gb|g|ram)\b'
        r'|'
        # formatos inversos (ej. "8gb 128gb", "ram 8gb+256gb")
        r'(?:4|6|8|12|16|32)\s*(?:gb|g|ram)\b[\s\+/]*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)?\b'
        r'|'
        # formatos pegados (ej. "8+128gb", "128gb8gb")
        r'(?<![a-zA-Z0-9])(?:4|6|8|12|16|32)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
        # r'(?:4|6|8|12|16|32)\s*\+\s*(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
        r'|'
        r'(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\s*(?:4|6|8|12|16|32)\s*(?:gb|g)\b'
        r'|'
        # Almacenamiento sin unidad + RAM (ej. "512 12GB RAM") ESTE
        r'(?:16|32|64|128|256|512|1024)\b\s*(?:4|6|8|12|16|32)\s*(?:gb|g|ram)\b'
        r'|'
         # formatos con "RAM" explícito (ej. "64GB 4GB RAM")
        r'(?:16|32|64|128|256|512|1024)\s*(?:gb|g)\s+(?:3|4|6|8|12|16|24|32)\s*(?:gb|g)\s+ram\b'
        r'|'
        # eliminar solo almacenamiento (ej."256gb")
        r'(?:16|32|64|128|256|512|1024)\s*(?:gb|g|tb|t)\b'
        r')',
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
    
    # Normalizar espacios y formato primero
    # Normalizar espacios alrededor de +/-
    text = re.sub(r'(\d)\s*([+-])\s*(\d)', r'\1 \2 \3', text) 
    text = re.sub(r'(\d)\s*(gb|g|ram|rom)\s*(\d)', r'\1\2 \3', text, flags=re.IGNORECASE)  # Separar valores pegados
    
    brand_pattern = get_brand_pattern(brand)
    # Quitar nombre de marca del texto
    text = brand_pattern.sub('', text) 
    # # Quitar palabras genericas de celular
    text = CELLPHONE_TERMS_PATTERN.sub('', text)
    # # Quitar palabras de memoria para facilitar patron de memoria y almacenamiento
    text = MEMORY_TERMS_PATTERN.sub('', text)
    # # Quitar valores de conectividad(5g,4g,3g,2g,lte)
    text = CONNECTIVITY_PATTERN.sub('', text)
    # # Quitar valores de almacenamiento y memoria complejos (combinaciones)
    text = STORAGE_MEMORY_PATTERN.sub('', text)
    # # Quitar patrones basicos de almacenamiento y/o memoria
    text = STORAGE_PATTERN.sub('', text)
    text = RAM_PATTERN.sub('', text)
    # # Quitar patrones de megapixeles
    text = CAMERA_MP_PATTERN.sub('', text)
    # # Quitar colores
    text = COLORS_PATTERN.sub('', text)
    # # Quitar palabras genericas
    text = UNNECESSARY_WORDS_PATTERN.sub('', text)
    # # Quitar grado de proteccion
    text = IP_RATING_PATTERN.sub('', text)
    # # 12. Eliminar puntos, simbolos extras
    text = PUNCTUATION_PATTERN.sub(' ', text)
    # # 13. Eliminar espacios en blanco extras
    text = WHITESPACE_PATTERN.sub(' ', text).strip()
    
    return text

# Versión mejorada de la función que usa patrones dinámicos
def remove_model_noise_with_patterns_v2(text: str, brand: str, learner: ModelLearner) -> str:
    """
    Versión mejorada que combina patrones dinámicos con limpieza estática.
    
    Args:
        text: Texto del modelo a limpiar
        brand: Marca del producto
        learner: Instancia de ModelLearner con patrones aprendidos
    
    Returns:
        Texto limpio del modelo
    """
    if not text or not brand:
        return ""
    
    # 1. Limpieza básica inicial
    cleaned_text = text.lower().strip()
    
    # 2. Obtener patrones dinámicos aprendidos
    learned_patterns = learner.get_model_patterns(brand)
    
    # 3. Si hay patrones aprendidos, intentar extraer tokens relevantes
    relevant_tokens = []
    if learned_patterns:
        # Crear patrón para buscar tokens aprendidos
        pattern_regex = re.compile(rf'\b(?:{"|".join(map(re.escape, learned_patterns))})\b', re.IGNORECASE)
        matches = pattern_regex.findall(cleaned_text)
        
        if matches:
            # Ordenar matches por longitud (más específicos primero)
            relevant_tokens = sorted(set(matches), key=len, reverse=True)
            
            # Si encontramos tokens relevantes, priorizarlos
            if relevant_tokens:
                # Verificar que los tokens encontrados sean realmente significativos
                significant_tokens = []
                for token in relevant_tokens:
                    # Filtrar tokens que sean solo números simples sin contexto
                    if len(token) > 1 or (token.isdigit() and len(token) >= 2):
                        significant_tokens.append(token)
                
                if significant_tokens:
                    return " ".join(significant_tokens[:3])  # Limitar a 3 tokens más relevantes
    
    # 4. Si no hay patrones útiles, aplicar limpieza estática
    cleaned_text = remove_model_noise_with_patterns(cleaned_text, brand)
    
    # 5. Post-procesamiento: eliminar tokens muy cortos o poco informativos
    tokens = cleaned_text.split()
    filtered_tokens = []
    
    for token in tokens:
        # Mantener tokens que:
        # - Tengan más de 1 carácter
        # - Sean alfanuméricos (contienen números Y letras)
        # - Sean números de 2+ dígitos
        # - Sean palabras significativas (no solo letras sueltas)
        if (len(token) > 1 and 
            (any(c.isdigit() for c in token) or 
             (token.isalpha() and len(token) > 2) or
             (token.isdigit() and len(token) >= 2))):
            filtered_tokens.append(token)
    
    # 6. Limitar resultado y mantener orden de relevancia
    result = " ".join(filtered_tokens[:4])  # Máximo 4 tokens
    
    return result.strip()


def nlp_remove_stopwords_and_noise(text: str) -> str:
    if not nlp_model or not text.strip():
            return text
    try:
        doc = nlp_model(text)
        filtered_tokens = []
        
        for token in doc:
            token_text = token.text.lower()
            if (token_text =='galaxy' or token_text == 'iphone'):
                filtered_tokens.append(token_text)
                continue
            # Excluir stopwords, puntuación)
            if ( token.is_stop  or token.is_punct):
                continue
            # Agregar a tokens filtrados
            filtered_tokens.append(token_text)
        return ' '.join(filtered_tokens[:5])  # Limita a 5 tokens
        

    except Exception as e:
        print(f"Error procesando texto en NLP: {e}")
        return text

def normalize_model_name(brand: str, model: str, learner: Optional[ModelLearner] = None) -> str:
    if not model or not brand: return model or ""
    
    # 1. Limpieza basica del modelo (parentesis, corchetes, espacios y minusculas)
    cleaned_text = basic_cleanup(model)
    
    
    # # En caso que exista un modelo de aprendizaje(learner), intenta encontrar una coincidencia exacta fuzzy
    # if learner:
    #     # Buscamos el mejor modelo conocido segundo 'marca' y 'modelo (limpio)'
    #     best_match = learner.find_best_match(brand, cleaned_text)
    #     if best_match:
    #         return best_match
            
    # # Limpieza con patrones (prioriza patrones aprendidos si existen)
    # if learner:
    #     cleaned_text = remove_model_noise_with_patterns_v2(cleaned_text, brand, learner)
    # # En caso que no existan patrones aprendidos, usa patrones estaticos
    # else:
    #     cleaned_text = remove_model_noise_with_patterns(cleaned_text, brand)
    
    cleaned_text = remove_model_noise_with_patterns(cleaned_text, brand)
    
    
    # 3. Elimina stopwords y ruido usando NLP
    cleaned_text = nlp_remove_stopwords_and_noise(cleaned_text)
    
    return cleaned_text.strip()