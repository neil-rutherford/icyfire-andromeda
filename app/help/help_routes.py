from app.help import bp
from flask import render_template, abort

@bp.route('/about')
def about():
    return render_template('help/about.html', title='About Us')


@bp.route('/careers')
def careers():
    return render_template('help/careers.html', title='Careers')


@bp.route('/contact')
def contact():
    return render_template('help/contact.html', title='Contact Us')


@bp.route('/help')
def help():
    return render_template('help/help.html', title='Help Topics')


@bp.route('/help/<topic>')
def help_topic(topic):
    #try:
    return render_template(
            'help/help/{}.html'.format(topic),
            title='{} Help'.format(topic.capitalize())
        )
    #except:
        #abort(404)


@bp.route('/help/<topic>/<title>')
def help_title(topic, title):
    title_dict = {
        'change_profile_pic': 'Change my profile picture',
        'create_account': 'Create an account',
        'delete_account': 'Delete my account',
        'log_in': 'Log in',
        'reset_password': 'Reset my password',
        'set_status': 'Set my status',
        'subscribe_unsubscribe': 'Subscribe to / unsubscribe from emails',
        'subscribe_patriot': 'Subscribe to Patriot Tier',
        'unsubscribe_patriot': 'Unsubscribe from Patriot Tier',
        'verify_email': 'Verify my email',

        'comment_article': 'Comment on an article',
        'follow_user': 'Follow a user',
        'gift_coins': 'Send coins to friends',
        'inbox': 'Check my inbox',
        'redeem_coins': 'Redeem coins for Patriot Tier subscription',
        'send_message': 'Send a message',
        'unfollow_user': 'Unfollow a user',
        'write_article': 'Write an article',
        
        'create_an_app': 'Create an app',
        'delete_article': 'Delete an article',
        'delete_comment': 'Delete a comment',
        'delete_message': "Delete a message",
        'delete_user': "Delete your account",
        'get_article': "Get information about an article",
        'get_articles': "Get a list of articles",
        'get_client': "Get more information about an app",
        'get_clients': "Get a list of apps",
        'get_comment': "Get information about a comment",
        'get_comments': "Get comments for an article",
        'get_connection': "Get information about a relationship between two users",
        'get_followers': "Get a list of who follows a user",
        'get_following': "Get a list of who a user is following",
        'get_log': "Get information about a log",
        'get_logs': "Get a list of logs",
        'get_message': "Get information about a message",
        'get_messages': "Get a list of your messages",
        'get_share': "Get information about a share",
        'get_shares': "Get a list of shares",
        'get_user': "Get information about a user",
        'get_users': "Get a list of users",
        'post_articles': "Publish an article",
        'post_client': "Modify an app's permissions",
        'post_clients': 'Create an app',
        'post_comments': 'Post a comment',
        'post_followers': 'Follow a user',
        'post_messages': 'Send a message',
        'post_users': 'Create a user account',
        'subscribe_to_premium_api': 'Subscribe to Premium API',
        'unsubscribe_from_premium_api': 'Unsubscribe from Premium API'
    }
    #try:
    return render_template(
            'help/help/{}/{}.html'.format(topic, title),
            title=title_dict[title]
        )
    #except:
        #abort(404)