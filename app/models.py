from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import jwt
import os
import datetime
from time import time


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class Article(db.Model):

    __tablename__ = 'article'
    __searchable__ = ['title', 'description', 'body']

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_file_path = db.Column(db.String(250))
    slug = db.Column(db.String(254), index=True, unique=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    section = db.Column(db.Integer) # 1: Politics, 2: World, 3: Technology, 4: Energy/Environment, 5: Economy/Business, 6: Science/Religion, 7: Health
    tags = db.Column(db.String(300)) # Delimiter: ", "
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    logs = db.relationship('ActivityLog', backref='article', lazy='dynamic')
    shares = db.relationship('Share', backref='article', lazy='dynamic')

    def __repr__(self):
        return "<Article {}>".format(self.slug)


class Comment(db.Model):

    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Comment {}>".format(self.timestamp)


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    anonymous_uuid = db.Column(db.String(36))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    share_id = db.Column(db.Integer, db.ForeignKey('share.id'))
    ip_address = db.Column(db.String(15))
    referrer_page = db.Column(db.String(255))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<ActivityLog {}>".format(self.timestamp)


class Share(db.Model):

    __tablename__ = 'share'

    id = db.Column(db.Integer, primary_key=True)
    share_uuid = db.Column(db.String(36))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    anonymous_uuid = db.Column(db.String(36))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(15))
    network = db.Column(db.Integer) # 1: Facebook, 2: Twitter, 3: Tumblr, 4: LinkedIn
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Share {}>".format(self.timestamp)


class User(UserMixin, db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    stripe_customer_id = db.Column(db.String(300), unique=True)
    expires_on = db.Column(db.DateTime)
    username = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(100))
    dob = db.Column(db.DateTime)
    gender = db.Column(db.Integer) # 1: Male, 2: Female
    email_opt_in = db.Column(db.Boolean)
    is_verified = db.Column(db.Boolean)
    profile_pic = db.Column(db.String(300))
    coins = db.Column(db.Integer)
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    messages = db.relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.from_user_id')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password(self, expires_in=600):
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, os.environ['SECRET_KEY'], algorithm='HS256')
    
    def get_verify_email(self, expires_in=600):
        return jwt.encode({'verify_email': self.email, 'exp': time() + expires_in}, os.environ['SECRET_KEY'], algorithm='HS256')

    def get_access_token(self, consumer_key, consumer_secret, crud):
        return jwt.encode({'access_token': self.email,'consumer_key': consumer_key, 'consumer_secret': consumer_secret, 'crud': crud}, os.environ['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.filter_by(id=id).first()
    
    @staticmethod
    def verify_verify_email_token(token):
        try:
            email = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['verify_email']
        except:
            return
        return User.query.filter_by(email=email).first()

    @staticmethod
    def verify_access_token(token):
        try:
            email = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['access_token']
        except:
            return
        return {
            'consumer_key': jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['consumer_key'],
            'consumer_secret': jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['consumer_secret'],
            'user': User.query.filter_by(email=email).first(),
            'crud': jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])['crud']
        }
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_articles(self):
        followed = Article.query.join(
            followers, (followers.c.followed_id == Article.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Article.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Article.timestamp.desc())

    def followed_comments(self):
        followed = Comment.query.join(
            followers, (followers.c.followed_id == Comment.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Comment.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Comment.timestamp.desc())

    def unread_message_count(self):
        unread = Message.query.filter(
            Message.to_user_id == self.id,
            Message.seen_timestamp == None
        ).all()
        return len(unread)

    def check_subscription(self):
        '''
        Returns True if the user has an active subscription.
        '''
        return datetime.datetime.utcnow() < self.expires_on


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply_to = db.Column(db.Integer, db.ForeignKey('message.id'))
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(50))
    body = db.Column(db.String(300))
    sent_timestamp = db.Column(db.DateTime)
    seen_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Message {}>".format(self.subject)


class ApiClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_approved = db.Column(db.Boolean)
    is_blacklist = db.Column(db.Boolean)
    consumer_key = db.Column(db.String(255))
    consumer_secret = db.Column(db.String(255))
    stripe_customer_id = db.Column(db.String(300), unique=True)
    expires_on = db.Column(db.DateTime)
    is_articles = db.Column(db.Boolean)
    is_comments = db.Column(db.Boolean)
    is_logs = db.Column(db.Boolean)
    is_shares = db.Column(db.Boolean)
    is_users = db.Column(db.Boolean)
    is_connections = db.Column(db.Boolean)
    is_messages = db.Column(db.Boolean)
    is_api = db.Column(db.Boolean)
    company_name = db.Column(db.String(300))
    contact_name = db.Column(db.String(300))
    phone_number = db.Column(db.String(14))
    email = db.Column(db.String(254))
    use_case = db.Column(db.Text)
    developer_platform = db.Column(db.String(100))
    monetization_model = db.Column(db.Text)
    permission_justification = db.Column(db.Text)

    def __repr__(self):
        return "<ApiClient {}>".format(self.consumer_key)
    
    def check_subscription(self):
        return self.expires_on > datetime.datetime.utcnow()


@login.user_loader
def load_user(id):
    return User.query.get(int(id))