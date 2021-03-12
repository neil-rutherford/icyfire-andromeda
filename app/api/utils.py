import redis
from config import Config
import time
from app.models import ApiClient, User
from flask import request

def verify_client(consumer_key, consumer_secret, permission):
    # Looks up API Client using consumer key
    client = ApiClient.query.filter_by(consumer_key=str(consumer_key)).first()

    # API Client not found
    if client is None:
        return (False, 403, "Authentication failed, client not found.")
    
    # API Client's consumer key is correct, but the consumer secret is incorrect
    if client.consumer_secret != str(consumer_secret):
        return (False, 403, "Authentication failed, incorrect credentials.")

    # Checks if API Client is approved or on a blacklist
    if client.is_blacklist is True or client.is_approved is False:
        return (False, 403, "API access has been restricted by the provider.")
    
    # Connects to Redis database and looks up how many requests have been made over the last hour
    r_server = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        password=Config.REDIS_PASSWORD
    )
    requests = r_server.llen('{}'.format(client.id))

    # If there have been no requests, add this request to a list that expires in an hour
    if requests == 0:
        r_server.rpush('{}'.format(client.id), int(time.time()))
        r_server.expire('{}'.format(client.id), 3600)

    # If the API Client has a subscription and they have gone over 3600 requests/hour, rate-limit them
    elif client.check_subscription() is True and requests > 3600:
        return (False, 429, "Too many requests, you are limited to 3,600 requests / hour.")

    # If the API Client doesn't have a subscription and they have gone over 60 requests/hour, rate-limit them
    elif client.check_subscription() is False and requests > 60:
        return (False, 429, "Too many requests, you are limited to 60 requests / hour.")
    
    # Else...add the request to the list and continue!
    else:
        r_server.rpush('{}'.format(client.id), int(time.time()))

    # Checks required permissions against granted permissions, raises a 403 if there is a problem
    if permission == 'articles' and client.is_articles is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'comments' and client.is_comments is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'logs' and client.is_logs is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'shares' and client.is_shares is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'users' and client.is_users is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'connections' and client.is_connections is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'comments' and client.is_comments is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'messages' and client.is_messages is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    elif permission == 'api' and client.is_api is False:
        return (False, 403, "Insufficient permissions, resource access denied.")
    
    # If they have successfully run the gauntlet, return True
    return (True, 200, "Client verified.")


def get_user(consumer_key):
    client = ApiClient.query.filter_by(consumer_key=str(consumer_key)).first()
    return User.query.filter_by(id=client.user_id).first()