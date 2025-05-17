from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,FileField,IntegerField
from wtforms.validators import DataRequired,Email,EqualTo,Length,Optional




class myForm(FlaskForm):
    name=StringField('USER NAME',validators=[DataRequired()])
    email=StringField('email',validators=[Optional(),DataRequired(),Email()])
    password=PasswordField('password',validators=[Optional(),DataRequired(), Length(min=8, message="Password must be at least 8 characters long")])
    confrim_password = PasswordField('Confirm Password', validators=[Optional(),
    DataRequired(),
    EqualTo('password', message="Passwords must match")])
    submit=SubmitField('submit')
    
        
class loginform(FlaskForm):
    login_email = StringField('Email', validators=[DataRequired(), Email() ])
    login_password = PasswordField('Password', validators=[
        DataRequired(), Length(min=8, message="Password must be at least 8 characters long")
    ])
    submit = SubmitField('LOGIN')

class image_saveform(FlaskForm):

    product_pic = FileField('Upload Image', validators=[DataRequired()])
    product_price=IntegerField('product price',validators=[DataRequired()])
    product_name=StringField('product name',validators=[DataRequired()])
    submit=SubmitField('submit')


class Userprofile_pic(FlaskForm):
    userprofile_pic=FileField('Upload',validators=[DataRequired()])
    submit=SubmitField('submit')
    


