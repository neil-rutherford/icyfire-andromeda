from flask import request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user
from app.models import Article
from app import db
from app.main import bp
import datetime

@bp.route('/contribute/customize/article', methods=['GET', 'POST'])
@login_required
def customize_article():
    if not current_user.check_subscription():
        flash("You must be a Patriot to contribute.")
        return redirect(url_for("auth.settings"))
    if request.method == 'POST':
        article = Article()
        article.user_id = current_user.id
        article.image_file_path = request.form.get('image_file_path')
        article.title = request.form['title']
        article.slug = str(request.form['title']).lower().replace(' ', '-')
        article.description = request.form['description']
        article.section = int(request.form['section'])
        article.tags = request.form['tags']
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('main.write_article', article_id=article.id))
    return render_template(
        'main/customize_article.html',
        title='Customize your article'
    )


@bp.route('/contribute/write/article/<int:article_id>', methods=['POST', 'GET'])
@login_required
def write_article(article_id):
    if not current_user.check_subscription():
        flash("You must be a Patriot to contribute.")
        return redirect(url_for("auth.settings"))
    article = Article.query.filter_by(id=article_id).first()
    if article is None:
        flash("Can't find your article. Please try again.")
        return redirect(url_for('main.customize_article'))
    if request.method == 'POST':
        article.body = request.form.get('body')
        article.timestamp = datetime.datetime.utcnow()
        db.session.add(article)
        db.session.commit()
        flash("Your article is live!")
        return redirect(url_for('main.view_article', slug=article.slug))
    return render_template(
        'main/write_article.html',
        title='Write your article',
        article=article
    )