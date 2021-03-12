import stripe
from app.models import User, ApiClient
from config import Config
import json


def pause_subscription(entity_type, entity_id):
    '''
    Pauses subscription for a given object.

    :param entity_type:     Is this a user or an API client, as a string?
    :param entity_id:       What is the primary key for this entity, as an integer?
    :rtype:                 Stripe JSON response if entity has a Stripe customer ID
    :rtype:                 None if entity does not have a Stripe customer ID
    :onerror:               Raises an assertion error if `entity_type` is not accepted.
    :onerror:               Raises an assertion error if `entity_id` is not an integer.
    '''

    stripe.api_key = Config.STRIPE_SECRET_KEY

    accepted_entities = ['user', 'api_client']

    if entity_type == 'user':
        entity = User.query.filter_by(id=entity_id).first()
    elif entity_type == 'api_client':
        entity = ApiClient.query.filter_by(id=entity_id).first()

    customer = entity.stripe_customer_id

    if customer is not None:
        subscriptions = stripe.Subscription.list(customer=customer).to_dict()
        try:
            for x in subscriptions['data']:
                stripe.Subscription.modify(
                    x['id'],
                    pause_collection={
                        'behavior': 'mark_uncollectible',
                        'resumes_at': entity.expires_on
                    }
                )
        except:
            return
    else:
        return


def cancel_subscription(entity_type, entity_id):
    '''
    Cancels a subscription for a given object.

    :param entity_type:     Is this a user or an API client, as a string?
    :param entity_id:       What is the primary key for this entity, as an integer?
    :rtype:                 Stripe JSON response if entity has a Stripe customer ID
    :rtype:                 None if entity does not have a Stripe customer ID
    :onerror:               Raises an assertion error if `entity_type` is not accepted.
    :onerror:               Raises an assertion error if `entity_id` is not an integer.
    '''

    stripe.api_key = Config.STRIPE_SECRET_KEY

    accepted_entities = ['user', 'api_client']

    if entity_type == 'user':
        entity = User.query.filter_by(id=entity_id).first()
    elif entity_type == 'api_client':
        entity = ApiClient.query.filter_by(user_id=entity_id).first()

    customer = entity.stripe_customer_id

    if customer is not None:
        subscriptions = stripe.Subscription.list(customer=customer).to_dict()
        try:
            for x in subscriptions['data']:
                stripe.Subscription.delete(x['id'])
        except:
            return
    else:
        return