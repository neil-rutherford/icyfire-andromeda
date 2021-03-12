from app.api import bp
from flask import flash, redirect, url_for, render_template
from app.models import ApiClient, Message
from app import db
from flask_login import login_required, current_user
import uuid
import datetime
from app.api.forms import ApplicationForm

@bp.route('/api/apply', methods=["GET", "POST"])
@login_required
def apply():
    form = ApplicationForm()
    if form.validate_on_submit():
        client = ApiClient()
        client.user_id = current_user.id
        client.is_approved = False
        client.is_blacklist = False
        client.consumer_key = str(uuid.uuid4())
        client.consumer_secret = str(uuid.uuid4())
        client.stripe_customer_id = None
        client.expires_on = datetime.datetime(1970, 1, 1)
        client.is_articles = bool(form.is_articles.data)
        client.is_comments = bool(form.is_comments.data)
        client.is_logs = bool(form.is_logs.data)
        client.is_shares = bool(form.is_shares.data)
        client.is_users = bool(form.is_users.data)
        client.is_connections = bool(form.is_connections.data)
        client.is_messages = bool(form.is_messages.data)
        client.is_api = bool(form.is_api.data)
        client.company_name = str(form.company_name.data)
        client.contact_name = str(form.contact_name.data)
        client.phone_number = str(form.phone_number.data)
        client.email = str(form.email.data)
        client.use_case = str(form.use_case.data)
        client.developer_platform = str(form.developer_platform.data)
        client.monetization_model = str(form.monetization_model.data)
        client.permission_justification = str(form.permission_justification.data)
        db.session.add(client)
        db.session.commit()

        message = Message()
        message.to_user_id = current_user.id
        message.subject = 'Your Galatea API application'
        message.body = 'Thank you for applying for Galatea API permissions. We are currently reviewing your application. You may check on its status here: {}.'.format(url_for('api.view_client'))
        message.sent_timestamp = datetime.datetime.utcnow()
        message.seen_timestamp = None
        db.session.add(message)
        db.session.commit()
        flash("Your API application has been received!")
        return redirect(url_for('api.view_client'))
    return render_template(
        'api/apply.html',
        title='Apply for API permissions',
        form=form
    )


@bp.route('/api/view-client')
@login_required
def view_client():
    client = ApiClient.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template(
        'api/view_client.html',
        title='Your app',
        client=client
    )