from app.main import bp
from flask import render_template, flash, redirect, url_for, request, session, send_from_directory
from app.models import Article, Share, ActivityLog, Comment
import datetime
from app import db
from flask_login import current_user, login_required
import uuid

@bp.before_request
def track_activity():
    if current_user.is_anonymous:
        if 'anonymous_uuid' not in session:
            session['anonymous_uuid'] = str(uuid.uuid4())
            session.permanent = True
    else:
        if current_user.check_subscription() is False and current_user.profile_pic != 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png':
            current_user.profile_pic = 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png'
            db.session.commit()
        if current_user.check_subscription() is False and current_user.status != None:
            current_user.status = None
            db.session.commit()
    if request.path.split('/')[1] == 'article':
        article = Article.query.filter_by(slug=request.path.split('/')[2]).first()
        if article is None:
            pass
        #if 'read_list' in session:
            #session['read_list'] = session['read_list'].extend([article.id])
        #else:
            #session['read_list'] = [article.id]
        if current_user.is_authenticated:
            user_id = current_user.id
            anonymous_uuid = None
        else:
            user_id = None
            anonymous_uuid = session['anonymous_uuid']
        if request.args.get('share'):
            share = Share.query.filter_by(share_uuid=int(request.args.get('share'))).first()
            share_id = share.id
            coin_amount = 2
        else:
            share_id = None
            coin_amount = 1
        if 'X-Forwarded-For' in request.headers:
            ip_address = request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
        else:
            ip_address = request.remote_addr or request.access_route[0]
        referrer_page = request.referrer
        user_agent = request.user_agent.string
        
        log = ActivityLog()
        log.article_id = article.id
        log.anonymous_uuid = anonymous_uuid
        log.user_id = user_id
        log.share_id = share_id
        log.ip_address = ip_address
        log.referrer_page = request.referrer
        log.user_agent = request.user_agent.string
        log.timestamp = datetime.datetime.utcnow()
        db.session.add(log)

        article.author.coins += coin_amount
        db.session.commit()


@bp.route('/')
def index():
    return render_template(
        'main/index.html', 
        section='all',
        title='Welcome to Galatea News',
        banner=['Welcome to Galatea News', 'Come to your own conclusions.', 'banner_videos/title.mp4']
    )

# FIX
#@bp.route('/search')
#def search():
    #results = Article.query.whoosh_search(request.args.get('query')).all()
    #return render_template(
        #'main/search.html',
        #title='Search results - {}'.format(request.args.get('query')),
        #results=results
    #)


@bp.route('/section/<section>')
def view_section(section):
    allowed_sections = ['politics', 'world', 'technology', 'energy', 'economy', 'science', 'health']
    if section not in allowed_sections:
        flash("Can't find that section.")
        return redirect(url_for('main.index'))
    title_dict = {
        'politics': 'U.S. Politics',
        'world': 'World News',
        'technology': 'Technology',
        'energy': 'Energy / Environment',
        'economy': 'Economy / Business',
        'science': 'Science / Religion',
        'health': 'Health'
    }
    banner_dict = {
        'politics': ['U.S. Politics', ' ', 'banner_videos/politics.mp4'],
        'world': ['World News', ' ', 'banner_videos/world.mp4'],
        'technology': ['Technology', ' ', 'banner_videos/technology.mp4'],
        'energy': ['Energy / Environment', ' ', 'banner_videos/energy.mp4'],
        'economy': ['Economy / Business', ' ', 'banner_videos/economy.mp4'],
        'science': ['Science / Religion', ' ', 'banner_videos/science.mp4'],
        'health': ['Health', ' ', 'banner_videos/health.mp4']
    }
    return render_template(
        'main/index.html', 
        section=section,
        title=title_dict[section],
        banner=banner_dict[section]
    )


@bp.route('/article/<slug>', methods=['GET', 'POST'])
def view_article(slug):
    article = Article.query.filter_by(slug=slug).first_or_404()
    section_dict = {
        1: 'U.S. Politics',
        2: 'World News',
        3: 'Technology',
        4: 'Energy / Environment',
        5: 'Economy / Business',
        6: 'Science / Religion',
        7: 'Health'
    }
    section = section_dict[int(article.section)]
    comments = Comment.query.filter_by(article_id=article.id).order_by(Comment.timestamp.desc()).all()

    if request.method == 'POST':
        comment = Comment()
        comment.article_id = article.id
        comment.user_id = current_user.id
        comment.comment = str(request.form.get('comment'))
        comment.timestamp = datetime.datetime.utcnow()
        db.session.add(comment)
        db.session.commit()
        flash("Your comment was posted!")
        return redirect(url_for('main.view_article', slug=article.slug))
    return render_template(
        'main/view_article.html',
        title=article.title,
        article=article,
        section=section,
        comments=comments
    )


@bp.route('/robots.txt')
def robots():
    return redirect(url_for('static', filename='robots.txt'))


@bp.route('/sitemap.xml')
def sitemap():
    return redirect(url_for('static', filename='sitemap.xml'))


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')