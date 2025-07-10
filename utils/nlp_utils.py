import spacy
from collections import defaultdict
import json
import os
from typing import Dict, Set, List
from rapidfuzz import process, fuzz

# Carga del modelo spaCy (manteniendo tu implementación actual)
def load_spacy_model(preferred="es_core_news_sm", fallback="es_core_news_sm"):
    try:
        return spacy.load(preferred)
    except OSError:
        try:
            return spacy.load(fallback)
        except OSError:
            raise RuntimeError(
                f"spaCy no disponible. Instala con:\n"
                f"pip install spacy && python -m spacy download {preferred}"
            )

# --------------------------------- CLASE DE APRENDIZAJE AUTOMATICO ---------------------------------
class ModelLearner:
    
    # ---------------Metodo constructor de la clase ModelLearner-------
    def __init__(self, data_file="model_patterns.json"):
        self.data_file = data_file
        self.model_patterns: Dict[str, List[str]] = defaultdict(list) # Guarda tokens relevantes(como numeros) por cada marca
        self.brand_models: Dict[str, Set[str]] = defaultdict(set) # Guarda modelos conocidos por cada marca
        self.load_data() # Carga los datos para ver si existen
        
    # ---------------Carga los datos de un JSON------------------------
    def load_data(self):
        # En caso que el archivo exista, abre y carga dos estructuras: patterns y brand_models
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.model_patterns = defaultdict(list, data.get('patterns', {}))
                    self.brand_models = defaultdict(set, 
                        {k: set(v) for k, v in data.get('brand_models', {}).items()})
            except Exception as e:
                print(f"Error cargando datos de aprendizaje -> load_data(): {e}")
                
    # ---------------Guarda los datos en un JSON------------------------
    def save_data(self):
        try:
            # Guarda model_patterns y brand_models como JSON
            data = { 'patterns': dict(self.model_patterns), 'brand_models': {k: list(v) for k, v in self.brand_models.items()}}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando datos de aprendizaje -> save_data(): {e}")

    # ---------------Aprende de un modelo limpio------------------------
    """ Recibe un modelo (limpio) y su marca y agrega el modelo a la lista conocida de esa marca."""
    def learn_from_clean_model(self, brand: str, model: str):
        
        if not brand or not model:return
        brand_lower = brand.lower()
        model_lower = model.lower()
        
        # Agregar el modelo completo a los conocidos
        self.brand_models[brand_lower].add(model_lower)
        
        # Extraer tokens numéricos significativos (para patterns de modelos)
        tokens = model_lower.split()
        # Iteracion sobre los tokens
        for token in tokens:
            # Nueva condición: longitud entre 2 y 6 caracteres
            # Mantenemos que debe contener números y Longitud controlada (Max 6)
            is_valid_token = (len(token) <= 6 )
            
            if (is_valid_token and token not in self.model_patterns[brand_lower]):
                self.model_patterns[brand_lower].append(token)
        # Guarda los datos actualizados
        self.save_data()
    
# ---------------FUNCION 1: Devuelve modelos conocidos para una marca ------------------------
    def get_known_models(self, brand: str) -> Set[str]:
        return self.brand_models.get(brand.lower(), set())
    
# ---------------FUNCION 2: Devuelve patrones conocidos para una marca ------------------------
    def get_model_patterns(self, brand: str) -> List[str]:
        return self.model_patterns.get(brand.lower(), [])
    
# ---------------FUNCION 3: Busca el mejor match entre modelos conocidos usando fuzzy matching-------
    def find_best_match(self, brand: str, text: str) -> str:
        known_models = self.get_known_models(brand)
        if not known_models or not text.strip():
            return ""

        try:
            text_lower = text.lower()
            
            # Caso 1: El text(modelo) ya se encuentra en el listado de modelos conocidos
            if text_lower in known_models: return text_lower

            # Caso 2: Si no se encuentra, intenta buscar la mejor coincidencia entre los listados conocidos
            result = process.extractOne( text_lower, known_models, scorer=fuzz.token_set_ratio, score_cutoff=85)
            
            if result:
                best_match, score, _ = result
                if best_match == text_lower:
                    return best_match if score > 85 else ""

            return ""

        except Exception as e:
            print(f"[ERROR] en find_best_match: {e}")
            return ""



nlp_model = load_spacy_model()