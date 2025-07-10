### Archivo: services/clean_service.py

from db.init_db import SessionLocal
from db.models import Product
from services.cleaner.base_cleaner import BaseCleaner
from services.cleaner.cellphone_cleaner import CellphoneCleaner
from services.cleaner.tv_cleaner import TVCleaner
from services.cleaner.general_cleaner import GeneralCleaner
from sqlalchemy.exc import IntegrityError

# Diccionario para mapear categoria
CLEANERS = { 'celulares': CellphoneCleaner, 'televisores': TVCleaner }

from utils.nlp_utils import ModelLearner

def clean_products():
    db = SessionLocal()
    learner = ModelLearner()  # Instancia única para toda la ejecución
    
    try:
        raw_products = db.query(Product).all()
        for raw in raw_products:
            cleaner_class = CLEANERS.get(raw.category.lower(), GeneralCleaner)
            cleaner = cleaner_class(raw, learner) 
            cleaned = cleaner.clean()
            if cleaned:
                db.add(cleaned)
        
        db.commit()
        learner.save_data() 
        print("✔ Datos normalizados y patrones actualizados.")
    
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()