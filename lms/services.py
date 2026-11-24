import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(course):
    product = stripe.Product.create(name=course.title)
    return product.id


def create_stripe_price(course, product_id):
    price = stripe.Price.create(
        currency='rub',
        unit_amount=int(course.price * 100),  # Stripe ждёт копейки
        product=product_id,
    )
    return price.id


def create_stripe_session(price_id):
    session = stripe.checkout.Session.create(
        success_url='http://127.0.0.1:8000/',
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
    )
    return session.id, session.url

