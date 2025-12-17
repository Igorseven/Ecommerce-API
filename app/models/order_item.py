"""
Model de Item do Pedido (OrderItem)
"""
from app.database import db


class OrderItem(db.Model):
    """Modelo de Item do Pedido"""

    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_image = db.Column(db.String(500), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, **kwargs):
        """Inicializa o item e calcula o total"""
        super(OrderItem, self).__init__(**kwargs)
        if self.quantity and self.unit_price and not self.total_price:
            self.calculate_total()

    def calculate_total(self):
        """Calcula o preço total do item (quantidade * preço unitário)"""
        self.total_price = self.quantity * self.unit_price
        return self.total_price

    def to_dict(self):
        """
        Converte o item para dicionário

        Returns:
            dict: Representação do item
        """
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_image': self.product_image,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price)
        }

    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
