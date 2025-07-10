from sqlalchemy import func, text
from datetime import datetime
import logging
from db.init_db import get_db, SessionLocal
from db.models import ProductClean, ProductAnalytics

# Configuracion de loggin
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def truncate_analytics_table():
    """Vacía la tabla products_analytics"""
    db = SessionLocal()
    try:
        db.query(ProductAnalytics).delete()
        db.commit()
        logger.info("Tabla products_analytics truncada")
    except Exception as e:
        db.rollback()
        logger.error(f"Error truncando tabla analytics: {str(e)}")
        raise
    finally:
        db.close()
        
def calculate_model_stats(db):
    """Calcula estadísticas agregadas por modelo"""
    return db.query(
        ProductClean.model,
        func.avg(ProductClean.price).label('avg_price'),
        func.min(ProductClean.price).label('min_price'),
        func.count(ProductClean.store.distinct()).label('store_count')
    ).group_by(ProductClean.model).all()
    

def transform_to_analytics():
    """Transforma datos de products_clean a products_analytics"""
    db = SessionLocal()
    try:
        start_time = datetime.now()
        logger.info("Iniciando transformación silver → gold")
        
        # 1. Vaciar tabla (opcional, podrías hacer incremental)
        truncate_analytics_table()
        
        # 2. Calcular estadísticas por modelo
        model_stats = calculate_model_stats(db)
        stats_dict = {model: {'avg': avg, 'min': min_p, 'count': cnt} 
                     for model, avg, min_p, cnt in model_stats}
        
        # 3. Procesar cada producto
        clean_products = db.query(ProductClean).all()
        
        for product in clean_products:
            stats = stats_dict.get(product.model, {})
            
            # Determinar mejor precio disponible
            prices = [p for p in [product.price_offer, product.price_normal] if p is not None]
            best_price = min(prices) if prices else None
            
            # Calcular descuento si aplica
            discount = 0
            if product.price_normal and product.price_offer:
                discount = ((product.price_normal - product.price_offer) / product.price_normal) * 100
            
            # Crear registro analytics
            analytics_record = ProductAnalytics(
                store=product.store,
                brand=product.brand,
                model=product.model,
                origin_url=product.origin_url,
                best_price=best_price,
                price_normal=product.price_normal,
                discount=discount,
                avg_price_by_model=stats.get('avg', 0),
                min_price_by_model=stats.get('min', 0),
                store_count_by_model=stats.get('count', 0),
                last_updated=datetime.utcnow()
            )
            
            db.add(analytics_record)
        
        db.commit()
        logger.info(f"Transformación completada. Procesados {len(clean_products)} productos en {datetime.now() - start_time}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error durante la transformación: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    transform_to_analytics()