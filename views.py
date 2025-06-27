from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Product, SellerProfile# Assuming you have a Product model
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Cart, Order,Order_buynow
from django.http import HttpResponse
from thrift_store.models import Product

@login_required
def buy_now(request):
    cart = request.user.cart
    items = cart.products.all()

    if not items:
        return redirect('cart')  # If cart is empty, redirect to the cart

    # Calculate the total amount for the order
    total_amount = sum(item.price for item in items)

    # Create the Buy Now order
    order = Order_buynow.objects.create(
        user=request.user,
        total_amount=total_amount,
        payment_method='Cash on Delivery'  # Hardcoded as COD
    )

    # Add products to the order
    order.items.set(items)

    for i in items:
        i.delete()
        
    # Clear the cart after creating the order
    #cart.products.clear()

    # Redirect to the order confirmation page
    return redirect('order_confirmation', order_id=order.id)


# Order confirmation view: displays the order details after "Buy Now"
def order_confirmation(request, order_id):
    order = get_object_or_404(Order_buynow, id=order_id)
    
    return render(request, 'thrift_store/order_confirmation.html', {'order': order})

# Index page: Products that were in the user's cart should not be shown
def index(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_products = cart.products.all()

    # Fetch all active products except those in the user's cart
    products = Product.objects.filter(is_active=True).exclude(id__in=cart_products.values_list('id', flat=True))
    
    return render(request, 'thrift_store/index.html', {'products': products})

# Seller dashboard: Exclude products in the user's cart from the dashboard
@login_required
def seller_dashboard(request):
    products = Product.objects.filter(seller=request.user)

    # Get the user's cart and remove the cart products from the seller's dashboard
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_products = cart.products.all()
    
    # Filter out products that are in the cart
    products = products.exclude(id__in=cart_products.values_list('id', flat=True))

    # Calculate total products
    total_products = products.count()

    # Calculate total sales
    total_sales = 0
    for product in products:
        total_sales += product.sold_count * product.price

    context = {
        'seller_name': request.user.first_name,
        'total_products': total_products,
        'total_sales': total_sales,
        'products': products
    }

    return render(request, 'thrift_store/dashboard.html', context)

# Add product: Ensure products that are in the cart are not available for addition again
@login_required
def add_product(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_products = cart.products.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not name or not price or not description or not image:
            messages.error(request, "All fields are required.")
            return render(request, 'thrift_store/add_product.html')

        # Save the product
        product = Product(
            name=name,
            price=price,
            description=description,
            image=image,
            seller=request.user
        )
        product.save()
        messages.success(request, "Product added successfully!")

        return redirect('index')  # Redirect to the index page after adding the product

    return render(request, 'thrift_store/add_product.html', {
        'cart_products': cart_products  # You can pass cart products to the template if needed
    })
    ##


    

def cart(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect to login if the user is not logged in

    # Ensure the user has a cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.products.all()

    return render(request, "thrift_store/cart.html", {
        "Products": items
    })
    
@receiver(post_save, sender=User)
def create_cart_for_user(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
        


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect to login if user is not logged in

    product = get_object_or_404(Product, id=product_id)

    # Ensure the user has a cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add the product to the cart
    cart.products.add(product)

    # Redirect back to the product list or any other page
    return redirect("index")  # Replace with the name of your product list view

def remove_from_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")  # Redirect to login if user is not logged in

    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(user=request.user)  # Assuming the cart exists
    
    # Remove the product from the cart
    cart.products.remove(product)

    return redirect("cart")  # Redirect back to the cart page

    


@login_required
def view_seller_products(request):
    # Fetch all products added by the logged-in seller
    products = Product.objects.filter(seller=request.user)
    return render(request, 'thrift_store/view_products.html', {'products': products})

@login_required
def logout(request):
    return render(request, 'thrift_store/logout.html')

@login_required
def edit_product(request, pk):
    # Fetch the product to be edited
    product = get_object_or_404(Product, id=pk, seller=request.user)  # Ensure the seller owns the product

    if request.method == 'POST':
        # Update the product with the new data
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        if request.FILES.get('image'):  # Only update image if a new one is uploaded
            product.image = request.FILES.get('image')
        product.save()

        messages.success(request, "Product updated successfully!")
        return redirect('view_products')  # Redirect back to the View Products page

    return render(request, 'thrift_store/edit_product.html', {'product': product})

@login_required
def delete_product(request, pk):
    # Fetch the product to be deleted
    product = get_object_or_404(Product, id=pk, seller=request.user)  # Ensure the seller owns the product

    if request.method == 'POST':  # Confirm deletion
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('view_products')  # Redirect back to the View Products page

    return render(request, 'thrift_store/delete_product.html', {'product': product})


@login_required
def seller_profile(request):
    # Get or create the SellerProfile for the logged-in user
    profile, created = SellerProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update user information
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()

        # Update profile information
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.save()

        return redirect('dashboard')  # Redirect to the dashboard

    return render(request, 'thrift_store/seller_profile.html', {'profile': profile})

def index(request):
    products = Product.objects.filter(is_active=True)  # Fetch all active products
    return render(request, 'thrift_store/index.html', {'products': products})
    

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index')  # Redirect to the homepage
        else:
            messages.error(request, 'Invalid email or password')
    return render(request, 'thrift_store/login.html')


def user_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'thrift_store/register.html')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'thrift_store/register.html')

        user = User.objects.create_user(username=email, password=password, first_name=name)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')
    return render(request, 'thrift_store/register.html')