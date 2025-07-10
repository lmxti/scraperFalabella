from sqlalchemy import Column, DateTime, Integer, String, Numeric, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    store = Column(String) # Tienda donde se encuentra el producto
    category = Column(String) # Categoria de producto
    brand = Column(String) # Marca de producto
    model = Column(String) # Modelo de producto(en bruto)
    image = Column(String) # Imagen de producto
    price_normal = Column(Numeric, nullable=True) # Precio normal de producto
    price_internet = Column(Numeric, nullable=True) # Precio internet de producto
    price_card = Column(Numeric, nullable=True) # Precio con tarjeta de producto
    price_offer = Column(Numeric, nullable=True) # Precio oferta de producto
    product_url = Column(String, unique=True) # Enlace de producto
    
class ProductClean(Base):
    __tablename__ = 'products_clean'
    id = Column(Integer, primary_key=True)
    store = Column(String)
    category = Column(String)
    brand = Column(String)
    model = Column(String)
    price = Column(Numeric)
    origin_url = Column(String)
    price_normal = Column(Numeric)
    price_offer = Column(Numeric)
    cleaned_at = Column(DateTime, default=datetime.utcnow)
    
class ProductAnalytics(Base):
    __tablename__ = 'products_analytics'
    
    # Metadata básica (conservada de las tablas anteriores)
    id = Column(Integer, primary_key=True)
    store = Column(String)  # Tienda (ej: "Falabella")
    brand = Column(String)  # Marca (ej: "Samsung")
    model = Column(String)  # Modelo normalizado (ej: "Galaxy S23")
    origin_url = Column(String)  # URL original
    
    # Información de precios
    best_price = Column(Numeric)  # El menor precio disponible (oferta/normal)
    price_normal = Column(Numeric)  # Precio sin descuento
    discount = Column(Float)  # Porcentaje de descuento (0 a 100)
    
    # Comparativas (lo nuevo importante)
    avg_price_by_model = Column(Numeric)  # Precio promedio para este modelo en todas las tiendas
    min_price_by_model = Column(Numeric)  # Precio mínimo encontrado para este modelo
    store_count_by_model = Column(Integer)  # En cuántas tiendas aparece este modelo
    
    # Temporalidad básica
    last_updated = Column(DateTime, default=datetime.utcnow)
    