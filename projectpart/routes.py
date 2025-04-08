from flask import Blueprint, render_template, redirect, url_for, request, flash
from models import db, Product, Transaction
from forms import ProductForm

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

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

