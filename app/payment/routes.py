from app.payment import bp
from flask import render_template, flash, redirect, url_for, request, Response
import stripe
import datetime
from config import Config
from flask_login import login_required, current_user
from app.models import ApiClient, User
from app.payment.utils import cancel_subscription
from app import db

# https://www.youtube.com/watch?v=cC9jK3WntR8&ab_channel=PrettyPrinted
# https://github.com/PrettyPrinted/youtube_video_code/blob/master/2020/06/12/Accepting%20Payments%20in%20Flask%20Using%20Stripe%20Checkout%20%5B2020%5D/flask_stripe/app.py

stripe.api_key = Config.STRIPE_SECRET_KEY
stripe_endpoint_secret = Config.STRIPE_ENDPOINT_SECRET


@bp.route('/payment/buy/patriot-tier')
@login_required
def buy_patriot_tier():
    customer = stripe.Customer.create(
        email=current_user.email,
        name=current_user.username
    )
    current_user.stripe_customer_id = customer['id']
    db.session.commit()

    session = stripe.checkout.Session.create(
        success_url=url_for('payment.thank_you', product='patriot-tier', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('payment.buy_patriot_tier', _external=True),
        mode='subscription',
        payment_method_types=['card'],
        customer=current_user.stripe_customer_id,
        line_items=[{
            'price': Config.STRIPE_PATRIOT_PRODUCT_KEY,
            'quantity': 1
        }]
    )
    return render_template(
        'payment/buy_patriot_tier.html',
        title='Start your Patriot subscription',
        checkout_session_id=session['id'],
        checkout_public_key=Config.STRIPE_PUBLIC_KEY
    )


@bp.route('/payment/buy/premium-api')
@login_required
def buy_premium_api():
    client = ApiClient.query.filter_by(user_id=current_user.id).first()
    if client is None:
        flash("Please register before attempting payment.")
        return redirect(url_for('api.apply'))

    customer = stripe.Customer.create(
        email=client.email,
        description='Premium API subscription'
    )
    client.stripe_customer_id = customer['id']
    db.session.commit()

    session = stripe.checkout.Session.create(
        success_url=url_for('payment.thank_you', product='premium-api', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('payment.buy_premium_api', _external=True),
        mode='subscription',
        payment_method_types=['card'],
        customer=client.stripe_customer_id,
        line_items=[{
            'price': Config.STRIPE_PREMIUM_API_PRODUCT_KEY,
            'quantity': 1
        }]
    )
    return render_template(
        'payment/buy_premium_api.html',
        title='Start your Premium API subscription',
        client=client,
        checkout_session_id=session['id'],
        checkout_public_key=Config.STRIPE_PUBLIC_KEY
    )


@bp.route('/payment/cancel/patriot-tier')
@login_required
def cancel_patriot_tier():
    cancel_subscription(entity_type='user', entity_id=current_user.id)
    flash("Your Patriot Tier subscription has been cancelled.")
    return redirect(url_for('auth.settings'))


@bp.route('/payment/cancel/premium-api')
@login_required
def cancel_premium_api():
    cancel_subscription(entity_type='api_client', entity_id=current_user.id)
    flash("Your Premium API subscription has been cancelled.")
    return redirect(url_for('api.view_client'))


@bp.route('/payment/thank-you/<product>')
def thank_you(product):
    flash("Thank you for your business!")
    if product == 'patriot-tier':
        return redirect(url_for('auth.settings'))
    elif product == 'premium-api':
        return redirect(url_for('api.view_client'))
    else:
        return Response(status=400, response="Accepted products: patriot-tier, premium-api.")


@bp.route('/_payment/webhook', methods=['POST'])
def webhook():
    print('WEBHOOK CALLED')

    if request.content_length > 1024 * 1024:
        print('REQUEST TOO BIG')
        abort(400)
    payload = request.get_data()
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = Config.STRIPE_ENDPOINT_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        print('INVALID PAYLOAD')
        return {}, 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('INVALID SIGNATURE')
        return {}, 400

    # Handle the checkout.session.completed event
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        customer = event['data']['object']['customer']
        if line_items['data'][0]['description'] == 'Galatea Patriot Tier':
            entity = User.query.filter_by(stripe_customer_id=customer).first()
        elif line_items['data'][0]['description'] == 'Galatea Premium API':
            print('Galatea Premium API')
            entity = ApiClient.query.filter_by(stripe_customer_id=customer).first()
            if entity:
                print('Client found!')
        else:
            return {}, 400

        
        entity.expires_on = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        db.session.commit()
        
    
    return {}