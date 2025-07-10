from services.cleaner.base_cleaner import BaseCleaner
from utils.cleaning_utils import normalize_model_name  # La nueva función
from db.models import ProductClean

from utils.nlp_utils import ModelLearner

class CellphoneCleaner(BaseCleaner):
    # Metodo constructor que recibe un producto(crudo) y una instancia de ModelLearner(si no se proporciona, se crea una nueva)
    def __init__(self, product, learner: ModelLearner = None):
        super().__init__(product)
        self.learner = learner or ModelLearner()  # Usa una instancia existente o crea nueva
    
    # Metodo polimorfo especial para celulare que limpia el producto
    def clean(self):
        # Si no se proporciona marca o modelo, retorna None
        if not self.product.brand or not self.product.model:
            print(f"Datos incompletos: Brand={self.product.brand}, Model={self.product.model}")
            return None
    
        try:
            # Normalizacion del nombre del modelo pasando 'marca', 'modelo de producto' y 'learner'
            model = normalize_model_name(
                brand=self.product.brand,
                model=self.product.model,
                learner=self.learner
            )
        
            # print(f"[DEBUG] Modelo limpio: {model}")
            # self.learner.learn_from_clean_model(self.product.brand, model)
            
            return ProductClean(
                store=self.product.store,
                category='celulares',
                brand=self.product.brand,
                model=model,
                price_normal=self.product.price_normal,
                price_offer=self.product.price_offer,
                origin_url=self.product.product_url
            )
        except Exception as e:
            print(f"Error cleaning product -> clean(): {e}")
            return None