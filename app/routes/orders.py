"""
Rotas para gerenciamento de pedidos (Orders)
CRUD completo: POST, GET, PUT, DELETE
"""
from flask import Blueprint, jsonify, request
from app.database import db
from app.models.order import Order
from app.models.address import Address
from app.models.order_item import OrderItem
from app.services.viacep_service import ViaCEPService
from app.services.shipping_service import ShippingService
from marshmallow import Schema, fields, ValidationError, validate
import logging

logger = logging.getLogger(__name__)

# Criar blueprint
orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')


# Schemas de validação com Marshmallow
class OrderItemSchema(Schema):
    """Schema para validação de itens do pedido"""
    product_id = fields.Int(required=True)
    product_name = fields.Str(required=True)
    product_image = fields.Str(required=False, allow_none=True)
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Decimal(required=True, as_string=True)


class AddressSchema(Schema):
    """Schema para validação de endereço"""
    cep = fields.Str(required=True)
    number = fields.Str(required=False, allow_none=True)
    complement = fields.Str(required=False, allow_none=True)


class CreateOrderSchema(Schema):
    """Schema para validação de criação de pedido"""
    customer_name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    customer_email = fields.Email(required=True)
    customer_phone = fields.Str(required=False, allow_none=True)
    address = fields.Nested(AddressSchema, required=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True, validate=validate.Length(min=1))


class UpdateOrderSchema(Schema):
    """Schema para validação de atualização de pedido"""
    customer_name = fields.Str(required=False, validate=validate.Length(min=3, max=100))
    customer_email = fields.Email(required=False)
    customer_phone = fields.Str(required=False, allow_none=True)
    status = fields.Str(required=False, validate=validate.OneOf(['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']))


# Instanciar schemas
create_order_schema = CreateOrderSchema()
update_order_schema = UpdateOrderSchema()


@orders_bp.route('', methods=['POST'])
def create_order():
    """
    POST /api/orders - Criar novo pedido

    Body JSON:
    {
        "customer_name": "João Silva",
        "customer_email": "joao@email.com",
        "customer_phone": "11999999999",
        "address": {
            "cep": "01310100",
            "number": "123",
            "complement": "Apto 45"
        },
        "items": [
            {
                "product_id": 1,
                "product_name": "Produto A",
                "product_image": "http://...",
                "quantity": 2,
                "unit_price": 50.00
            }
        ]
    }

    Returns:
        201: Pedido criado com sucesso
        400: Dados inválidos
        500: Erro interno
    """
    try:
        # Validar dados de entrada
        data = request.get_json()
        validated_data = create_order_schema.load(data)

        # Validar CEP via ViaCEP
        cep_data = validated_data['address']['cep']
        cep_result = ViaCEPService.validate_and_get_address(cep_data)

        if not cep_result.get('valid'):
            return jsonify({
                'error': 'CEP inválido',
                'details': cep_result.get('error')
            }), 400

        # Criar pedido
        order = Order(
            customer_name=validated_data['customer_name'],
            customer_email=validated_data['customer_email'],
            customer_phone=validated_data.get('customer_phone')
        )

        # Criar endereço
        address = Address(
            cep=cep_result['cep'],
            street=cep_result['street'],
            number=validated_data['address'].get('number'),
            complement=validated_data['address'].get('complement'),
            neighborhood=cep_result['neighborhood'],
            city=cep_result['city'],
            state=cep_result['state']
        )
        order.address = address

        # Criar itens do pedido
        for item_data in validated_data['items']:
            item = OrderItem(
                product_id=item_data['product_id'],
                product_name=item_data['product_name'],
                product_image=item_data.get('product_image'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            item.calculate_total()
            order.items.append(item)

        # Calcular frete
        items_total = sum(float(item.total_price) for item in order.items)
        shipping_info = ShippingService.calculate_shipping(cep_result['state'], items_total)
        order.shipping_cost = shipping_info['final_cost']

        # Calcular total
        order.calculate_total()

        # Salvar no banco de dados
        db.session.add(order)
        db.session.commit()

        logger.info(f"Pedido criado com sucesso: {order.order_number}")

        return jsonify({
            'message': 'Pedido criado com sucesso',
            'order': order.to_dict(include_details=True)
        }), 201

    except ValidationError as e:
        logger.warning(f"Dados inválidos na criação de pedido: {e.messages}")
        return jsonify({
            'error': 'Dados inválidos',
            'details': e.messages
        }), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar pedido: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao criar pedido'
        }), 500


