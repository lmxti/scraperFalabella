from services.cleaner.base_cleaner import BaseCleaner
from db.models import ProductClean

class GeneralCleaner(BaseCleaner):
    def clean(self):
        if not self.product.brand or not self.product.model:
            return None

        return ProductClean(
            brand=self.product.brand,
            model=self.product.model,
            category=self.product.category or 'desconocido',
            price_normal=self.product.price_normal,
            price_offer=self.product.price_offer,
            product_url=self.product.product_url,
            source='falabella'
        )