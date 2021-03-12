from app.help import bp
from flask import render_template

@bp.route('/legal/privacy-policy')
def privacy_policy():
    return render_template('help/legal/privacy_policy.html', title='Privacy Policy')


@bp.route('/legal/terms-of-service')
def terms_of_service():
    return render_template('help/legal/terms_of_service.html', title='Terms of Service')


@bp.route('/legal/cookies')
def cookies():
    return render_template('help/legal/cookies.html', title="Cookie Policy")


@bp.route('/legal/disclaimers')
def disclaimers():
    return render_template('help/legal/disclaimers.html', title="Disclaimers")


@bp.route('/legal/api-terms-of-use')
def api_terms_of_use():
    return render_template('help/legal/api_terms_of_use.html', title="API Terms of Use")


@bp.route('/legal/content-policy')
def content_policy():
    return render_template('help/legal/content_policy.html', title="Content Policy")