from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextField, TextAreaField
from wtforms.fields.core import IntegerField
from wtforms.validators import Regexp, ValidationError, DataRequired, Email, EqualTo, Length, Required
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp(regex = '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', flags=0, message='Your password must be 8-20 characters long, contain capitalized letters and numbers, and must not contain spaces, special characters or emoji.')])
    remember_me = BooleanField('Rememeber Me', default=False)
    token = StringField('Token from Authenticator', validators=[Required(), Length(6, 6)])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp(regex = '(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}', flags=0, message='Your password must be 8-20 characters long, contain capitalized letters and numbers, and must not contain spaces, special characters or emoji.')])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different email adress.')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(min=0, max=50)])
    last_name = StringField('Last Name', validators=[Length(min=0, max=50)])
    cellphone = StringField('Cellphone', validators=[Length(min=0, max=12), Regexp(regex='^[0-9]*$', flags=0, message="Please only insert numbers!")])
    submit = SubmitField('Submit')
    

class AccountForm(FlaskForm):
    AccountName = StringField('Name your account', validators=[
        DataRequired(), Length(min=1, max=140)])
    AccountBalance = IntegerField('Starting balance')
    AccountType = SelectField('Account Type', choices=[("Standard Account", "Standard Account"), ("Gamer Account", "Gamer Account")])
    submit = SubmitField('Submit')

class EditAccountForm(FlaskForm):
    AccountName = StringField('Name your account', validators=[
        DataRequired(), Length(min=1, max=140)])
    AccountType = SelectField('Account Type', choices=[("Standard Account", "Standard Account"), ("Gamer Account", "Gamer Account")])
    submit = SubmitField('Submit')

class ContactForm(FlaskForm):
  name1 = TextField("Name",  validators=[Required("Please enter your name.")])
  email1 = TextField("Email",  validators=[Required("Please enter your email address."), Email()])
  type1 = SelectField('Inquiry type', choices=[("Loan application", "Loan application"), ("Credit Card application", "Credit Card application"), ("Activation of a deactivated account", "Activation of a deactivated account"), ("Other", "Other")])
  subject1 = TextField("Subject",  validators=[Required("Please enter a subject.")])
  message1 = TextAreaField("Message",  validators=[Required("Please enter a message.")])
  submit1 = SubmitField("Send inquiry")
