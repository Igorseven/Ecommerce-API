"""
Arquivo principal para executar a aplicação Flask
"""
from app import create_app
import os

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    # Obter configurações do ambiente
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'

    print("=" * 60)
    print("E-Commerce API - Iniciando servidor...")
    print("=" * 60)
    print(f" Ambiente: {os.getenv('FLASK_ENV', 'development')}")
    print(f" Host: {host}")
    print(f" Porta: {port}")
    print(f" Debug: {debug}")
    print("=" * 60)
    print("\n Endpoints disponíveis:")
    print("   • Raiz: http://localhost:5000/")
    print("   • Health: http://localhost:5000/health")
    print("   • Pedidos: http://localhost:5000/api/orders")
    print("   • CEP: http://localhost:5000/api/cep/<cep>")
    print("   • Produtos: http://localhost:5000/api/products")
    print("=" * 60)
    print("\n Servidor rodando! Pressione CTRL+C para parar.\n")

    # Iniciar servidor
    app.run(
        host=host,
        port=port,
        debug=debug
    )
