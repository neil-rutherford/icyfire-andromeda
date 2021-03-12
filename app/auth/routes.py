from app.auth import bp
from flask import flash, render_template, url_for, request, redirect, session
from app.auth.email import send_password_reset_email, send_verify_email_email
from app.models import User, ApiClient
from app import db
from app.auth.forms import RegisterForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm
import datetime
from flask_login import current_user, login_required, login_user, logout_user
from app.auth.utils import transfer_logs, transfer_shares
from app.payment.utils import cancel_subscription
import hashlib
import uuid


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm(prefix='form-register-')
    if form.validate_on_submit():
        user = User()
        user.email = str(form.email.data)
        user.set_password(str(form.password.data))
        user.expires_on = datetime.datetime(1970, 1, 1)
        user.username = str(form.username.data)
        user.status = None
        user.dob = datetime.datetime(int(form.yob.data), 1, 1)
        user.gender = int(form.gender.data)
        user.profile_pic = 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png'
        user.coins = 0
        user.is_verified = False
        db.session.add(user)
        db.session.commit()

        if 'anonymous_uuid' in session:
            anonymous_uuid = session['anonymous_uuid']
            transfer_logs(anonymous_uuid=anonymous_uuid, user_id=user.id)
            transfer_shares(anonymous_uuid=anonymous_uuid, user_id=user.id)

        flash("Welcome, {}!".format(user.username))
        login_user(user, remember=True)
        return redirect(url_for('auth.settings'))
    return render_template(
        'auth/register.html', 
        title='Register', 
        form=form
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=str(form.email.data)).first()
        if user is None or not user.check_password(str(form.password.data)):
            flash('ERROR: Invalid email or password.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template(
        'auth/login.html', 
        title='Log In', 
        form=form
    )


@bp.route('/logout')
def logout():
    logout_user()
    flash("Successfully logged out.")
    return redirect(url_for('main.index'))


@bp.route('/settings')
@login_required
def settings():
    if current_user.expires_on == datetime.datetime(1970, 1, 1):
        membership = 'none'
    elif current_user.expires_on < datetime.datetime.utcnow():
        membership = 'expired'
    else:
        membership = 'current'
    return render_template(
        'auth/settings.html', 
        title='Account settings', 
        membership=membership
    )


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        send_password_reset_email(current_user)
        logout_user()
        flash('Check your email for instructions to reset your password. Remember to check your junk mail too!')
        return redirect(url_for('auth.login'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        else:
            flash("Can't find that email address.")
            return redirect(url_for('auth.reset_password_request'))
        flash('Check your email for instructions to reset your password. Remember to check your junk mail too!')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password_request.html', 
        title='Request a password reset', 
        form=form
    )


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template(
        'auth/reset_password.html', 
        title='Reset password', 
        form=form
    )


@bp.route('/send-verification-email')
@login_required
def send_verification_email():
    if current_user.is_verified is False:
        send_verify_email_email(current_user)
        flash("Check your email for instructions to verify your email. Remember to check your junk mail too!")
        return redirect(url_for('auth.settings'))
    else:
        flash("Your email is verified.")
        return redirect(url_for('auth.settings'))


@bp.route('/verify-email/<token>')
def verify_email(token):
    user = User.verify_verify_email_token(token)
    if not user:
        return redirect(url_for('main.index'))
    else:
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        flash("Your email has been verified. Thanks!")
        return redirect(url_for('auth.settings'))


@bp.route('/email/opt-in')
@login_required
def email_opt_in():
    current_user.email_opt_in = True
    db.session.add(current_user)
    db.session.commit()
    flash("Successfully subscribed to email support.")
    return redirect(url_for('auth.settings'))


@bp.route('/email/opt-out')
@login_required
def email_opt_out():
    current_user.email_opt_in = False
    db.session.add(current_user)
    db.session.commit()
    flash("Successfully unsubscribed from email support.")
    return redirect(url_for('auth.settings'))


@bp.route('/account/delete')
@login_required
def delete_account():
    cancel_subscription(entity_type='user', entity_id=current_user.id)
    current_user.email = None
    current_user.password_hash = None
    current_user.expires_on = datetime.datetime.utcnow()
    current_user.username = '[USER {}]'.format(str(uuid.uuid4()))
    current_user.status = None
    current_user.dob = None
    current_user.gender = None
    current_user.email_opt_in = False
    current_user.is_verified = False
    current_user.profile_pic = 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png'
    current_user.coins = 0
    client = ApiClient.query.filter_by(user_id=current_user.id).first()
    if client is not None:
        cancel_subscription(entity_type='api_client', entity_id=current_user.id)
        client.is_blacklist = True
        client.consumer_key = None
        client.consumer_secret = None
        client.is_articles = False
        client.is_comments = False
        client.is_logs = False
        client.is_shares = False
        client.is_connections = False
        client.is_messages = False
        client.is_api = False
    db.session.commit()
    logout_user()
    flash("You have successfully deleted your account. We're sad to see you go!")
    return redirect(url_for('main.index'))

# Works
@bp.route('/set-status', methods=['POST'])
@login_required
def set_status():
    if current_user.check_subscription() is False:
        flash("Only Patriots can update their status.")
        return redirect(url_for('auth.settings'))
    current_user.status = str(request.form.get('status'))
    db.session.commit()
    flash("Status successfully updated!")
    return redirect(url_for('auth.settings'))


@bp.route('/change-profile-pic', methods=['GET', 'POST'])
@login_required
def change_profile_pic():
    if current_user.check_subscription() is False:
        flash("Only Patriots can change their profile picture.")
        return redirect(url_for('auth.settings'))
    hashed_email = hashlib.md5(str(current_user.email).encode()).hexdigest()
    if request.method == "POST":
        current_user.profile_pic = 'https://www.gravatar.com/avatar/{}?s=300'.format(hashed_email)
        db.session.commit()
        flash("Successfully changed your profile picture!")
        return redirect(url_for('auth.settings'))
    return render_template(
        'auth/change_profile_pic.html',
        title='Change your profile picture',
        image_source='https://www.gravatar.com/avatar/{}?s=300'.format(hashed_email)
    )
