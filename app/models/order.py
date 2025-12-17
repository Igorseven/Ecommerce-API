"""
Model de Pedido (Order)
"""
from app.database import db
from datetime import datetime
import random
import string


class Order(db.Model):
    """Modelo de Pedido"""

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    address = db.relationship('Address', backref='order', uselist=False, cascade='all, delete-orphan')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        """Inicializa o pedido com número único"""
        super(Order, self).__init__(**kwargs)
        if not self.order_number:
            self.order_number = self._generate_order_number()

    @staticmethod
    def _generate_order_number():
        """Gera um número de pedido único no formato ORD-YYYYMMDD-XXXX"""
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"ORD-{date_str}-{random_str}"

    def calculate_total(self):
        """Calcula o total do pedido (itens + frete)"""
        items_total = sum(float(item.total_price) for item in self.items)
        self.total_amount = items_total + float(self.shipping_cost)
        return self.total_amount

    def to_dict(self, include_details=False):
        """
        Converte o pedido para dicionário

        Args:
            include_details: Se True, inclui endereço e itens

        Returns:
            dict: Representação do pedido
        """
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'total_amount': float(self.total_amount),
            'shipping_cost': float(self.shipping_cost),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_details:
            data['address'] = self.address.to_dict() if self.address else None
            data['items'] = [item.to_dict() for item in self.items]

        return data

    def __repr__(self):
        return f"<Order {self.order_number} - {self.customer_name}>"
