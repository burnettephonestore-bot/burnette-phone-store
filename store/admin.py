from django.contrib import admin
from .models import Product, Update, Request, Bank, MobileMoney, SiteSettings, Cart, UserProfile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'media_type', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'valid_until', 'created_at')
    list_filter = ('type', 'valid_until')

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'product_name', 'base_price', 'discount', 'final_price', 'wants_delivery', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'wants_delivery')
    search_fields = ('contact_name', 'contact_email', 'product_name')
    readonly_fields = ('product', 'product_name', 'base_price', 'discount', 'final_price', 'explanation', 'contact_name', 'contact_phone', 'contact_email', 'wants_delivery', 'region', 'district', 'payment_method', 'payment_target', 'created_at')
    fields = ('product', 'product_name', 'base_price', 'discount', 'final_price', 'explanation', 'contact_name', 'contact_phone', 'contact_email', 'wants_delivery', 'region', 'district', 'payment_method', 'payment_target', 'status', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ()

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_number')

@admin.register(MobileMoney)
class MobileMoneyAdmin(admin.ModelAdmin):
    list_display = ('name', 'number')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('title', 'admin_username', 'admin_email')
    fields = ('title', 'logo_url', 'logo_file', 'theme_color', 'admin_username', 'admin_password', 'admin_name', 'admin_email', 'admin_phone')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'product__name')

    def has_add_permission(self, request):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'city', 'region')
    search_fields = ('user__username', 'user__email', 'phone')
