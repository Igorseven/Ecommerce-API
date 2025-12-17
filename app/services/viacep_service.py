"""
Serviço de integração com a API ViaCEP
"""
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class ViaCEPService:
    """Serviço para validar e buscar informações de CEP"""

    @staticmethod
    def _clean_cep(cep):
        """
        Remove caracteres não numéricos do CEP

        Args:
            cep: CEP com ou sem formatação

        Returns:
            str: CEP apenas com números
        """
        return ''.join(filter(str.isdigit, cep))

    @staticmethod
    def validate_and_get_address(cep):
        """
        Valida um CEP e retorna os dados do endereço

        Args:
            cep: CEP a ser validado (com ou sem formatação)

        Returns:
            dict: Dados do endereço ou None se inválido
        """
        try:
            # Limpar CEP
            clean_cep = ViaCEPService._clean_cep(cep)

            # Validar formato
            if len(clean_cep) != 8:
                logger.warning(f"CEP inválido (comprimento incorreto): {cep}")
                return {
                    'valid': False,
                    'error': 'CEP deve conter 8 dígitos'
                }

            # Buscar na API ViaCEP
            api_url = current_app.config.get('VIACEP_API_URL', 'https://viacep.com.br/ws')
            url = f"{api_url}/{clean_cep}/json/"

            logger.info(f"Consultando ViaCEP: {url}")
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            data = response.json()

            # Verificar se o CEP foi encontrado
            if data.get('erro'):
                logger.warning(f"CEP não encontrado: {cep}")
                return {
                    'valid': False,
                    'error': 'CEP não encontrado'
                }

            # Formatar resposta
            formatted_cep = f"{clean_cep[:5]}-{clean_cep[5:]}"
            return {
                'valid': True,
                'cep': formatted_cep,
                'street': data.get('logradouro', ''),
                'complement': data.get('complemento', ''),
                'neighborhood': data.get('bairro', ''),
                'city': data.get('localidade', ''),
                'state': data.get('uf', ''),
                'ibge': data.get('ibge', ''),
                'gia': data.get('gia', ''),
                'ddd': data.get('ddd', '')
            }

        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao consultar CEP: {cep}")
            return {
                'valid': False,
                'error': 'Timeout ao consultar CEP. Tente novamente.'
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar ViaCEP: {str(e)}")
            return {
                'valid': False,
                'error': 'Erro ao consultar serviço de CEP'
            }

        except Exception as e:
            logger.error(f"Erro inesperado ao validar CEP: {str(e)}")
            return {
                'valid': False,
                'error': 'Erro interno ao processar CEP'
            }

    @staticmethod
    def format_cep(cep):
        """
        Formata o CEP no padrão XXXXX-XXX

        Args:
            cep: CEP sem formatação

        Returns:
            str: CEP formatado
        """
        clean_cep = ViaCEPService._clean_cep(cep)
        if len(clean_cep) == 8:
            return f"{clean_cep[:5]}-{clean_cep[5:]}"
        return cep
