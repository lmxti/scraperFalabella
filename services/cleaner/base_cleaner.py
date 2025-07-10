from abc import ABC, abstractmethod
from db.models import Product

# Clase base
class BaseCleaner(ABC):
    # Constructor de la clase
    def __init__(self, product: Product):
        self.product = product

    # Definicion de metodo abstracto, se debe definir por cada subclase
    @abstractmethod
    def clean(self):
        pass