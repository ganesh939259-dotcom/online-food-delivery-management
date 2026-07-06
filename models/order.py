from models.user import db
from datetime import datetime


class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(15), nullable=False)

    food = db.Column(db.String(100), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)

    total = db.Column(db.Float, nullable=False)

    payment = db.Column(db.String(50), nullable=False)

    status = db.Column(
    db.String(50),
    default="Pending"
)

    order_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )