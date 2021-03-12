from app.api import bp
from flask import Response, request
from app.models import Article, Comment, ActivityLog, Share, User, Message, ApiClient
import json
from app.api.utils import verify_client, get_user
from app.payment.utils import cancel_subscription
import datetime
import uuid
from app import db


@bp.route('/_api/get/articles', methods=['POST'])
def get_article_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='articles'
    )
    if auth[0] is True:
        articles = Article.query.filter_by().order_by(Article.timestamp.desc()).all()[0:25]
        data_list = []
        for x in articles:
            data_dict = {
                'id': x.id,
                'title': x.title,
                'description': x.description,
                'timestamp': x.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'comments': len(x.comments.all()),
                'logs': len(x.logs.all()),
                'shares': len(x.shares.all())
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200, 
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )
    

@bp.route('/_api/post/articles', methods=['POST'])
def post_article_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='articles'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        if user.check_subscription:
            try:
                article = Article()
                article.user_id = user.id
                article.image_file_path = str(request.form.get('image_file_path'))
                article.title = str(request.form.get('title'))
                article.slug = article.title.lower().replace(' ', '-')
                article.description = str(request.form.get('description'))
                article.section = int(request.form.get('section'))
                article.tags = str(request.form.get('tags'))
                article.body = str(request.form.get('body'))
                article.timestamp = datetime.datetime.utcnow()
                db.session.add(article)
                db.session.commit()
                return Response(status=201, response="SUCCESS: Article {} created.".format(article.slug))
            except Exception as e:
                return Response(status=400, response="ERROR: {}".format(e))
        else:
            return Response(status=403, response="ERROR: Account does not have adequate permissions to post an article.")
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/article/<int:article_id>', methods=['POST'])
def get_article_resource(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='articles'
    )
    if auth[0] is True:
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        data_dict = {
            'id': article.id,
            'user_id': article.user_id,
            'image_file_path': article.image_file_path,
            'slug': article.slug,
            'title': article.title,
            'description': article.description,
            'section': article.section,
            'tags': article.tags,
            'body': article.body,
            'timestamp': article.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'comments': len(article.comments.all()),
            'logs': len(article.logs.all()),
            'shares': len(article.shares.all())
        }
        return Response(
            status=200, 
            response=json.dumps(data_dict), 
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/delete/article/<int:article_id>', methods=['POST'])
def delete_article_resource(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='articles'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        if article.user_id != user.id:
            return Response(status=403, response="ERROR: Insufficient permissions, resource access denied.")
        for x in article.comments:
            db.session.delete(x)
        for x in article.logs:
            db.session.delete(x)
        for x in article.shares:
            db.session.delete(x)
        db.session.delete(article)
        db.session.commit()
        return Response(status=204, response="SUCCESS: Article {} deleted.".format(article.slug))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/comments/<int:article_id>', methods=['POST'])
def get_comment_collection(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='comments'
    )
    if auth[0] is True:
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        comments = Comment.query.filter_by(article_id=article.id).order_by(Comment.timestamp.desc()).all()
        data_list = []
        for x in comments:
            data_dict = {
                'id': x.id,
                'timestamp': x.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200, 
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/comments/<int:article_id>', methods=['POST'])
def post_comment_collection(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='comments'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        try:
            comment = Comment()
            comment.article_id = article.id
            comment.user_id = user.id
            comment.comment = str(request.form.get('comment'))
            comment.timestamp = datetime.datetime.utcnow()
            db.session.add(comment)
            db.session.commit()
            return Response(status=201, response="SUCCESS: Comment {} created.".format(comment.id))
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/comment/<int:comment_id>', methods=['POST'])
def get_comment_resource(comment_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='comments'
    )
    if auth[0] is True:
        comment = Comment.query.filter_by(id=comment_id).first()
        if comment is None:
            return Response(status=404, response="ERROR: Comment {} not found.".format(comment_id))
        data_dict = {
            'id': comment.id,
            'article_id': comment.article_id,
            'user_id': comment.user_id,
            'comment': comment.comment,
            'timestamp': comment.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200, 
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/delete/comment/<int:comment_id>', methods=['POST'])
def delete_comment_resource(comment_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='comments'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        comment = Comment.query.filter_by(id=comment_id).first()
        if comment is None:
            return Response(status=404, response="ERROR: Comment {} not found.".format(comment_id))
        if comment.user_id != user.id:
            return Response(status=403, response="ERROR: Insufficient permissions, resource access denied.")
        try:
            db.session.delete(comment)
            db.session.commit()
            return Response(status=204, response="SUCCESS: Comment {} successfully deleted.".format(comment_id))
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/logs/<int:article_id>', methods=['POST'])
def get_log_collection(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='logs'
    )
    if auth[0] is True:
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        logs = ActivityLog.query.filter_by(article_id=article_id).order_by(ActivityLog.timestamp.desc()).all()
        data_list = []
        for x in logs:
            data_dict = {
                'id': x.id,
                'timestamp': x.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200, 
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/log/<int:activity_log_id>', methods=['POST'])
def get_log_resource(activity_log_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='logs'
    )
    if auth[0] is True:
        log = ActivityLog.query.filter_by(id=activity_log_id).first()
        if log is None:
            return Response(status=404, response="ERROR: Log {} not found.".format(activity_log_id))
        data_dict = {
            'id': log.id,
            'article_id': log.article_id,
            'anonymous_uuid': log.anonymous_uuid,
            'user_id': log.user_id,
            'share_id': log.share_id,
            'ip_address': log.ip_address,
            'referrer_page': log.referrer_page,
            'user_agent': log.user_agent,
            'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/shares/<int:article_id>', methods=['POST'])
def get_share_collection(article_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='shares'
    )
    if auth[0] is True:
        article = Article.query.filter_by(id=article_id).first()
        if article is None:
            return Response(status=404, response="ERROR: Article {} not found.".format(article_id))
        shares = Share.query.filter_by(article_id=article.id).order_by(Share.timestamp.desc()).all()
        data_list = []
        for x in shares:
            data_dict = {
                'id': x.id,
                'share_uuid': x.share_uuid,
                'article_id': x.article_id,
                'timestamp': x.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/share/<int:share_id>', methods=['POST'])
def get_share_resource(share_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='shares'
    )
    if auth[0] is True:
        share = Share.query.filter_by(id=share_id).first()
        if share is None:
            return Response(status=404, response="ERROR: Share {} not found.".format(share_id))
        data_dict = {
            'id': share.id,
            'share_uuid': share.share_uuid,
            'article_id': share.article_id,
            'anonymous_uuid': share.anonymous_uuid,
            'user_id': share.user_id,
            'ip_address': share.ip_address,
            'network': share.network,
            'timestamp': share.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/users', methods=['POST'])
def get_user_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='users'
    )
    if auth[0] is True:
        users = User.query.filter_by().order_by(User.id.desc()).all()
        data_list = []
        for x in users:
            data_dict = {
                'id': x.id,
                'username': x.username,
                'status': x.status,
                'is_patriot': x.check_subscription()
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/users', methods=['POST'])
def post_user_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='users'
    )
    if auth[0] is True:
        try:
            user = User()
            user.email = str(request.form.get('email'))
            user.password_hash = user.set_password(request.form.get('password'))
            user.stripe_customer_id = None
            user.expires_on = datetime.datetime(1970, 1, 1)
            user.username = str(request.form.get('username'))
            user.status = None
            user.dob = datetime.datetime(int(request.form.get('yob')), 1, 1)
            user.gender = int(request.form.get('gender'))
            user.email_opt_in = False
            user.is_verified = False
            user.profile_pic = "https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png"
            user.coins = 0
            db.session.add(user)
            db.session.commit()
            return Response(status=201, response="SUCCESS: User {} created.".format(user.username))
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/user/<int:user_id>', methods=['POST'])
def get_user_resource(user_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='users'
    )
    if auth[0] is True:
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response(status=404, response="ERROR: User {} not found.".format(user_id))
        data_dict = {
            'id': user.id,
            'email': user.email,
            'expires_on': user.expires_on.strftime("%Y-%m-%d %H:%M:%S"),
            'username': user.username,
            'status': user.status,
            'dob': user.dob.strftime("%Y-%m-%d %H:%M:%S"),
            'gender': user.gender,
            'email_opt_in': user.email_opt_in,
            'is_verified': user.is_verified,
            'profile_pic': user.profile_pic,
            'coins': user.coins
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/delete/user/<int:user_id>', methods=['POST'])
def delete_user_resource(user_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='users'
    )
    if auth[0] is True:
        current_user = get_user(consumer_key=request.form.get('consumer_key'))
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response(status=404, response="ERROR: User {} not found.".format(user_id))
        if user.id != current_user.id:
            return Response(status=403, response="ERROR: Insufficient permissions, resource access denied.")
        try:
            cancel_subscription(entity_type='user', entity_id=user.id)
            user.email = None
            user.password_hash = None
            user.expires_on = datetime.datetime.utcnow()
            user.username = '[DELETED]'
            user.status = None
            user.dob = None
            user.gender = None
            user.email_opt_in = False
            user.is_verified = False
            user.profile_pic = 'https://iptc.org/wp-content/uploads/2018/05/avatar-anonymous-300x300.png'
            user.coins = 0
            db.session.commit()
            return Response(
                status=204,
                response='SUCCESS: User {} successfully deleted.'.format(user_id)
            )
        except Exception as e:
            return Response(
                status=400,
                response="ERROR: {}".format(e)
            )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/followers/<int:user_id>', methods=['POST'])
def get_follower_collection(user_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='connections'
    )
    if auth[0] is True:
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response(status=404, response="ERROR: User {} not found.".format(user_id))
        followers = user.followers
        data_list = []
        for x in followers:
            data_dict = {
                'id': x.id,
                'username': x.username,
                'status': x.status,
                'is_patriot': x.check_subscription()
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/followers/<int:user_id>', methods=['POST'])
def post_follower_collection(user_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='connections'
    )
    if auth[0] is True:
        current_user = get_user(consumer_key=request.form.get('consumer_key'))
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response(status=404, response="ERROR: User {} not found.".format(user_id))
        current_user.follow(user)
        db.session.commit()
        return Response(
            status=200,
            response="SUCCESS: You are now following user {}.".format(user_id)
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/following/<int:user_id>', methods=['POST'])
def get_following_collection(user_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='connections'
    )
    if auth[0] is True:
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return Response(status=404, response="ERROR: User {} not found.".format(user_id))
        following = user.followed
        data_list = []
        for x in following:
            data_dict = {
                'id': x.id,
                'username': x.username,
                'status': x.status,
                'is_patriot': x.check_subscription()
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/connection/<int:user1_id>&<int:user2_id>', methods=['POST'])
def get_connection_resource(user1_id, user2_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='connections'
    )
    if auth[0] is True:
        user1 = User.query.filter_by(id=user1_id).first()
        user2 = User.query.filter_by(id=user2_id).first()
        if user1 is None:
            return Response(status=404, response="ERROR: User 1 not found.")
        if user2 is None:
            return Response(status=404, response='ERROR: User 2 not found.')
        data_dict = {
            'user1_follows_user2': user1.is_following(user2),
            'user2_follows_user1': user2.is_following(user1),
            'user1_messages_user2': len(Message.query.filter(Message.from_user_id == user1.id, Message.to_user_id == user2.id).all()),
            'user2_messages_user1': len(Message.query.filter(Message.from_user_id == user2.id, Message.to_user_id == user1.id).all())
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/messages', methods=["POST"])
def get_message_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='messages'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        messages = Message.query.filter_by(to_user_id=user.id).order_by(Message.sent_timestamp.desc()).all()
        data_list = []
        for x in messages:
            data_dict = {
                'id': x.id,
                'from_user_id': x.from_user_id,
                'to_user_id': x.to_user_id,
                'subject': x.subject,
                'sent_timestamp': x.sent_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'seen_timestamp': x.seen_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/messages', methods=["POST"])
def post_message_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='messages'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        try:
            message = Message()
            if request.form.get('reply_to') is not None:
                message.reply_to = int(request.form.get('reply_to'))
            else:
                message.reply_to = None
            message.from_user_id = user.id
            message.to_user_id = int(request.form.get('to_user_id'))
            message.subject = str(request.form.get('subject'))
            message.body = str(request.form.get('body'))
            message.sent_timestamp = datetime.datetime.utcnow()
            message.seen_timestamp = None
            db.session.add(message)
            db.session.commit()
            return Response(
                status=201,
                response='SUCCESS: Message sent to {}'.format(request.form.get('to_user_id'))
            )
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/message/<int:message_id>', methods=["POST"])
def get_message_resource(message_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='messages'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        message = Message.query.filter_by(id=message_id).first()
        if message is None:
            return Response(status=404, response='ERROR: Message {} not found.'.format(message_id))
        if message.from_user_id != user.id or message.to_user_id != user.id:
            return Response(status=403, response="ERROR: Insufficient permissions, resource access denied.")
        data_dict = {
            'id': message.id,
            'reply_to': message.reply_to,
            'from_user_id': message.from_user_id,
            'to_user_id': message.to_user_id,
            'subject': message.subject,
            'body': message.body,
            'sent_timestamp': message.sent_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'seen_timestamp': message.seen_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/delete/message/<int:message_id>', methods=["POST"])
def delete_message_resource(message_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='messages'
    )
    if auth[0] is True:
        user = get_user(consumer_key=request.form.get('consumer_key'))
        message = Message.query.filter_by(id=message_id).first()
        if message is None:
            return Response(status=404, response='ERROR: Message {} not found.'.format(message_id))
        if message.from_user_id != user.id or message.to_user_id != user.id:
            return Response(status=403, response="ERROR: Insufficient permissions, resource access denied.")
        db.session.delete(message)
        db.session.commit()
        return Response(
            status=204,
            response="SUCCESS: Message {} deleted.".format(message_id)
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/clients', methods=['POST'])
def get_client_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='api'
    )
    if auth[0] is True:
        clients = ApiClient.query.filter_by().order_by(ApiClient.id.desc()).all()
        data_list = []
        for x in clients:
            data_dict = {
                'id': x.id,
                'user_id': x.user_id,
                'is_approved': x.is_approved,
                'is_blacklist': x.is_blacklist
            }
            data_list.append(data_dict)
        data_json = json.dumps(data_list)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/clients', methods=['POST'])
def post_client_collection():
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='api'
    )
    if auth[0] is True:
        try:
            client = ApiClient()
            client.user_id = int(request.form.get('user_id'))
            client.is_approved = False
            client.is_blacklist = False
            client.consumer_key = str(uuid.uuid4())
            client.consumer_secret = str(uuid.uuid4())
            client.stripe_customer_id = None
            client.expires_on = datetime.datetime(1970,1,1)
            client.is_articles = bool(request.form.get('is_articles'))
            client.is_comments = bool(request.form.get('is_comments'))
            client.is_logs = bool(request.form.get('is_logs'))
            client.is_shares = bool(request.form.get('is_shares'))
            client.is_users = bool(request.form.get('is_users'))
            client.is_connections = bool(request.form.get('is_connections'))
            client.is_messages = bool(request.form.get('is_messages'))
            client.is_api = bool(request.form.get('is_api'))
            client.company_name = str(request.form.get('company_name'))
            client.contact_name = str(request.form.get('contact_name'))
            client.phone_number = str(request.form.get('phone_number'))
            client.email = str(request.form.get('email'))
            client.use_case = str(request.form.get('use_case'))
            client.developer_platform = str(request.form.get('developer_platform'))
            client.monetization_model = str(request.form.get('monetization_model'))
            client.permission_justification = str(request.form.get('permission_justification'))
            db.session.add(client)
            db.session.commit()
            return Response(
                status=201,
                response='SUCCESS: API client application {} created.'.format(client.id)
            )
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/get/client/<int:api_client_id>', methods=['POST'])
def get_client_resource(api_client_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='api'
    )
    if auth[0] is True:
        client = ApiClient.query.filter_by(id=api_client_id).first()
        if client is None:
            return Response(status=404, response="ERROR: Client {} not found.".format(api_client_id))
        data_dict = {
            'id': client.id,
            'user_id': client.user_id,
            'is_approved': client.is_approved,
            'is_blacklist': client.is_blacklist,
            'expires_on': client.expires_on.strftime("%Y-%m-%d %H:%M:%S"),
            'is_articles': client.is_articles,
            'is_comments': client.is_comments,
            'is_logs': client.is_logs,
            'is_shares': client.is_shares,
            'is_users': client.is_users,
            'is_connections': client.is_connections,
            'is_messages': client.is_messages,
            'is_api': client.is_api,
            'company_name': client.company_name,
            'contact_name': client.contact_name,
            'phone_number': client.phone_number,
            'email': client.email,
            'use_case': client.use_case,
            'developer_platform': client.developer_platform,
            'monetization_model': client.monetization_model,
            'permission_justification': client.permission_justification
        }
        data_json = json.dumps(data_dict)
        return Response(
            status=200,
            response=data_json,
            mimetype='application/json'
        )
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )


@bp.route('/_api/post/client/<int:api_client_id>', methods=['POST'])
def post_client_resource(api_client_id):
    auth = verify_client(
        consumer_key=request.form.get('consumer_key'),
        consumer_secret=request.form.get('consumer_secret'),
        permission='api'
    )
    if auth[0] is True:
        client = ApiClient.query.filter_by(id=api_client_id).first()
        if client is None:
            return Response(status=404, response="ERROR: Client {} not found.".format(api_client_id))
        try:
            client.is_approved = bool(request.form.get('is_approved'))
            client.is_blacklist = bool(request.form.get('is_blacklist'))
            client.is_articles = bool(request.form.get('is_articles'))
            client.is_comments = bool(request.form.get('is_comments'))
            client.is_logs = bool(request.form.get('is_logs'))
            client.is_shares = bool(request.form.get('is_shares'))
            client.is_users = bool(request.form.get('is_users'))
            client.is_connections = bool(request.form.get('is_connections'))
            client.is_messages = bool(request.form.get('is_messages'))
            client.is_api = bool(request.form.get('is_api'))
            db.session.commit()
            return Response(status=200, response="SUCCESS: API Client {} updated.".format(client.id))
        except Exception as e:
            return Response(status=400, response="ERROR: {}".format(e))
    else:
        return Response(
            status=auth[1],
            response="ERROR: {}".format(auth[2])
        )