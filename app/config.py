"""
Configurações da aplicação Flask
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Configuração base da aplicação"""

    # Configurações do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # Configurações do banco de dados
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root123@localhost:3306/ecommerce_db'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG  # Log SQL queries em desenvolvimento

    # Configurações de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # URLs das APIs externas
    VIACEP_API_URL = os.getenv('VIACEP_API_URL', 'https://viacep.com.br/ws')

    # Configurações de frete (valores em reais por região)
    SHIPPING_RATES = {
        'SP': 10.00,  # São Paulo
        'RJ': 15.00,  # Rio de Janeiro
        'MG': 15.00,  # Minas Gerais
        'ES': 20.00,  # Espírito Santo
        'default': 25.00  # Outros estados
    }

    # Paginação
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100


class DevelopmentConfig(Config):
    """Configurações para ambiente de desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configurações para ambiente de produção"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configurações para ambiente de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dicionário para facilitar a seleção da configuração
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
