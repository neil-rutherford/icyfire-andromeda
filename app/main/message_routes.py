from flask_login import login_required, current_user
from flask import request, redirect, url_for, render_template, flash, abort
from app.models import User, Message
from app import db
from app.main import bp
import datetime

@bp.route('/send/message?id=<username>', methods=['POST'])
@login_required
def send_message(username):
    if request.method != 'POST':
        abort(405)
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    message = Message()
    message.from_user_id = current_user.id
    message.to_user_id = user.id
    message.subject = str(request.form.get('subject'))
    message.body = str(request.form.get('body'))
    message.sent_timestamp = datetime.datetime.utcnow()
    db.session.add(message)
    db.session.commit()
    flash("Message sent!")
    return redirect(url_for('main.view_user', username=user.username))


@bp.route('/inbox')
@login_required
def inbox():
    unread_messages = Message.query.filter(
        Message.to_user_id == current_user.id,
        Message.seen_timestamp == None
    ).order_by(Message.sent_timestamp.desc()).all()
    read_messages = Message.query.filter(
        Message.to_user_id == current_user.id,
        Message.seen_timestamp != None
    ).order_by(Message.sent_timestamp.desc()).all()
    return render_template(
        'main/inbox.html',
        title='Your inbox',
        unread_messages=unread_messages,
        read_messages=read_messages
    )


@bp.route('/view/message?id=<int:message_id>', methods=['POST', 'GET'])
@login_required
def view_message(message_id):
    message = Message.query.filter_by(id=message_id).first()
    previous_message = Message.query.filter_by(id=message.reply_to).first()
    if message is None:
        flash("Sorry, the message is no longer available.")
        return redirect('main.inbox')
    if message.to_user_id != current_user.id:
        flash("That message isn't meant for you.")
        return redirect('main.inbox')
    if message.seen_timestamp is None:
        message.seen_timestamp = datetime.datetime.utcnow()
        db.session.commit()
    if request.method == 'POST':
        reply = Message()
        reply.from_user_id = current_user.id
        reply.to_user_id = message.from_user_id
        reply.subject = str(request.form.get('subject'))
        reply.body = str(request.form.get('body'))
        reply.sent_timestamp = datetime.datetime.utcnow()
        db.session.add(reply)
        db.session.commit()
        flash("Reply sent!")
        return redirect(url_for('main.inbox'))

    return render_template(
        'main/view_message.html',
        title="View message: {}".format(message.subject),
        message=message,
        previous_message=previous_message
    )