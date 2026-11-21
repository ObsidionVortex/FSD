def cart_context(request):
    """
    Context processor to provide cart information to all templates.
    """
    cart = request.session.get('cart', {})
    cart_count = 0
    if isinstance(cart, dict):
        cart_count = sum(cart.values())
    return {
        'cart_count': cart_count,
    }
