from product.models import Category, Noutbooks, Card, Like, Order
from methodism import custom_response, error_messages, MESSAGE

def add_card(request, params):
    if 'product_id' not in params:
        return custom_response(False, message=MESSAGE['DataNotFull'])
    product = Noutbooks.objects.filter(id=params['product_id']).first()
    if not product:
        return custom_response(False, message=MESSAGE['NotData'])
    card, created = Card.objects.get_or_create(product=product, user= request.user)
    if created:
        card.quantity = params.get('qt', 1)
    else:
        card.quantity += params['qt']

    card.save()
    return custom_response(True, message=f"{product.model} qo'shildi {card.quantity} dona")


def delete_card(request, params):
    if 'card_id' not in params:
        return custom_response(False, message=MESSAGE['DataNotFull'])

    card = Card.objects.filter(id=params['card_id'], user=request.user).first()
    if not card:
        return custom_response(False, message=MESSAGE['NotData'])

    qt = params.get('qt', 1)

    if qt > card.quantity:
        return custom_response(False, message="Savatdagi miqdor so'ralgan miqdordan kam.")

    if qt == card.quantity:
        card.delete()
    else:
        card.quantity -= qt
        card.save()

    return custom_response(True, message=f"{qt} dona mahsulot o'chirildi.")


def get_card(request,params):
    cards = Card.objects.filter(user=request.user)
    data = []
    for card in cards:
        data.append({
            'id': card.id,
            'product': card.product.model,
            'quantity': card.quantity,
            'price': float(card.price),
            'total': float(card.price),
        })
    return custom_response(True, data=data)


def add_order(request, params):
    cards = Card.objects.filter(user=request.user)

    if not cards.exists():
        return custom_response(False, message="Savat bo'sh! Hech qanday mahsulot mavjud emas.")

    total_price = 0
    for card in cards:
        total_price += card.price * card.quantity

    order = Order.objects.create(
        user=request.user,
        price=total_price,
        status=False
    )

    for card in cards:
        order.card.add(card)
    cards.delete()

    return custom_response(True, message="Buyurtma muvaffaqiyatli qabul qilindi")

def get_order(request, params):
    orders = Order.objects.filter(user=request.user)
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'price': float(order.price),
            'status': "Qabul qilingan" if order.status else "Kutilmoqda",
            'created_at': order.created_at,
        })
    return custom_response(True, data=data)


def order_accept(request, params):
    if 'order_id' not in params:
        return custom_response(False, message=MESSAGE['DataNotFull'])

    order = Order.objects.filter(id=params['order_id']).first()
    if not order:
        return custom_response(False, message=MESSAGE['NotData'])

    order.status = True
    order.save()
    return custom_response(True, message="Buyurtma qabul qilindi")


def add_like(request, params):
    if 'product_id' not in params:
        return custom_response(False, message="Ma'lumotlar to'liq emas!")
    product = Noutbooks.objects.filter(id=params['product_id']).first()
    if not product:
        return custom_response(False, message="Mahsulot topilmadi!")
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if created:
        like.like = True
    else:
        like.like = not like.like
    like.save()
    return custom_response(True,message=f"{product.model} mahsuloti {'yoqtirildi' if like.like else 'yoqtirilmadi'}.")


def get_like(request, params):
    likes = Like.objects.filter(user=request.user, like=True)
    data = []
    for like in likes:
        data.append({
            'product': like.product.model,
            'price': float(like.product.price),
        })
    return custom_response(True, data=data)


def add_dislike(request, params):
    if 'product_id' not in params:
        return custom_response(False, message="Ma'lumotlar to'liq emas!")
    product = Noutbooks.objects.filter(id=params['product_id']).first()
    if not product:
        return custom_response(False, message="Mahsulot topilmadi!")
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if created:
        like.dislike = True
    else:
        like.dislike = not like.dislike

    like.save()

    return custom_response(True,message=f"{product.model} mahsuloti {'yoqtirilmadi' if like.dislike else 'yoqtirildi'}.")