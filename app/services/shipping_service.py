"""
Serviço de cálculo de frete
"""
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class ShippingService:
    """Serviço para calcular o valor do frete baseado no CEP"""

    @staticmethod
    def calculate_shipping(state, total_amount=0):
        """
        Calcula o valor do frete baseado no estado de destino

        Args:
            state: Sigla do estado (UF)
            total_amount: Valor total dos produtos (para possíveis descontos)

        Returns:
            dict: Informações do frete
        """
        try:
            # Obter tabela de valores de frete da configuração
            shipping_rates = current_app.config.get('SHIPPING_RATES', {
                'SP': 10.00,
                'RJ': 15.00,
                'MG': 15.00,
                'ES': 20.00,
                'default': 25.00
            })

            # Normalizar estado para uppercase
            state = state.upper() if state else ''

            # Buscar valor do frete para o estado
            shipping_cost = shipping_rates.get(state, shipping_rates.get('default', 25.00))

            # Regra: Frete grátis para compras acima de R$ 200,00
            free_shipping_threshold = 200.00
            if total_amount >= free_shipping_threshold:
                logger.info(f"Frete grátis aplicado para pedido de R$ {total_amount}")
                return {
                    'state': state,
                    'original_cost': shipping_cost,
                    'final_cost': 0.00,
                    'free_shipping': True,
                    'message': f'Frete grátis para compras acima de R$ {free_shipping_threshold:.2f}'
                }

            logger.info(f"Frete calculado: R$ {shipping_cost} para {state}")
            return {
                'state': state,
                'original_cost': shipping_cost,
                'final_cost': shipping_cost,
                'free_shipping': False,
                'message': f'Valor do frete para {state}'
            }

        except Exception as e:
            logger.error(f"Erro ao calcular frete: {str(e)}")
            # Em caso de erro, retornar valor padrão
            default_cost = 25.00
            return {
                'state': state,
                'original_cost': default_cost,
                'final_cost': default_cost,
                'free_shipping': False,
                'message': 'Valor de frete padrão aplicado',
                'error': str(e)
            }

    @staticmethod
    def get_shipping_estimate_days(state):
        """
        Estima o prazo de entrega em dias úteis baseado no estado

        Args:
            state: Sigla do estado (UF)

        Returns:
            int: Número estimado de dias úteis para entrega
        """
        # Prazos estimados por região (em dias úteis)
        delivery_days = {
            'SP': 2,
            'RJ': 3,
            'MG': 3,
            'ES': 4,
            'PR': 4,
            'SC': 5,
            'RS': 5,
            'default': 7
        }

        state = state.upper() if state else ''
        return delivery_days.get(state, delivery_days.get('default', 7))

    @staticmethod
    def get_all_shipping_rates():
        """
        Retorna todas as taxas de frete configuradas

        Returns:
            dict: Tabela de taxas de frete por estado
        """
        try:
            shipping_rates = current_app.config.get('SHIPPING_RATES', {})
            return shipping_rates
        except Exception as e:
            logger.error(f"Erro ao obter tabela de fretes: {str(e)}")
            return {}
