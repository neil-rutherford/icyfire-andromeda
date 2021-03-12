from app.blog import bp
from flask import flash, redirect, url_for, abort, render_template

@bp.route('/blog')
def blog():
    return render_template('blog/blog.html', title='Survival Blog')


@bp.route('/blog/<filename>')
def article(filename):
    try:
        return render_template(
            'blog/articles/{}.html',
            title=filename.replace('-', ' ').capitalize()
        )
    except:
        abort(404)