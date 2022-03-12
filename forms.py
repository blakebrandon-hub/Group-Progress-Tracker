from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me', validators=[])


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


class BoardForm(FlaskForm):
    title = StringField('Title')
    private = BooleanField('Private')
    description = StringField('Description')


class BoardUpdateForm(FlaskForm):
    title = StringField('Title')
    private = SelectField('Privacy', choices=[("Public", "Public"), ("Private", "Private")]) 
    description = StringField('Description')   


class DeleteForm(FlaskForm):
    confirm = BooleanField('Are you sure?')


class CollaboratorForm(FlaskForm):
    user = StringField('Username', validators=[InputRequired()])


class GroupForm(FlaskForm):
    title = StringField('Title')


class ProfileForm(FlaskForm):
    bio = StringField('Bio')


class TicketForm(FlaskForm):
    text = StringField('Ticket')


class TicketUpdateForm(FlaskForm):
    text = StringField('Ticket')
    status = SelectField('Status', choices=[(" ", " "), ("Working On It", "Working On It"), ("Completed", "Completed")])
    assign = StringField('Assign collaborator to ticket')


class CommentForm(FlaskForm):
    text = StringField('Comment')
    