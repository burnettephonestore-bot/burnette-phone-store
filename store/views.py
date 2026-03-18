from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Product, Update, Request, Cart, UserProfile, Bank, MobileMoney, SiteSettings
from .serializers import ProductSerializer, UpdateSerializer, RequestSerializer, CartSerializer, UserProfileSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.views.decorators.cache import cache_page
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from decimal import Decimal


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    phone = forms.CharField(max_length=20, required=False, help_text="Enter your phone number for delivery and contact.")
    address = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter your full address for delivery.")
    city = forms.CharField(max_length=100, required=False, help_text="Enter your city.")
    region = forms.CharField(max_length=100, required=False, help_text="Enter your region (e.g., Dar es Salaam, Arusha).")
    district = forms.CharField(max_length=100, required=False, help_text="Enter your district for precise delivery.")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'address', 'city', 'region', 'district')


def get_settings():
    return SiteSettings.objects.first() or SiteSettings.objects.create()


@cache_page(60 * 5)
def home(request):
    products = Product.objects.all()[:6]  # Featured products
    updates = Update.objects.filter(valid_until__isnull=True) | Update.objects.filter(valid_until__gt=timezone.now())
    settings = get_settings()
    return render(request, 'home.html', {
        'products': products,
        'updates': updates,
        'settings': settings
    })


@cache_page(60 * 5)
def products(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)
    settings = get_settings()
    return render(request, 'products.html', {
        'products': products,
        'settings': settings,
        'query': query
    })


@cache_page(60 * 5)
def updates_view(request):
    updates = Update.objects.filter(valid_until__isnull=True) | Update.objects.filter(valid_until__gt=timezone.now())
    settings = get_settings()
    return render(request, 'updates.html', {
        'updates': updates,
        'settings': settings
    })

def request_product(request):
    selected_product = None
    if request.GET.get('product'):
        try:
            selected_product = Product.objects.get(id=request.GET['product'])
        except Product.DoesNotExist:
            selected_product = None

    if request.method == 'POST':
        product_id = request.POST.get('product')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email') or (request.user.email if request.user.is_authenticated else '')

        if request.user.is_authenticated:
            # Autofill missing user information
            if not name:
                name = request.user.get_full_name() or request.user.username
            if not phone:
                profile = getattr(request.user, 'userprofile', None)
                phone = (profile.phone if profile else '') or ''

        discount = request.POST.get('discount', 0)
        wants_delivery = request.POST.get('wants_delivery') == 'true'
        region = request.POST.get('region') if wants_delivery else ''
        district = request.POST.get('district') if wants_delivery else ''

        # Basic server-side validation
        if not product_id or not name or not phone:
            messages.error(request, 'Please select a product and provide your name and phone number.')
        else:
            try:
                product = Product.objects.get(id=product_id)
                discount_amount = Decimal(discount or '0')
                discount_amount = max(discount_amount, Decimal('0'))
                if discount_amount > product.price:
                    discount_amount = product.price
                final_price = max(product.price - discount_amount, Decimal('0'))

                if wants_delivery:
                    if not region or not district:
                        raise ValueError('Please provide your region and district for delivery.')
                    payment_method = ''
                    payment_target = ''
                else:
                    payment_method = request.POST.get('payment_method')
                    bank_name = request.POST.get('bank_name') if payment_method == 'bank' else ''
                    mobile_name = request.POST.get('mobile_name') if payment_method == 'mobile' else ''
                    payment_target = bank_name if payment_method == 'bank' else mobile_name
                    if not payment_method or not payment_target:
                        raise ValueError('Please choose a payment method and enter the account/number.')

                # Keep request linked to the authenticated user.
                new_request = Request.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    product=product,
                    product_name=product.name,
                    base_price=product.price,
                    discount=discount_amount,
                    final_price=final_price,
                    explanation='Request submitted via site form',
                    contact_name=name,
                    contact_phone=phone,
                    contact_email=email,
                    wants_delivery=wants_delivery,
                    region=region,
                    district=district,
                    payment_method=payment_method,
                    payment_target=payment_target
                )

                # Ensure the user's profile stays in sync with what they entered.
                if request.user.is_authenticated:
                    profile = getattr(request.user, 'userprofile', None)
                    if profile:
                        updated = False
                        if phone and not profile.phone:
                            profile.phone = phone
                            updated = True
                        if email and not request.user.email:
                            request.user.email = email
                            request.user.save()
                        if updated:
                            profile.save()

                settings = get_settings()
                try:
                    message = (
                        f"New product request submitted.\n"
                        f"Request ID: {new_request.id}\n"
                        f"Product: {product.name}\n"
                        f"Customer Name: {name}\n"
                        f"Customer Phone: {phone}\n"
                        f"Customer Email: {email or 'N/A'}\n"
                        f"Base Price: TZS {product.price}\n"
                        f"Discount: TZS {discount_amount}\n"
                        f"Final Price: TZS {final_price}\n"
                        f"Delivery: {'Yes' if wants_delivery else 'No'}\n"
                        f"Region: {region or 'N/A'}\n"
                        f"District: {district or 'N/A'}\n"
                        f"Payment Method: {payment_method or 'N/A'}\n"
                        f"Payment Target: {payment_target or 'N/A'}\n"
                        f"Submitted At: {new_request.created_at}\n"
                        f"Status: {new_request.status}"
                    )
                    send_mail(
                        subject=f"New product request: {product.name}",
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=['cleysir54@gmail.com'],
                        fail_silently=True,
                    )
                except Exception:
                    pass

                messages.success(request, 'Your request has been submitted successfully!')
                return redirect('request_product')
            except Product.DoesNotExist:
                messages.error(request, 'The selected product was not found.')
            except Exception as e:
                messages.error(request, f'Error submitting request: {str(e)}')

    products = Product.objects.all()
    banks = Bank.objects.all()
    mobiles = MobileMoney.objects.all()
    settings = get_settings()
    return render(request, 'request.html', {
        'products': products,
        'banks': banks,
        'mobiles': mobiles,
        'settings': settings,
        'selected_product': selected_product
    })

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        settings = get_settings()
        if username.lower() == settings.admin_username.lower() and password == settings.admin_password:
            request.session['admin_logged_in'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'admin_login.html')

