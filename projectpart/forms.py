from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired()])
    description = StringField('Description')
    category = SelectField('Category', choices=[('carbs', 'Carbs'), ('fruits', 'Fruits & Veggies'), ('proteins', 'Proteins')], validators=[DataRequired()])
    submit = SubmitField('Save')

#should i add a transaction form?


