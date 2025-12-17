"""
Configuração do banco de dados e SQLAlchemy
"""
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

# Instância do SQLAlchemy
db = SQLAlchemy()


def init_db(app):
    """
    Inicializa o banco de dados com a aplicação Flask

    Args:
        app: Instância do Flask
    """
    db.init_app(app)

    with app.app_context():

        # Criar todas as tabelas
        db.create_all()
        print("✓ Banco de dados inicializado com sucesso!")


def reset_db(app):
    """
    Remove e recria todas as tabelas (útil para desenvolvimento)

    Args:
        app: Instância do Flask
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✓ Banco de dados resetado com sucesso!")


# Funções auxiliares para timestamps
def get_current_timestamp():
    """Retorna o timestamp atual"""
    return datetime.now()
