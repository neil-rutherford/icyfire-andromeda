from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class ApplicationForm(FlaskForm):

    company_name = StringField('Company name', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Company name'})
    contact_name = StringField('Point of contact (POC) name', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Point of contact (POC) name'})
    phone_number = StringField('POC phone number', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'POC phone number'})
    email = StringField('POC email', render_kw={'style': 'width:50%;', 'placeholder': 'POC email'})
    
    is_articles = BooleanField('Articles')
    is_comments = BooleanField('Comments')
    is_logs = BooleanField('Activity logs')
    is_shares = BooleanField('Shares')
    is_users = BooleanField('Users')
    is_connections = BooleanField('Connections')
    is_messages = BooleanField('Messages')
    is_api = BooleanField('API')
    permission_justification = TextAreaField('If needed, use this space to explain why you are requesting certain permissions.', render_kw={'style': 'width:50%;', 'placeholder': 'If needed, use this space to explain why you are requesting certain permissions.'})

    use_case = TextAreaField('Use case', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Use case'})
    developer_platform = StringField('Developer platform', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Developer platform'})
    monetization_model = TextAreaField('Monetization model', validators=[DataRequired()], render_kw={'style': 'width:50%;', 'placeholder': 'Monetization model'})

    submit = SubmitField('Submit', render_kw={'class': 'btn btn-primary btn-lg'})
    