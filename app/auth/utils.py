from app.models import ActivityLog, Share
from app import db

def transfer_logs(anonymous_uuid, user_id):
    '''
    1. Looks up all views for a given `anonymous_uuid` value.
    2. Sets the previously null `view.user_id` to the given `user_id` value.
    3. Commits all changes to database.

    :param anonymous_uuid:      Anonymous UUID, as a string.
    :param user_id:             User ID, as an integer.
    :rtype:                     None
    '''
    logs = ActivityLog.query.filter_by(anonymous_uuid=str(anonymous_uuid)).all()
    for log in logs:
        log.user_id = int(user_id)
    db.session.add_all(logs)
    db.session.commit()


def transfer_shares(anonymous_uuid, user_id):
    '''
    1. Looks up all shares for a given `anonymous_uuid` value.
    2. Sets the previously null `share.user_id` to the given `user_id` value.
    3. Commits all changes to database.

    :param anonymous_uuid:      Anonymous UUID, as a string.
    :param user_id:             User ID, as an integer.
    :rtype:                     None
    '''
    shares = Share.query.filter_by(anonymous_uuid=str(anonymous_uuid)).all()
    for share in shares:
        share.user_id = int(user_id)
    db.session.add_all(shares)
    db.session.commit()