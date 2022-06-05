from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired


class PolicyDataForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired('Field required')])
    version = FloatField("Version", validators=[DataRequired('Field required')])
    credential_name = StringField("Requested credential", validators=[DataRequired('Field required')])
    attribute1 = StringField("Attribute 1", validators=[DataRequired('Field required')])
    attribute2 = StringField("Attribute 2", validators=[DataRequired('Field required')])
    attribute3 = StringField("Attribute 3", validators=[DataRequired('Field required')])
    attribute4 = StringField("Attribute 4", validators=[DataRequired('Field required')])
    attribute5 = StringField("Attribute 5", validators=[DataRequired('Field required')])
    schema_id = StringField("Schema ID", validators=[DataRequired('Field required')])
    issuer_did = StringField("Issuer DID", validators=[DataRequired('Field required')])
    submit = SubmitField('Add policy')
