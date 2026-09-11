from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Store, Order, OrderItem, Review
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import StoreForm, ProductForm, ReviewForm, RegistrationForm
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.contrib.auth.models import Group


def register(request):
    '''Register a new user as a Buyer or Vendor.'''

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            role = form.cleaned_data['role']
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'Shop/register.html', {
        'form': form
    })


def login_redirect(request):
    '''Redirect users to the appropriate page after login.'''

    if request.user.groups.filter(name='Vendor').exists():
        return redirect('store_list')

    if request.user.groups.filter(name='Admin').exists():
        return redirect('/admin/')

    return redirect('product_list')


class CustomLoginView(LoginView):
    '''Log users in and redirect them based on their group.'''

    def get_success_url(self):
        return login_redirect(self.request).url


def is_vendor(user):
    return user.groups.filter(name='Vendor').exists()


def product_list(request):
    '''Display a list of all products.'''
    products = Product.objects.all()

    return render(request, 'Shop/product_list.html', {
        'products': products
    })


def product_detail(request, product_id):
    '''Display the details of a single product.'''
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    return render(request, 'Shop/product_detail.html', {
        'product': product,
        'reviews': reviews
    })


def store_list(request):
    '''Display a list of all stores.'''
    stores = Store.objects.all()

    return render(request, 'Shop/store_list.html', {
        'stores': stores
    })


def store_detail(request, store_id):
    '''Display the details of a single store.'''
    store = get_object_or_404(Store, id=store_id)
    return render(request, 'Shop/store_detail.html', {
        'store': store
    })


@login_required
@user_passes_test(is_vendor)
def product_create(request):
    '''Add a new product to the store.'''
    stores = Store.objects.filter(vendor=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = get_object_or_404(
                Store, id=request.POST['store'],
                vendor=request.user
            )
            product.save()
            return redirect('product_list')

    else:
        form = ProductForm()

    return render(request, 'Shop/add_product.html', {
        'form': form,
        'stores': stores
    })


@login_required
@user_passes_test(is_vendor)
def product_delete(request, product_id):
    '''Delete an existing product'''
    product = get_object_or_404(
            Product,
            id=product_id,
            store__vendor=request.user
        )
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, "Shop/product_confirm_delete.html", {
        "product": product
    })


@login_required
@user_passes_test(is_vendor)
def product_update(request, product_id):
    '''Update existing product.'''
    product = get_object_or_404(
            Product,
            id=product_id,
            store__vendor=request.user
        )
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            return redirect("product_list")
    form = ProductForm(instance=product)

    return render(request, 'Shop/product_update.html', {
        "form": form,
        "product": product
    })


@login_required
@user_passes_test(is_vendor)
def store_create(request):
    '''Add a new store to the application.'''
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        vendor = request.user

        Store.objects.create(
            name=name,
            description=description,
            vendor=vendor
        )

        return redirect('store_list')

    return render(request, 'Shop/add_store.html')


@login_required
@user_passes_test(is_vendor)
def store_delete(request, store_id):
    store = get_object_or_404(Store, id=store_id, vendor=request.user)
    if request.method == 'POST':
        store.delete()
        return redirect('store_list')

    return render(request, 'Shop/store_confirm_delete.html', {
        'store': store
    })


@login_required
@user_passes_test(is_vendor)
def store_update(request, store_id):

    store = get_object_or_404(
        Store,
        id=store_id,
        vendor=request.user
    )

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save(commit=False)
            form.save()
            return redirect('store_list')

    else:
        form = StoreForm(instance=store)

    return render(request, 'Shop/store_update.html', {
        'form': form,
        'store': store
    })


@login_required
def add_to_cart(request, product_id):
    '''Add a product to the user's session cart.'''

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    quantity = int(request.POST.get('quantity', 1))

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')


@login_required
def cart_detail(request):
    '''Display the current user's session cart.'''

    cart = request.session.get('cart', {})

    cart_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        cart_items.append({
            'product': product,
            'quantity': quantity
        })

    total = sum(
        item['product'].price * item['quantity']
        for item in cart_items
    )

    return render(request, 'Shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def checkout(request):
    '''Process the user's session cart.'''

    cart = request.session.get('cart', {})

    cart_items = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)

        cart_items.append({
            'product': product,
            'quantity': quantity
        })

    total = sum(
        item['product'].price * item['quantity']
        for item in cart_items
    )

    if request.method == 'POST':
        if not cart_items:
            return redirect('cart_detail')

        order = Order.objects.create(
            user=request.user,
            total=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        email_body = f"""
        Thank you for your order.

        Order number: {order.id}
        Date: {order.created_at}

        Items:
        """

        for item in cart_items:
            email_body += (
                f"{item['product'].name} - "
                f"Quantity: {item['quantity']} - "
                f"Price: R{item['product'].price}\n"
            )

        email_body += f"\nTotal: R{order.total}"

        send_mail(
            subject=f"Invoice for Order #{order.id}",
            message=email_body,
            from_email=None,
            recipient_list=[request.user.email],
        )

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('invoice', order_id=order.id)

    return render(request, 'Shop/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def invoice(request, order_id):
    '''Display an invoice for a completed order.'''

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'Shop/invoice.html', {
        'order': order,
        'order_items': order_items
    })


@login_required
def review_create(request, product_id):
    '''Allow a logged-in user to leave a review for a product.'''

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user

            review.verified = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()

            review.save()

            return redirect('product_detail', product_id=product.id)

    else:
        form = ReviewForm()

    return render(request, 'Shop/review_form.html', {
        'form': form,
        'product': product
    })


@login_required
def remove_from_cart(request, product_id):
    '''Remove a product from the user's session cart.'''

    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')