@orders_bp.route('', methods=['GET'])
def get_orders():
    """
    GET /api/orders - Listar todos os pedidos

    Query params:
        - status: Filtrar por status (ex: pending, confirmed)
        - limit: Número máximo de resultados (padrão: 10)
        - offset: Número de registros a pular (paginação)
        - order_by: Campo para ordenação (created_at, total_amount)
        - sort: Direção da ordenação (asc, desc)

    Returns:
        200: Lista de pedidos
        500: Erro interno
    """
    try:
        # Obter parâmetros de query
        status = request.args.get('status')
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        order_by = request.args.get('order_by', 'created_at')
        sort = request.args.get('sort', 'desc')

        # Limitar o limite máximo
        limit = min(limit, 100)

        # Construir query
        query = Order.query

        # Filtrar por status
        if status:
            query = query.filter_by(status=status)

        # Ordenação
        if order_by == 'total_amount':
            order_column = Order.total_amount
        else:
            order_column = Order.created_at

        if sort == 'asc':
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())

        # Paginação
        total_count = query.count()
        orders = query.offset(offset).limit(limit).all()

        # Serializar pedidos
        orders_data = [order.to_dict(include_details=False) for order in orders]

        return jsonify({
            'orders': orders_data,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        logger.error(f"Erro ao listar pedidos: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao listar pedidos'
        }), 500


@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    GET /api/orders/<id> - Buscar pedido específico

    Args:
        order_id: ID do pedido

    Returns:
        200: Dados do pedido
        404: Pedido não encontrado
        500: Erro interno
    """
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({
                'error': 'Pedido não encontrado'
            }), 404

        return jsonify({
            'order': order.to_dict(include_details=True)
        }), 200

    except Exception as e:
        logger.error(f"Erro ao buscar pedido {order_id}: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao buscar pedido'
        }), 500


@orders_bp.route('/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """
    PUT /api/orders/<id> - Atualizar pedido

    Args:
        order_id: ID do pedido

    Body JSON:
    {
        "customer_name": "João Silva Jr.",
        "customer_email": "joao.jr@email.com",
        "customer_phone": "11888888888",
        "status": "confirmed"
    }

    Returns:
        200: Pedido atualizado
        400: Dados inválidos
        404: Pedido não encontrado
        500: Erro interno
    """
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({
                'error': 'Pedido não encontrado'
            }), 404

        # Validar dados de entrada
        data = request.get_json()
        validated_data = update_order_schema.load(data)

        # Atualizar campos
        if 'customer_name' in validated_data:
            order.customer_name = validated_data['customer_name']
        if 'customer_email' in validated_data:
            order.customer_email = validated_data['customer_email']
        if 'customer_phone' in validated_data:
            order.customer_phone = validated_data['customer_phone']
        if 'status' in validated_data:
            order.status = validated_data['status']

        # Salvar alterações
        db.session.commit()

        logger.info(f"Pedido {order.order_number} atualizado com sucesso")

        return jsonify({
            'message': 'Pedido atualizado com sucesso',
            'order': order.to_dict(include_details=True)
        }), 200

    except ValidationError as e:
        logger.warning(f"Dados inválidos na atualização do pedido {order_id}: {e.messages}")
        return jsonify({
            'error': 'Dados inválidos',
            'details': e.messages
        }), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar pedido {order_id}: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao atualizar pedido'
        }), 500


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """
    DELETE /api/orders/<id> - Deletar pedido

    Args:
        order_id: ID do pedido

    Returns:
        204: Pedido deletado com sucesso
        404: Pedido não encontrado
        500: Erro interno
    """
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({
                'error': 'Pedido não encontrado'
            }), 404

        order_number = order.order_number

        # Deletar pedido (cascade vai deletar endereço e itens)
        db.session.delete(order)
        db.session.commit()

        logger.info(f"Pedido {order_number} deletado com sucesso")

        return '', 204

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar pedido {order_id}: {str(e)}")
        return jsonify({
            'error': 'Erro interno ao deletar pedido'
        }), 500
