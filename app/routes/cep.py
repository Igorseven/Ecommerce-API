"""
Rotas para validação de CEP
"""
from flask import Blueprint, jsonify, request
from app.services.viacep_service import ViaCEPService
from app.services.shipping_service import ShippingService
import logging

logger = logging.getLogger(__name__)

# Criar blueprint
cep_bp = Blueprint('cep', __name__, url_prefix='/api/cep')


@cep_bp.route('/<cep>', methods=['GET'])
def validate_cep(cep):
    """
    Valida e busca informações de um CEP

    Args:
        cep: CEP a ser validado (com ou sem formatação)

    Returns:
        JSON com dados do endereço ou erro
    """
    try:
        logger.info(f"Requisição para validar CEP: {cep}")

        # Validar e buscar dados do CEP
        result = ViaCEPService.validate_and_get_address(cep)

        if not result.get('valid'):
            return jsonify({
                'error': result.get('error', 'CEP inválido'),
                'valid': False
            }), 400

        # Calcular frete (opcional, enviado como query param)
        calculate_shipping = request.args.get('calculate_shipping', 'false').lower() == 'true'

        response_data = result.copy()

        if calculate_shipping and result.get('state'):
            shipping_info = ShippingService.calculate_shipping(result['state'])
            response_data['shipping'] = shipping_info
            response_data['estimated_delivery_days'] = ShippingService.get_shipping_estimate_days(result['state'])

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Erro ao validar CEP {cep}: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao processar CEP',
            'valid': False
        }), 500


@cep_bp.route('/shipping/<state>', methods=['GET'])
def get_shipping_rate(state):
    """
    Busca o valor do frete para um estado específico

    Args:
        state: Sigla do estado (UF)

    Query params:
        total_amount: Valor total do pedido (para calcular frete grátis)

    Returns:
        JSON com informações do frete
    """
    try:
        logger.info(f"Requisição para calcular frete para estado: {state}")

        # Obter valor total (opcional)
        total_amount = request.args.get('total_amount', 0, type=float)

        # Calcular frete
        shipping_info = ShippingService.calculate_shipping(state, total_amount)
        shipping_info['estimated_delivery_days'] = ShippingService.get_shipping_estimate_days(state)

        return jsonify(shipping_info), 200

    except Exception as e:
        logger.error(f"Erro ao calcular frete para {state}: {str(e)}")
        return jsonify({
            'error': 'Erro ao calcular frete'
        }), 500


@cep_bp.route('/shipping/rates', methods=['GET'])
def get_all_shipping_rates():
    """
    Retorna todas as taxas de frete configuradas

    Returns:
        JSON com tabela de fretes
    """
    try:
        rates = ShippingService.get_all_shipping_rates()
        return jsonify(rates), 200

    except Exception as e:
        logger.error(f"Erro ao buscar tabela de fretes: {str(e)}")
        return jsonify({
            'error': 'Erro ao buscar taxas de frete'
        }), 500
