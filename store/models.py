from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    media_url = models.URLField(max_length=1024, blank=True)
    media_file = models.ImageField(upload_to='products/', blank=True)
    media_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')], default='image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Update(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video')], default='text')
    content = models.TextField()
    media_url = models.URLField(max_length=1024, blank=True)
    media_file = models.FileField(upload_to='updates/', blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=12, decimal_places=2)
    explanation = models.TextField()
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    wants_delivery = models.BooleanField(default=False)
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=10, choices=[('bank', 'Bank'), ('mobile', 'Mobile Money')], blank=True)
    payment_target = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.contact_name} for {self.product_name}"

class Bank(models.Model):
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class MobileMoney(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Comment(models.Model):
    name = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name}"

class SiteSettings(models.Model):
    title = models.CharField(max_length=255, default='Burnette Phone Store')
    logo_url = models.URLField(max_length=1024, blank=True)
    theme_color = models.CharField(max_length=7, default='#0d6efd')
    admin_username = models.CharField(max_length=100, default='hudhaifa')
    admin_password = models.CharField(max_length=255, default='123')
    admin_name = models.CharField(max_length=255, default='Hudhaifa')
    admin_email = models.EmailField(blank=True)
    admin_phone = models.CharField(max_length=20, blank=True)
    logo_file = models.ImageField(upload_to='logos/', blank=True, null=True, help_text="Upload an image file of any type (JPEG, PNG, GIF, BMP, TIFF, WebP, etc.)")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        # Send email notification
        try:
            message = (
                f"A new user has registered.\n"
                f"Username: {instance.username}\n"
                f"Email: {instance.email}\n"
                f"First Name: {instance.first_name or 'N/A'}\n"
                f"Last Name: {instance.last_name or 'N/A'}\n"
                f"Date Joined: {instance.date_joined}\n"
                f"Phone: {instance.userprofile.phone or 'N/A'}\n"
                f"Address: {instance.userprofile.address or 'N/A'}\n"
                f"City: {instance.userprofile.city or 'N/A'}\n"
                f"Region: {instance.userprofile.region or 'N/A'}"
            )
            send_mail(
                subject="New User Registration",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cleysir54@gmail.com'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(post_save, sender=Cart)
def notify_cart_added(sender, instance, created, **kwargs):
    if created:
        try:
            message = (
                f"New cart item added.\n"
                f"User: {instance.user.username} ({instance.user.email})\n"
                f"Product: {instance.product.name}\n"
                f"Quantity: {instance.quantity}\n"
                f"Unit Price: TZS {instance.product.price}\n"
                f"Total Price: TZS {instance.total_price}\n"
                f"Added At: {instance.added_at}\n"
                f"User Phone: {instance.user.userprofile.phone or 'N/A'}\n"
                f"User Address: {instance.user.userprofile.address or 'N/A'}\n"
                f"User City: {instance.user.userprofile.city or 'N/A'}\n"
                f"User Region: {instance.user.userprofile.region or 'N/A'}"
            )
            send_mail(
                subject="New Cart Item Added",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cleysir54@gmail.com'],
                fail_silently=True,
            )
        except:
            pass


@receiver(post_save, sender=Request)
def notify_request_submitted(sender, instance, created, **kwargs):
    if created:
        try:
            send_mail(
                subject="New Product Request Submitted",
                message=f"New request from {instance.contact_name} ({instance.contact_email}) for {instance.product_name}. Final Price: TZS {instance.final_price}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cleysir54@gmail.com'],
                fail_silently=True,
            )
        except:
            pass