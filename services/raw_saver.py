from sqlalchemy.exc import IntegrityError
from db.models import Product
from db.init_db import SessionLocal

def save_raw_data(product_data: dict):
    db = SessionLocal()
    try:
        existing = db.query(Product).filter_by(product_url=product_data["product_url"]).first()
        if existing:
            # Actualizar producto existente
            for key, value in product_data.items():
                setattr(existing, key, value)
        else:
            new_product = Product(**product_data)
            db.add(new_product)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Error de integridad: {e}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error guardando producto: {e}")
    finally:
        db.close()