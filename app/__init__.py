"""
Inicialização da aplicação Flask
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import config_by_name
from app.database import init_db
import logging
import os


def create_app(config_name=None):
    """
    Factory function para criar a aplicação Flask

    Args:
        config_name: Nome da configuração (development, production, testing)

    Returns:
        Flask app: Instância configurada do Flask
    """
    # Criar instância do Flask
    app = Flask(__name__)

    # Configurar JSON para não escapar caracteres Unicode (acentos, etc)
    app.json.ensure_ascii = False

    # Determinar ambiente
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Carregar configurações
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Configurar logging
    setup_logging(app)

    # Configurar CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)

    # Inicializar banco de dados
    init_db(app)

    # Registrar blueprints (rotas)
    register_blueprints(app)

    # Registrar error handlers
    register_error_handlers(app)

    # Rota raiz de teste
    @app.route('/')
    def index():
        return jsonify({
            'message': 'E-Commerce API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'orders': '/api/orders',
                'cep': '/api/cep',
                'products': '/api/products',
                'health': '/health'
            }
        })

    # Rota de health check
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200

    logger = logging.getLogger(__name__)
    logger.info(f"Aplicação Flask iniciada no modo: {config_name}")

    return app


def register_blueprints(app):
    """
    Registra todos os blueprints (rotas) da aplicação

    Args:
        app: Instância do Flask
    """
    from app.routes.orders import orders_bp
    from app.routes.cep import cep_bp

    app.register_blueprint(orders_bp)
    app.register_blueprint(cep_bp)

    logger = logging.getLogger(__name__)
    logger.info("✓ Blueprints registrados com sucesso")


def register_error_handlers(app):
    """
    Registra handlers de erro personalizados

    Args:
        app: Instância do Flask
    """

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Recurso não encontrado',
            'status': 404
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Método HTTP não permitido',
            'status': 405
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Erro interno do servidor',
            'status': 500
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger = logging.getLogger(__name__)
        logger.error(f"Erro não tratado: {str(error)}")

        return jsonify({
            'error': 'Erro interno do servidor',
            'status': 500
        }), 500


def setup_logging(app):
    """
    Configura o sistema de logging

    Args:
        app: Instância do Flask
    """
    # Configurar nível de log
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO

    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configurar logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            # Adicionar file handler se necessário
            # logging.FileHandler('app.log')
        ]
    )

    # Reduzir verbosidade de libs externas
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
