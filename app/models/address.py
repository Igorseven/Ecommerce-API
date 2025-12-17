"""
Model de Endereço (Address)
"""
from app.database import db


class Address(db.Model):
    """Modelo de Endereço de Entrega"""

    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    number = db.Column(db.String(10), nullable=True)
    complement = db.Column(db.String(100), nullable=True)
    neighborhood = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)

    def to_dict(self):
        """
        Converte o endereço para dicionário

        Returns:
            dict: Representação do endereço
        """
        return {
            'id': self.id,
            'cep': self.cep,
            'street': self.street,
            'number': self.number,
            'complement': self.complement,
            'neighborhood': self.neighborhood,
            'city': self.city,
            'state': self.state
        }

    def __repr__(self):
        return f"<Address {self.street}, {self.number} - {self.city}/{self.state}>"
