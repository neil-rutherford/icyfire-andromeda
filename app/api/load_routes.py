from app.api import bp
from flask import Response, request, url_for
import json
from app.models import User
from app.analytics.lame_utils import get_all_articles, get_section_articles
import datetime

@bp.route('/_api/load/articles/<section>')
def load_articles(section):
    '''
    {
        image_file_path
        section (as UPPERCASE English)
        title
        description
        tags (as comma-separated list)
        timestamp (YYYY-MM-DD HH:MM:SS)
        url_for
    }
    '''
    quantity = 10

    if section == 'all':
        posts = get_all_articles()
    elif section == 'politics':
        posts = get_section_articles(1)
    elif section == 'world':
        posts = get_section_articles(2)
    elif section == 'technology':
        posts = get_section_articles(3)
    elif section == 'energy':
        posts = get_section_articles(4)
    elif section == 'economy':
        posts = get_section_articles(5)
    elif section == 'science':
        posts = get_section_articles(6)
    elif section == 'health':
        posts = get_section_articles(7)
    else:
        return Response(status=400, response="Accepted sections: all, politics, world, technology, energy, economy, science, health.")

    section_dict = {
        1: 'U.S. POLITICS',
        2: 'WORLD NEWS',
        3: 'TECHNOLOGY',
        4: 'ENERGY / ENVIRONMENT',
        5: 'ECONOMY / BUSINESS',
        6: 'SCIENCE / RELIGION',
        7: 'HEALTH'
    }

    if request.args:
        counter = int(request.args.get("counter"))
        if counter == 0:
            data_list = []
            for post in posts[0: quantity]:
                data_dict = [
                    post.image_file_path,
                    section_dict[post.section],
                    post.title,
                    post.description,
                    post.tags,
                    post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    url_for('main.view_article', slug=post.slug)
                ]
                data_list.append(data_dict)
            data_json = json.dumps(data_list)

        elif counter == len(posts):
            print("No more posts.")
            data_json = json.dumps([])

        else:
            data_list = []
            for post in posts[counter: counter + quantity]:
                data_dict = [
                    post.image_file_path,
                    section_dict[post.section],
                    post.title,
                    post.description,
                    post.tags,
                    post.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    url_for('main.view_article', slug=post.slug)
                ]
                data_list.append(data_dict)
            data_json = json.dumps(data_list)

    return Response(
        status=200,
        response=data_json,
        mimetype='application/json'
    )


@bp.route('/_api/load/connections/type=<connection_type>&user=<username>')
def load_connections(connection_type, username):
    '''
    {
        profile_pic
        username
        is_subscription
        status
        url_for
    }
    '''
    quantity = 10
    user = User.query.filter_by(username=username).first()
    if user is None:
        return Response(status=404, response='User {} not found.'.format(username))
    if connection_type == 'followers':
        connections = user.followers.all()
    elif connection_type == 'following':
        connections = user.followed.all()
    else:
        return Response(status=400, response="Accepted connection_types: followers, following.")
    
    if request.args:
        counter = int(request.args.get('counter'))
        if counter == 0:
            data_list = []
            for x in connections[0:quantity]:
                data_dict = [
                    x.profile_pic,
                    x.username,
                    x.check_subscription(),
                    x.status,
                    url_for('main.view_user', username=x.username)
                ]
                data_list.append(data_dict)
            data_json = json.dumps(data_list)
        elif counter == len(connections):
            print("No more connections.")
            data_json = json.dumps([])
        else:
            data_list = []
            for x in connections[counter: counter + quantity]:
                data_dict = [
                    x.profile_pic,
                    x.username,
                    x.check_subscription(),
                    x.status,
                    url_for('main.view_user', username=x.username)
                ]
                data_list.append(data_dict)
            data_json = json.dumps(data_list)
    
    return Response(
        status=200,
        response=data_json,
        mimetype='application/json'
    )