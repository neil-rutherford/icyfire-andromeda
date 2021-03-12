from flask_login import current_user, login_required
from app import db
from flask import flash, redirect, url_for, request
from app.models import User, Message
from app.main import bp
import datetime
from app.payment.utils import pause_subscription


@bp.route('/coins/redeem')
@login_required
def redeem_coins():
    if current_user.coins < 500:
        flash("You must have 500 coins or more.")
        return redirect(url_for('auth.settings'))
    current_user.coins -= 500
    current_user.expires_on = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    db.session.commit()
    pause_subscription(entity_type='user', entity_id=current_user.id)
    flash("Transaction successful. You have spent 500 coins, and your subscription has been extended by 30 days.")
    return redirect(url_for('auth.settings'))


@bp.route('/coins/gift', methods=['POST'])
@login_required
def gift_coins():
    if request.method != 'POST':
        abort(405)

    username = str(request.form.get('username'))
    amount = int(request.form.get('amount'))

    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username))
        return redirect(url_for('auth.settings'))
    if current_user.coins < int(request.form.get('amount')):
        flash("You cannot gift {} coins when you only have a balance of {}.".format(amount, current_user.coins))
        return redirect(url_for('auth.settings'))
    
    current_user.coins -= amount
    user.coins += amount

    message = Message()
    message.from_user_id = current_user.id
    message.to_user_id = user.id
    message.subject = '{} just sent you {} coins!'.format(current_user.username, amount)
    message.body = str(request.form.get('body'))
    message.sent_timestamp = datetime.datetime.utcnow()

    db.session.add(message)
    db.session.commit()
    flash("You have successfully gifted {} coins to {}.".format(amount, username))
    return redirect(url_for('auth.settings'))