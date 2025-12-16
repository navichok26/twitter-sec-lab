from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, Group

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    group_id = SelectField('Group', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Post')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.group_id.choices = [(g.id, g.name) for g in Group.query.all()]

class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Update Post')

class TransferPostForm(FlaskForm):
    new_owner_id = SelectField('New Owner', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Transfer Post')
    
    def __init__(self, *args, **kwargs):
        super(TransferPostForm, self).__init__(*args, **kwargs)
        self.new_owner_id.choices = [(u.id, u.username) for u in User.query.all()]

class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    owner_id = SelectField('Group Admin', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Group')
    
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        # ?????????? ?????? ????????????? ? ????? group_admin ??? ??????????
        admins = User.query.filter_by(role='group_admin').all()
        self.owner_id.choices = [(u.id, u.username) for u in admins]