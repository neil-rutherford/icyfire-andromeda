from app.models import *
import datetime
from flask_login import current_user
from flask import *
import pickle
import numpy

def get_user_tendencies():
    '''
    Users interact with content in different ways. 
    This function looks at the distribution of user interactions over the past three weeks, then uses that to populate 10 article slots.

    :rtype:     Dictionary
    '''
    if current_user.is_anonymous is True:
        anonymous_uuid = session['anonymous_uuid']
        views = View.query.filter(
            View.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            View.anonymous_uuid == anonymous_uuid
        ).all()
        comments = []
        shares = Share.query.filter(
            Share.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            Share.anonymous_uuid == anonymous_uuid
        ).all()
        referrals = Referral.query.filter(
            Referral.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            Referral.anonymous_uuid == anonymous_uuid
        ).all()
    else:
        user_id = current_user.id
        views = View.query.filter(
            View.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            View.user_id == user_id
        ).all()
        comments = Comment.query.filter(
            Comment.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            Comment.user_id == user_id
        ).all()
        shares = Share.query.filter(
            Share.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            Share.user_id == user_id
        ).all()
        referrals = Referral.query.filter(
            Referral.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
            Referral.user_id == user_id
        ).all()
    total = len(views) + len(comments) + len(shares) + len(referrals)
    view = int((len(views) / total)*10)
    comment = int((len(comments) / total)*10)
    share = int((len(shares) / total)*10)
    referral = int((len(referrals) / total)*10)
    return {
        'referrals': referral,
        'shares': share,
        'comments': comment,
        'views': view,
        'news': 10 - (view + comment + share + referral)
    }


def get_user_history(interaction_type):
    '''
    Given a type of interaction, what articles has the user interacted with in the past three weeks?

    :param interaction_type:    ["views", "comments", "shares", "referrals"], as a string.
    :rtype:                     Set
    :onerror:                   Raises ValueError if `interaction_type` not allowed.
    '''
    article_list = []
    if current_user.is_anonymous is True:
        anonymous_uuid = session['anonymous_uuid']

    if interaction_type == 'views':
        if current_user.is_anonymous:
            views = View.query.filter(
                View.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                View.anonymous_uuid == anonymous_uuid
            ).all()
        else:
            views = View.query.filter(
                View.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                View.user_id == current_user.id
            ).all()
        for view in views:
            x = Article.query.filter_by(id=view.article_id).first()
            article_list.append(x)

    elif interaction_type == 'comments':
        if current_user.is_anonymous:
            comments = []
        else:
            comments = Comment.query.filter(
                Comment.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                Comment.user_id == current_user.id
            ).all()
        for comment in comments:
            x = Article.query.filter_by(id=comment.article_id).first()
            article_list.append(x)

    elif interaction_type == 'shares':
        if current_user.is_anonymous:
            shares = Share.query.filter(
                Share.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                Share.anonymous_uuid == anonymous_uuid
            ).all()
        else:
            shares = Share.query.filter(
                Share.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                Share.user_id == current_user.id
            ).all()
        for share in shares:
            x = Article.query.filter_by(id=share.article_id).first()
            article_list.append(x)

    elif interaction_type == 'referrals':
        if current_user.is_anonymous:
            referrals = Referral.query.filter(
                Referral.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                Referral.anonymous_uuid == anonymous_uuid
            ).all()
        else:
            referrals = Referral.query.filter(
                Referral.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=3),
                Referral.user_id == current_user.id
            ).all()
        for referral in referrals:
            x = Article.query.filter_by(id=referral.article_id).first()
            article_list.append(x)

    else:
        raise ValueError("Accepted interaction types: views, comments, shares, referrals")

    return set(article_list)


def get_user_interests(user_history):
    '''
    Given a user's history, what tags are they most interested in?

    :param user_history:    Set of article objects.
    :rtype:                 Set
    '''
    tag_list = []
    for article in user_history:
        tags = str(article.tags).split(', ')
        for tag in tags:
            tag_list.append(tag)
    return set(tag_list)


def gauge_user_interaction_probability(article_list, user_interests):
    '''
    Given the tags the user is interested in, what is the probability they would like a given article in a list?
    (Uses GloVe Twitter-25 dataset to calculate tag similarity, then takes the average.)

    :param article_list:        A list of articles objects, as a list.
    :param user_interests:      User tag interests, as a set.
    :rtype:                     Dictionary with `article.id` as the key
    '''
    data_dict = {}
    for article in article_list:
        overall_matches = []
        model = pickle.load(open('./app/analytics/glove_vectors.pickle', 'rb'))
        tags = str(article.tags).split(', ')
        for x in tags:
            tag_matches = []
            for y in user_interests:
                tag_matches.append(model.similarity(x, y))
            overall_matches.append(sum(tag_matches) / len(tag_matches))
        data_dict[article.id] = {'user': sum(overall_matches) / len(overall_matches)}
    return data_dict


