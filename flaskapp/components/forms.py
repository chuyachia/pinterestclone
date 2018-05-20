from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL

class AddNewForm(FlaskForm):
    url = StringField('Image URL', validators=[DataRequired(),URL()])
    desc = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add')
