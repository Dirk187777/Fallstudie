"""Warenkorb in der Session: {"<Mischungs-ID>:<Größe>": Menge}."""
from decimal import Decimal

from shop.models import Blend, Size

SESSION_KEY = "cart"
MAX_QUANTITY = 20


def _get(session):
    return session.setdefault(SESSION_KEY, {})


def _key(blend_id, size):
    return f"{blend_id}:{size}"


def _parse(key):
    blend_id, _, size = key.partition(":")
    return int(blend_id), size or Size.REGULAR


def add(session, blend_id, size=Size.REGULAR, quantity=1):
    cart = _get(session)
    key = _key(blend_id, size)
    cart[key] = cart.get(key, 0) + quantity
    session.modified = True


def set_quantity(session, blend_id, size, quantity):
    """Menge setzen, 0 entfernt die Position."""
    if quantity <= 0:
        remove(session, blend_id, size)
        return
    key = _key(blend_id, size)
    cart = _get(session)
    if key in cart:
        cart[key] = min(quantity, MAX_QUANTITY)
        session.modified = True


def remove(session, blend_id, size=Size.REGULAR):
    _get(session).pop(_key(blend_id, size), None)
    session.modified = True


def count(session):
    return sum(session.get(SESSION_KEY, {}).values())


def items(session):
    entries = [(*_parse(key), quantity) for key, quantity in session.get(SESSION_KEY, {}).items()]
    blends = Blend.objects.select_related("base", "flavor").prefetch_related("boosters")
    blends = blends.in_bulk([blend_id for blend_id, _, _ in entries])
    result = []
    for blend_id, size, quantity in entries:
        blend = blends.get(blend_id)
        if blend is None:
            continue
        summary = blend.summary_for(size)
        result.append({
            "blend": blend,
            "size": size,
            "can_grams": summary["can_grams"],
            "quantity": quantity,
            "price": summary["price"],
            "subtotal": summary["price"] * quantity,
        })
    return result


def total(cart_items):
    return sum((item["subtotal"] for item in cart_items), Decimal("0"))


def clear(session):
    session.pop(SESSION_KEY, None)