def admin_dashboard(request):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    products = Product.objects.all()
    updates = Update.objects.all()
    status_filter = request.GET.get('status')
    requests = Request.objects.all().order_by('-created_at')
    if status_filter in ['pending', 'approved', 'rejected']:
        requests = requests.filter(status=status_filter)
    return render(request, 'admin_dashboard.html', {
        'products': products,
        'updates': updates,
        'requests': requests,
        'status_filter': status_filter
    })

def admin_update_request_status(request, request_id, status):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    if status not in ['pending', 'approved', 'rejected']:
        messages.error(request, 'Invalid status')
        return redirect('admin_dashboard')
    req = get_object_or_404(Request, pk=request_id)
    req.status = status
    req.save()
    messages.success(request, f'Request marked {status}.')
    return redirect('admin_dashboard')


def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Update user profile with additional details
            user.userprofile.phone = form.cleaned_data.get('phone')
            user.userprofile.address = form.cleaned_data.get('address')
            user.userprofile.city = form.cleaned_data.get('city')
            user.userprofile.region = form.cleaned_data.get('region')
            user.userprofile.district = form.cleaned_data.get('district')
            user.userprofile.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Burnette Phone Store.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please check the form and try again.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'{product.name} added to cart.')
    return redirect('products')


@login_required
def request_history(request):
    """Display a logged-in user's past product requests."""
    profile = None
    user_phone = ''
    try:
        profile = request.user.userprofile
        user_phone = profile.phone or ''
    except Exception:
        profile = None
        user_phone = ''

    # Get requests owned by the user
    user_requests = Request.objects.filter(user=request.user)

    # Get legacy requests by email
    legacy_email = Request.objects.filter(user__isnull=True, contact_email=request.user.email)

    # Get legacy requests by phone
    legacy_phone = Request.objects.filter(user__isnull=True, contact_phone=user_phone)

    # Combine all
    all_requests = list(user_requests) + list(legacy_email) + list(legacy_phone)
    all_requests.sort(key=lambda r: r.created_at, reverse=True)

    settings = get_settings()
    return render(request, 'request_history.html', {
        'requests': all_requests,
        'settings': settings
    })


@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    settings = get_settings()
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total, 'settings': settings})


@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, pk=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')


@login_required
def update_cart_quantity(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, pk=cart_id, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
        messages.success(request, 'Cart updated.')
    return redirect('view_cart')


def sitemap(request):
    products = Product.objects.all()
    updates = Update.objects.all()
    return render(request, 'sitemap.xml', {
        'products': products,
        'updates': updates,
        'host': request.get_host(),
        'scheme': request.scheme
    }, content_type='application/xml')


# API Views
class ProductListAPI(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductDetailAPI(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class UpdateListAPI(generics.ListAPIView):
    queryset = Update.objects.filter(valid_until__isnull=True) | Update.objects.filter(valid_until__gt=timezone.now())
    serializer_class = UpdateSerializer
    permission_classes = [permissions.AllowAny]


class CartListAPI(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class UserProfileAPI(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_request_api(request):
    # Similar to the web view, but for API
    # Implement request creation via API
    return Response({'message': 'Request created'})