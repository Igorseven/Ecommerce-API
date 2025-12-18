"""
Configuração do banco de dados e SQLAlchemy
"""
from datetime import datetime
import time
import logging

from flask_sqlalchemy import SQLAlchemy

# Instância do SQLAlchemy
db = SQLAlchemy()

logger = logging.getLogger(__name__)


def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask

    Args:
        app: Instância do Flask
    """
    db.init_app(app)

    with app.app_context():
        # Importar os modelos para que o SQLAlchemy os reconheça
        from app.models import Order, Address, OrderItem

        # Tentar criar as tabelas com retry
        max_retries = 5
        retry_delay = 2  # segundos

        for attempt in range(max_retries):
            try:
                # Testar conexão
                db.engine.connect()

                # Criar todas as tabelas
                db.create_all()
                print("✓ Banco de dados inicializado com sucesso!")
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou ao conectar ao banco. Tentando novamente em {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Falha ao inicializar banco de dados após {max_retries} tentativas: {str(e)}")
                    raise


def reset_db(app):
    """
    Remove e recria todas as tabelas (útil para desenvolvimento)

    Args:
        app: Instância do Flask
    """
    with app.app_context():
        # Importar os modelos para que o SQLAlchemy os reconheça
        from app.models import Order, Address, OrderItem

        db.drop_all()
        db.create_all()
        print("✓ Banco de dados resetado com sucesso!")


# Funções auxiliares para timestamps
def get_current_timestamp():
    """Retorna o timestamp atual"""
    return datetime.now()
