from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.views.decorators.http import require_POST
from decimal import Decimal

from .models import Product, Order, OrderItem
from .forms import ProductForm, CheckoutForm


# HOME PAGE
def home(request):
    query = request.GET.get('q', '').strip()
    stock_filter = request.GET.get('stock', '').strip()
    sort_by = request.GET.get('sort', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if stock_filter == 'in_stock':
        products = products.filter(stock__gt=0)
    elif stock_filter == 'out_of_stock':
        products = products.filter(stock=0)

    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    total_count = Product.objects.count()

    return render(request, 'home.html', {
        'products': products,
        'query': query,
        'stock_filter': stock_filter,
        'sort_by': sort_by,
        'total_count': total_count,
    })


# PRODUCT DETAILS
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    related_products = Product.objects.exclude(id=id).order_by('-id')[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ADMIN CHECK
def is_admin(user):
    return user.is_authenticated and user.is_staff


# ADD PRODUCT
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('home')
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {
        'form': form,
        'page_title': 'Add a product',
        'submit_label': 'Add product',
    })


# UPDATE PRODUCT
@login_required
@user_passes_test(is_admin)
def update_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully.')
            return redirect('home')
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {
        'form': form,
        'page_title': f'Update {product.name}',
        'submit_label': 'Save changes',
        'product': product,
    })


# DELETE PRODUCT
@login_required
@user_passes_test(is_admin)
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" has been removed.')
        return redirect('home')

    return render(request, 'delete_product.html', {
        'product': product
    })


# REGISTER
def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {
        'form': form
    })


# LOGIN
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'login.html')


# LOGOUT
@require_POST
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been safely logged out.')
    return redirect('login')


# ADD TO CART
@login_required
@require_POST
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart = request.session.get('cart', {})
    product_id = str(product.id)
    quantity = cart.get(product_id, 0)

    try:
        qty_to_add = int(request.POST.get('quantity', 1))
        if qty_to_add < 1:
            qty_to_add = 1
    except (ValueError, TypeError):
        qty_to_add = 1

    if product.stock < 1 or (quantity + qty_to_add) > product.stock:
        messages.error(request, 'This product is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart[product_id] = quantity + qty_to_add
    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f'Added {product.name} to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# UPDATE CART QUANTITY (+ / -)
@login_required
@require_POST
def update_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart = request.session.get('cart', {})
    product_id = str(product.id)
    current_qty = cart.get(product_id, 0)

    action = request.POST.get('action')

    if action == 'increase':
        if current_qty < product.stock:
            cart[product_id] = current_qty + 1
            messages.success(request, f'Updated quantity for {product.name}.')
        else:
            messages.warning(request, f'Only {product.stock} units available in stock.')
    elif action == 'decrease':
        if current_qty > 1:
            cart[product_id] = current_qty - 1
            messages.success(request, f'Updated quantity for {product.name}.')
        else:
            cart.pop(product_id, None)
            messages.info(request, f'Removed {product.name} from cart.')

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')


# VIEW CART
@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    # Remove any stale products that no longer exist
    stale_keys = []
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            stale_keys.append(product_id)

    if stale_keys:
        for k in stale_keys:
            cart.pop(k, None)
        request.session['cart'] = cart
        request.session.modified = True

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total,
        'subtotal': total,
    })


# REMOVE FROM CART
@login_required
@require_POST
def remove_cart(request, id):
    cart = request.session.get('cart', {})
    removed = cart.pop(str(id), None)
    request.session['cart'] = cart
    request.session.modified = True

    if removed is not None:
        messages.info(request, 'Item removed from your cart.')

    return redirect('view_cart')


# CHECKOUT
@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty. Add items before proceeding to checkout.')
        return redirect('view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    total = Decimal('0.00')
                    products = {}

                    for product_id, quantity in cart.items():
                        product = get_object_or_404(
                            Product.objects.select_for_update(),
                            id=product_id
                        )

                        if quantity < 1 or product.stock < quantity:
                            raise ValueError(
                                f"Insufficient stock for {product.name}"
                            )

                        products[product_id] = product
                        total += product.price * quantity

                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total,
                        address=form.cleaned_data['address']
                    )

                    for product_id, quantity in cart.items():
                        product = products[product_id]

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )

                        product.stock -= quantity
                        product.save()

                request.session['cart'] = {}
                request.session.modified = True

                messages.success(
                    request,
                    'Order placed successfully! Thank you for your purchase.'
                )

                return redirect('my_orders')

            except ValueError as error:
                messages.error(request, str(error))
                return redirect('view_cart')

    else:
        form = CheckoutForm()

    # Calculate cart summary for checkout page
    cart_items = []
    total = Decimal('0.00')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            pass

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    })


# MY ORDERS
@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__product').order_by('-created_at')

    return render(request, 'orders.html', {
        'orders': orders
    })


def not_found(request, exception):
    return render(request, '404.html', status=404)
