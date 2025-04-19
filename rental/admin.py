from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser,Brand,Car,Booking,Payment
# Register your models here.
class CustomUserAdmin(UserAdmin):
    model=CustomUser
    list_display=['email','fullname','phone','is_staff','is_active','profile_pic']
    list_filter=['is_staff','is_active']
    search_fields=['email','fullname']
    ordering=['email']

    # fields to display on the user detail page
    fieldsets=(
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('fullname', 'phone','profile_pic')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates',{'fields':('last_login',)}),
    )
    # the fieldsset for creating new users
    add_fieldsets=(
        (None,{
            'classes':('wide',),
            'fields':('email','password1','password2','fullname','phone','is_staff','is_active')
        }),
    )
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Brand)

class CarAdmin(admin.ModelAdmin):
    list_display=('name','brand','model','price_per_day','availability')
    search_fields=('name','brand_name')

admin.site.register(Car,CarAdmin)
admin.site.register(Booking)
admin.site.register(Payment)