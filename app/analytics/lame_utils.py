from flask_login import current_user
from app.models import Article, Comment

def get_all_articles():
    if current_user.is_anonymous:
        all_articles = set(Article.query.filter_by().order_by(Article.timestamp.desc()).all())
        return list(all_articles)
        
    else:
        following = current_user.followed_articles()
        rest = Article.query.filter_by().order_by(Article.timestamp.desc()).all()
        all_articles = set()
        for x in following:
            all_articles.add(x)
        for x in rest:
            all_articles.add(x)
        return list(all_articles)


def get_section_articles(section):
    section = int(section)
    if current_user.is_anonymous:
        all_articles = set(Article.query.filter_by(section=section).order_by(Article.timestamp.desc()).all())
        return list(all_articles)
    else:
        all_articles = set()
        following = current_user.followed_articles()
        for x in following:
            if x.section == section:
                all_articles.add(x)
        rest = Article.query.filter_by(section=section).order_by(Article.timestamp.desc()).all()
        for x in rest:
            all_articles.add(x)
        
        return list(all_articles)