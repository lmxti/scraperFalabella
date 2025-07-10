# analytics/visualization.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from db.init_db import SessionLocal
from db.models import ProductAnalytics
from typing import Optional

# Configuración de estilos
plt.style.use('ggplot')
sns.set_palette("pastel")

def get_model_data(model_name: str) -> pd.DataFrame:
    """Obtiene datos específicos de un modelo"""
    db = SessionLocal()
    try:
        query = db.query(ProductAnalytics).filter(ProductAnalytics.model.ilike(f"%{model_name}%"))
        return pd.read_sql(query.statement, db.bind)
    finally:
        db.close()

def plot_model_stats(model_name: str, save_path: Optional[str] = None):
    """Genera gráficos para un modelo específico"""
    df = get_model_data(model_name)
    
    if df.empty:
        print(f"No se encontraron datos para el modelo: {model_name}")
        return
    
    # Configuración de figura
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f"Análisis de precios para: {model_name}", fontsize=16)
    
    ## Gráfico 1: Distribución de precios por tienda
    sns.boxplot(data=df, x='store', y='best_price', ax=axes[0, 0])
    axes[0, 0].set_title("Distribución de precios por tienda")
    axes[0, 0].set_ylabel("Precio ($)")
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    ## Gráfico 2: Comparación precio normal vs mejor precio
    sns.barplot(data=df.melt(id_vars=['store'], value_vars=['price_normal', 'best_price']), 
                x='store', y='value', hue='variable', ax=axes[0, 1])
    axes[0, 1].set_title("Comparación: Precio normal vs Mejor precio")
    axes[0, 1].set_ylabel("Precio ($)")
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    ## Gráfico 3: Descuentos ofrecidos por tienda
    discount_df = df[df['discount'] > 0]  # Solo tiendas con descuento
    if not discount_df.empty:
        sns.barplot(data=discount_df, x='store', y='discount', ax=axes[1, 0])
        axes[1, 0].set_title("Porcentaje de descuento por tienda")
        axes[1, 0].set_ylabel("Descuento (%)")
        axes[1, 0].tick_params(axis='x', rotation=45)
    else:
        axes[1, 0].text(0.5, 0.5, "No hay descuentos disponibles", 
                        ha='center', va='center')
        axes[1, 0].set_title("Descuentos por tienda")
    
    ## Gráfico 4: Relación precio vs disponibilidad
    sns.scatterplot(data=df, x='store_count_by_model', y='best_price', 
                    hue='store', size='discount', sizes=(20, 200), ax=axes[1, 1])
    axes[1, 1].set_title("Relación: Precio vs Disponibilidad")
    axes[1, 1].set_xlabel("Número de tiendas que ofrecen el modelo")
    axes[1, 1].set_ylabel("Mejor precio ($)")
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

def plot_general_stats(save_path: Optional[str] = None):
    """Gráficos generales de todos los modelos"""
    db = SessionLocal()
    try:
        df = pd.read_sql("SELECT * FROM products_analytics", db.bind)
        
        # Top 10 modelos más populares
        top_models = df['model'].value_counts().head(10)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(x=top_models.index, y=top_models.values)
        plt.title("Top 10 modelos más ofrecidos")
        plt.ylabel("Número de ofertas")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(f"{save_path}_top_models.png", dpi=300, bbox_inches='tight')
        else:
            plt.show()
            
    finally:
        db.close()