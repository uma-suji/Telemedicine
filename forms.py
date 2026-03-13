from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class RegisterForm(FlaskForm):
    fullname = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    role = SelectField("Role", choices=[("doctor", "Doctor"), ("patient", "Patient")], validators=[DataRequired()])
    specialization = StringField("Specialization")  # optional, shown only if doctor
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