def get_recommendation_score(data_dict, interaction_type):
    '''
    This function calculates the z-score (http://www.comfsm.fm/~dleeling/statistics/s63/zscore.html) for a given interaction for a given list of articles.
    The z-score measures the relative score within the dataset (-2 is very below average, 0 is average, +2 is very above average). In other words, how is the community interacting with this?
    The z-score is then multiplied by the user's interaction probability to get a recommendation score.

    In other words: Given community engagement and individual user preferences, should we recommend this article?

    :param data_dict:           Dictionary with `article_ids` as keys and user interaction probabilities as values.
    :param interaction_type:    ["views", "comments", "shares", "referrals"], as a string.
    :rtype:                     Sorted list of data_dict['combined'] values in descending order
    :onerror:                   Raises a ValueError if `interaction_type` not accepted.
    '''
    interaction_list = []
    key_list = []
    if interaction_type == 'views':
        for x in data_dict:
            key_list.append(x)
            article = Article.query.filter_by(id=x).first()
            interaction_list.append(len(article.views))
    elif interaction_type == 'comments':
        for x in data_dict:
            key_list.append(x)
            article = Article.query.filter_by(id=x).first()
            interaction_list.append(len(article.comments))
    elif interaction_type == 'shares':
        for x in data_dict:
            key_list.append(x)
            article = Article.query.filter_by(id=x).first()
            interaction_list.append(len(article.shares))
    elif interaction_type == 'referrals':
        for x in data_dict:
            key_list.append(x)
            article = Article.query.filter_by(id=x).first()
            interaction_list.append(len(article.referrals))
    else:
        raise ValueError("Accepted interaction types: views, comments, shares, referrals")
    
    standard_deviation = numpy.std(interaction_list)
    mean = sum(interaction_list) / len(interaction_list)
    
    for x in key_list:
        for y in interaction_list:
            data_dict[x]['community'] = (y - mean) / standard_deviation
            data_dict[x]['combined'] = data_dict[x]['user'] * data_dict[x]['community']
    
    return sorted(data_dict.items(), key=lambda x: x[1]['combined'], reverse=True)


def get_unread_articles(section=None):
    '''
    Returns a list of articles from the past week that the user has not yet read.

    :param section:     Optional parameter specifying a `article.section` filter, as an integer. (Refer to docs for section codes.)
    :rtype:             List of article objects
    '''
    if section is None:
        articles = Article.query.filter(
            Article.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=1)
        ).all()
    else:
        articles = Article.query.filter(
            Article.timestamp >= datetime.datetime.utcnow() - datetime.timedelta(weeks=1),
            Article.section == int(section)
        ).all()

    views = get_user_history(interaction_type='views')
    comments = get_user_history(interaction_type='comments')
    shares = get_user_history(interaction_type='shares')
    referrals = get_user_history(interaction_type='referrals')
    all_history = views | comments | shares | referrals

    for x in all_history:
        if x in articles:
            articles.remove(x)

    return articles


def recommend_article(article_list, desired_interaction):
    allowed = ['views', 'comments', 'shares', 'referrals']
    if desired_interaction in allowed:
        user_history = get_user_history(interaction_type=desired_interaction)
        user_interests = get_user_interests(user_history=user_history)
        data_dict = gauge_user_interaction_probability(article_list=article_list, user_interests=user_interests)
        recommendation_list = get_recommendation_score(data_dict=data_dict, interaction_type=desired_interaction)
        return Article.query.filter_by(id=recommendation_list[0][0]).first()
    else:
        articles = Article.query.filter().order_by(Article.timestamp.desc()).all()
        for article in articles:
            if article in article_list:
                return article


def get_all_articles():
    '''
    Gets article recommendations for the main page.

    1. Uses user tendencies to determine article distribution.
    2. Gets a list of unread articles.
    3. Generates an article recommendation.
    4. Adds recommendation to recommendation list.
    5. Removes recommendation from unread article list.

    :rtype:     List of 10 article objects.
    '''
    article_list = get_unread_articles()
    recommendations = []

    user_tendencies = get_user_tendencies() 
    
    # Referrals
    for x in range(0, user_tendencies['referrals']):
        article = recommend_article(article_list=article_list, desired_interaction='referrals')
        recommendations.append(article)
        article_list.remove(article)

    # Shares
    for x in range(0, user_tendencies['shares']):
        article = recommend_article(article_list=article_list, desired_interaction='shares')
        recommendations.append(article)
        article_list.remove(article)

    # Comments
    for x in range(0, user_tendencies['comments']):
        article = recommend_article(article_list=article_list, desired_interaction='comments')
        recommendations.append(article)
        article_list.remove(article)

    # Views
    for x in range(0, user_tendencies['views']):
        article = recommend_article(article_list=article_list, desired_interaction='views')
        recommendations.append(article)
        article_list.remove(article)

    # News
    for x in range(0, user_tendencies['news']):
        article = recommend_article(article_list=article_list, desired_interaction='news')
        recommendations.append(article)
        article_list.remove(article)

    return recommendations


def get_section_articles(section):
    '''
    Same logic as `get_all_articles`, just for a specific section.

    :rtype:     List of 10 article objects.
    '''
    article_list = get_unread_articles(section=int(section))
    recommendations = []

    user_tendencies = get_user_tendencies() 
    
    # Referrals
    for x in range(0, user_tendencies['referrals']):
        article = recommend_article(article_list=article_list, desired_interaction='referrals')
        recommendations.append(article)
        article_list.remove(article)

    # Shares
    for x in range(0, user_tendencies['shares']):
        article = recommend_article(article_list=article_list, desired_interaction='shares')
        recommendations.append(article)
        article_list.remove(article)

    # Comments
    for x in range(0, user_tendencies['comments']):
        article = recommend_article(article_list=article_list, desired_interaction='comments')
        recommendations.append(article)
        article_list.remove(article)

    # Views
    for x in range(0, user_tendencies['views']):
        article = recommend_article(article_list=article_list, desired_interaction='views')
        recommendations.append(article)
        article_list.remove(article)

    # News
    for x in range(0, user_tendencies['news']):
        article = recommend_article(article_list=article_list, desired_interaction='news')
        recommendations.append(article)
        article_list.remove(article)

    return recommendations