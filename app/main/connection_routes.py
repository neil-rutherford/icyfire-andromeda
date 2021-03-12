from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import Article, Comment, User
from app.main import bp
from app import db


@bp.route('/view/user/<username>')
def view_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    articles = Article.query.filter_by(user_id=user.id).order_by(Article.timestamp.desc()).all()
    comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.timestamp.desc()).all()
    return render_template(
        'main/view_user.html',
        title='User {}'.format(user.username),
        user=user,
        articles=articles,
        comments=comments
    )


@bp.route('/view/<username>/followers')
def view_followers(username):
    return render_template(
        'main/view_connections.html',
        title="Who follows {}".format(username),
        connection_type="followers",
        username=username,
    )


@bp.route('/view/<username>/following')
def view_following(username):
    return render_template(
        'main/view_connections.html',
        title="Who {} follows".format(username),
        connection_type="following",
        username=username,
    )


@bp.route('/follow/user/<username>')
@login_required
def follow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('main.view_user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following {}!'.format(username))
    return redirect(url_for('main.view_user', username=username))


@bp.route('/unfollow/user/<username>')
@login_required
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}.'.format(username))
    return redirect(url_for('main.view_user', username=username))