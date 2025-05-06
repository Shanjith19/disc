from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.utils import timezone
from .models import Discount, Cart, Payment
from django.http import JsonResponse
from geopy.distance import geodesic
import razorpay
from .forms import DiscountForm
from django.shortcuts import get_object_or_404

# User Signup
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'discounts/signup.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'discounts/login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Dashboard (display discounts)
@login_required
def dashboard(request):
    discounts = Discount.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
    return render(request, 'discounts/dashboard.html', {'discounts': discounts})

# Nearby Discounts API
def nearby_discounts_api(request):
    latitude = request.GET.get("latitude")
    longitude = request.GET.get("longitude")
    
    if not latitude or not longitude:
        return JsonResponse({"error": "Latitude and Longitude required"}, status=400)

    user_location = (float(latitude), float(longitude))

    discounts = Discount.objects.all()
    nearby_discounts = []

    for discount in discounts:
        store_location = (discount.latitude, discount.longitude)
        distance = geodesic(user_location, store_location).km

        if distance <= 10:  # 10 km range
            nearby_discounts.append({
                "title": discount.title,
                "description": discount.description,
                "percentage": discount.percentage,
                "end_date": discount.end_date.strftime("%Y-%m-%d"),
                "shopkeeper": discount.shopkeeper.username
            })

    return JsonResponse({"deals": nearby_discounts})

# Add to Cart
@login_required

@login_required
def add_to_cart(request, discount_id):
    discount = get_object_or_404(Discount, id=discount_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.discounts.add(discount)
    cart.calculate_total()
    return redirect('dashboard')

# View Cart
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'discounts/cart.html', {'cart': cart})

@login_required
def checkout(request):
    # Assuming user is logged in and has a cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart.calculate_total()  # Recalculate the total if any changes
        return render(request, 'discounts/checkout.html', {'cart': cart})
    except Cart.DoesNotExist:
        return render(request, 'discounts/empty_cart.html') 

# Payment
""" def process_payment(request):
    cart = Cart.objects.get(user=request.user)
    amount = cart.total_amount

    # Apply 5% discount
    amount_after_discount = amount - (amount * 0.05)

    client = razorpay.Client(auth=("YOUR_RAZORPAY_KEY", "YOUR_RAZORPAY_SECRET"))
    payment = client.order.create(
        dict(
            amount=amount_after_discount * 100,  # in paise
            currency="INR",
            payment_capture="1"
        )
    )

    Payment.objects.create(
        user=request.user,
        cart=cart,
        amount_paid=amount_after_discount
    )

    return JsonResponse({"payment_id": payment['id'], "amount": amount_after_discount})
 """
from django.shortcuts import render, redirect
from .models import Cart, Payment
from django.contrib.auth.decorators import login_required

@login_required
def process_payment(request):
    cart = Cart.objects.get(user=request.user)
    amount = int(cart.total_amount * 100)  # Razorpay expects paise (but we’re mocking this)

    # Mocking payment success
    payment = Payment.objects.create(
        user=request.user,
        cart=cart,
        amount=cart.total_amount,
        status='Success',  # Mock success
        transaction_id="MOCK_TXN_123456"
    )

    # Clear cart (optional)
    cart.discounts.clear()

    return render(request, 'discounts/payment_success.html', {'payment': payment})

@login_required
def approve_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.user == payment.cart.discounts.first().shopkeeper:
        payment.payment_status = 'Approved'
        payment.save()
    return redirect('dashboard')  # Or wherever you want to redirect

# Shopkeeper - Upload Offers
from .forms import DiscountForm
from django.contrib.auth.decorators import login_required

@login_required
def upload_discount(request):
    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.shopkeeper = request.user  # assigns current user
            discount.save()
            return redirect('dashboard')
    else:
        form = DiscountForm()
    return render(request, 'discounts/upload_discount.html', {'form': form})
