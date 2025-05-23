from extensions import db
from flask_login import UserMixin
from datetime import datetime
from decimal import Decimal

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, email, password_hash, phone=None, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.is_admin = is_admin

    def __repr__(self):
        return f'<User {self.email}>'

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column('product_id', db.Integer, primary_key=True)  # Match the foreign key reference
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image = db.Column(db.String(200))
    category = db.Column(db.String(50))
    discount = db.Column(db.Integer, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='product', lazy=True)

    def get_discounted_price(self):
        """Calculate discounted price with proper decimal handling"""
        if self.discount:
            return float(self.price * Decimal(str(1 - self.discount/100)))
        return float(self.price)

    def update_stock(self, quantity):
        if self.stock_quantity >= quantity:
            self.stock_quantity -= quantity
            return True
        return False

    def __repr__(self):
        return f'<Product {self.name}>'

class Review(db.Model):
    __tablename__ = 'reviews'  # Match existing table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # Match product_id column
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    helpful_count = db.Column(db.Integer, default=0)

class Order(db.Model):
    __tablename__ = 'orders'  # Match existing table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, shipped, delivered, cancelled
    items = db.relationship('OrderItem', backref='order', lazy=True)
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_state = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=True)
    tracking_number = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items)

    def get_status_display(self):
        return self.status.title()

class OrderItem(db.Model):
    __tablename__ = 'order_items'  # Fix table name
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)  # Match product_id column
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)  # Store price at time of purchase
    discount_at_time = db.Column(db.Integer, nullable=True)  # Store discount at time of purchase

    @property
    def subtotal(self):
        if self.discount_at_time:
            discounted_price = self.price_at_time * (1 - self.discount_at_time/100)
            return discounted_price * self.quantity
        return self.price_at_time * self.quantity

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), nullable=False)  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50), nullable=False)  # credit_card, debit_card, upi, net_banking
    transaction_id = db.Column(db.String(100), nullable=True)
    order = db.relationship('Order', backref='payment', lazy=True, uselist=False)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column('cart_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship('User', backref='cart_items', lazy=True)
    product = db.relationship('Product', backref='cart_entries', lazy=True)
