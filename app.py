from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'MyKey'
db = SQLAlchemy(app)

#the models for the product and transaction tables
from datetime import datetime
class Product(db.model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)#carbs, fruits n vegies, proteins
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.eatnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.eatnow)
    quantity = db.Column(db.Integer, default=0)
    transactions = db.relationship('Transaction', backref='product', lazy=True)
    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.quantity}')"
    

class Transaction(db.model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.eatnow)
    transaction_type = db.Column(db.String(20), nullable=False)    #types zikuwe add, delete, edit a pdt
    
    def __repr__(self):
        return f"Transaction('{self.product_id}', '{self.quantity}', '{self.transaction_date}')"

with app.app_context():
    db.create_all()
    

#the forms for the product and transaction tables
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description')
    category = SelectField('Category', choices=[('carbs', 'Carbs'), ('fruits', 'Fruits & Veggies'), ('proteins', 'Proteins')], validators=[DataRequired()])
    submit = SubmitField('Save')

#routes for the app
from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, Product, Transaction
from forms import ProductForm

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)
#adding a pdt
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
      new_product = Product(
          name=form.name.data,
          price=form.price.data,
          category=form.category.data,
          quantity=form.quantity.data
                )  
      db.session.add(new_product)
      db.session.commit()
      transaction = Transaction(product_id=new_product.id, quantity=form.quantity.data, transaction_type='add')
      db.session.add(transaction)
      db.session.commit()  
      flash('Product added successfully!', 'success')
      return redirect(url_for('index'))
    return render_template('add_product.html', form=form)

#editing a pdt
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.category = form.category.data
        product.quantity = form.quantity.data
        db.session.commit()
        transaction = Transaction(product_id=product.id, quantity=form.quantity.data, transaction_type='edit')
        db.session.add(transaction)
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_product.html', form=form, product=product)

#deleting a pdt
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        transaction = Transaction(product_id=product.id, quantity=product.quantity, transaction_type='delete')
        db.session.add(transaction)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    else:
        flash('Product not found!', 'danger')
    return redirect(url_for('index'))

#fetching all transactions happening
@app.route('/transactions')
def view_transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

#generating reports

from sqlalchemy import func
@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/reports/generate', methods=['POST'])
def generate_report():
    report_type = request.form['report_type']
    start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
    
    # Adjust end_date to include the entire day
    end_date = end_date.replace(hour=23, minute=59, second=59)
    
    if report_type == 'transaction_summary':
        # Get transaction counts by type
        transaction_counts = db.session.query(
            Transaction.transaction_type,
            func.count(Transaction.id)
        ).filter(
            Transaction.timestamp.between(start_date, end_date)
        ).group_by(Transaction.transaction_type).all()
        
        # Get product with most transactions
        product_transactions = db.session.query(
            Transaction.product_id,
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.timestamp.between(start_date, end_date)
        ).group_by(Transaction.product_id).order_by(func.count(Transaction.id).desc()).first()
        
        most_active_product = None
        if product_transactions:
            most_active_product = Product.query.get(product_transactions[0])
        
        return render_template(
            'transaction_summary_report.html',
            transaction_counts=transaction_counts,
            most_active_product=most_active_product,
            start_date=start_date,
            end_date=end_date
        )
    
    elif report_type == 'inventory_status':
        # Get current inventory status
        products = Product.query.all()
        
        # Get products with low inventory (less than 10 items)
        low_inventory = Product.query.filter(Product.quantity < 10).all()
        
        # Get products with no inventory
        out_of_stock = Product.query.filter(Product.quantity == 0).all()
        
        return render_template(
            'inventory_status_report.html',
            products=products,
            low_inventory=low_inventory,
            out_of_stock=out_of_stock,
            start_date=start_date,
            end_date=end_date
        )
    
    flash('Invalid report type selected', 'danger')
    return redirect(url_for('reports'))


