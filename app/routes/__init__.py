"""
Rotas da API
"""
from app.routes.cep import cep_bp
from app.routes.orders import orders_bp

__all__ = ['cep_bp', 'orders_bp']
