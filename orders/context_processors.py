from . import cart


def cart_count(request):
    return {"cart_count": cart.count(request.session)}
