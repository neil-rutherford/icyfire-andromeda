from app.analytics import bp
from app import db
from app.models import Article, Share, ActivityLog
from flask import session, request, url_for, redirect
import uuid
from flask_login import current_user
import datetime


@bp.route('/_analytics/share/facebook/article=<int:article_id>')
def share_facebook(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        abort(404)
    share = Share(timestamp=datetime.datetime.utcnow())
    share.share_uuid = str(uuid.uuid4())
    share.article_id = article.id
    if current_user.is_anonymous is True:
        share.anonymous_uuid = session['anonymous_uuid']
        share.user_id = None
    else:
        share.anonymous_uuid = None
        share.user_id = current_user.id
    if 'X-Forwarded-For' in request.headers:
        share.ip_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        share.ip_address = request.remote_addr or 'untrackable'
    share.network = 1
    db.session.add(share)
    db.session.commit()
    return redirect(
        "https://www.facebook.com/sharer/sharer.php?u={}?share={}".format(url_for('main.view_article', slug=article.slug, _external=True), share.share_uuid)        
    )


@bp.route('/_analytics/share/twitter/article=<int:article_id>')
def share_twitter(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        abort(404)
    share = Share(timestamp=datetime.datetime.utcnow())
    share.share_uuid = str(uuid.uuid4())
    share.article_id = article.id
    if current_user.is_anonymous is True:
        share.anonymous_uuid = session['anonymous_uuid']
        share.user_id = None
    else:
        share.anonymous_uuid = None
        share.user_id = current_user.id
    if 'X-Forwarded-For' in request.headers:
        share.ip_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        share.ip_address = request.remote_addr or 'untrackable'
    share.network = 2
    db.session.add(share)
    db.session.commit()
    return redirect(
        "https://twitter.com/intent/tweet?text={}?share={}".format(url_for('main.view_article', slug=article.slug, _external=True), share.share_uuid)        
    )


@bp.route('/_analytics/share/tumblr/article=<int:article_id>')
def share_tumblr(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        abort(404)
    share = Share(timestamp=datetime.datetime.utcnow())
    share.share_uuid = str(uuid.uuid4())
    share.article_id = article.id
    if current_user.is_anonymous is True:
        share.anonymous_uuid = session['anonymous_uuid']
        share.user_id = None
    else:
        share.anonymous_uuid = None
        share.user_id = current_user.id
    if 'X-Forwarded-For' in request.headers:
        share.ip_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        share.ip_address = request.remote_addr or 'untrackable'
    share.network = 3
    db.session.add(share)
    db.session.commit()
    return redirect(
        "http://www.tumblr.com/share/link?url={}?share={}".format(url_for('main.view_article', slug=article.slug, _external=True), share.share_uuid)        
    )


@bp.route('/_analytics/share/linkedin/article=<int:article_id>')
def share_linkedin(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        abort(404)
    share = Share(timestamp=datetime.datetime.utcnow())
    share.share_uuid = str(uuid.uuid4())
    share.article_id = article.id
    if current_user.is_anonymous is True:
        share.anonymous_uuid = session['anonymous_uuid']
        share.user_id = None
    else:
        share.anonymous_uuid = None
        share.user_id = current_user.id
    if 'X-Forwarded-For' in request.headers:
        share.ip_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
    else:
        share.ip_address = request.remote_addr or 'untrackable'
    share.network = 4
    db.session.add(share)
    db.session.commit()
    return redirect(
        "https://www.linkedin.com/sharing/share-offsite/?url={}?share={}".format(url_for('main.view_article', slug=article.slug, _external=True), share.share_uuid)        
    )