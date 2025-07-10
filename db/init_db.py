from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from db.models import Base, ProductClean

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)
    
# Vaciar la tabla products_clean
def truncate_products_clean():
    db = SessionLocal()
    try:
        db.query(ProductClean).delete()
        db.commit()
    finally:
        db.close()
        
from sqlalchemy import text
        
def create_index_and_cluster():
    with engine.connect() as connection:
        # Crear índice solo si no existe
        connection.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'idx_marca_modelo' AND n.nspname = 'public'
            ) THEN
                CREATE INDEX idx_marca_modelo ON products_clean (brand, model);
            END IF;
        END$$;
        """))
        # Clusterizar la tabla con el índice creado
        connection.execute(text("CLUSTER products_clean USING idx_marca_modelo;"))
        connection.commit()

# Generador de sesión para usar con context manager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
