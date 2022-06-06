from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField, FloatField
from wtforms.validators import DataRequired


class TemplateForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired('Field required')])
    version = FloatField("Version", validators=[DataRequired('Field required')])
    tag = StringField("Tag", validators=[DataRequired('Field required')])
    attribute1 = StringField("Attribute 1", validators=[DataRequired('Field required')])
    attribute2 = StringField("Attribute 2", validators=[DataRequired('Field required')])
    attribute3 = StringField("Attribute 3", validators=[DataRequired('Field required')])
    attribute4 = StringField("Attribute 4", validators=[DataRequired('Field required')])
    attribute5 = StringField("Attribute 5", validators=[DataRequired('Field required')])
    supportRevocation = BooleanField("Support revocation?")
    submit = SubmitField('Add credential definition')

class PolicyForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired('Field required')])
    version = FloatField("Version", validators=[DataRequired('Field required')])
    credential_name = StringField("Requested credential", validators=[DataRequired('Field required')])
    attribute1 = StringField("Attribute 1", validators=[DataRequired('Field required')])
    attribute2 = StringField("Attribute 2", validators=[DataRequired('Field required')])
    attribute3 = StringField("Attribute 3", validators=[DataRequired('Field required')])
    attribute4 = StringField("Attribute 4", validators=[DataRequired('Field required')])
    schema_id = StringField("Schema ID", validators=[DataRequired('Field required')])
    issuer_did = StringField("Issuer DID", validators=[DataRequired('Field required')])
    submit = SubmitField('Add policy')



class YForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired('Field required')])
    last_name = StringField("Last Name", validators=[DataRequired('Field required')])
    agency_name = StringField("Agency name", validators=[DataRequired('Field required')])
    role = StringField("Role", validators=[DataRequired('Field required')])
    LIID = StringField("LLID", validators=[DataRequired('Field required')])
    submit = SubmitField('Send credential')


class EmailForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired('Field required')])
    password = PasswordField("Password", validators=[DataRequired('Field required')])
    email_to = StringField("Email To", validators=[DataRequired('Field required')])
    object = StringField("Object", validators=[DataRequired('Field required')])
    message = TextAreaField("Message", validators=[DataRequired('Field required')])
    submit = SubmitField('Send invitation to email')