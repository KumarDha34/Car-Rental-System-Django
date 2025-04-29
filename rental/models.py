from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
import uuid
from django.core.exceptions import ValidationError
from datetime import date
# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        
        email=self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    fullname = models.CharField(max_length=255) 
    profile_pic=models.ImageField(upload_to="profile_pictures/",default="profile_pictures/default.jpg")
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Brand(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description = models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Car(models.Model):
    name=models.CharField(max_length=255)
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
    model=models.CharField(max_length=50)
    price_per_day=models.DecimalField(max_digits=8,decimal_places=2)
    image=models.ImageField(upload_to='cars/')
    availability=models.BooleanField(default=True)

    def is_available(self, start_date=None, end_date=None):
        from .models import Booking
        bookings = Booking.objects.filter(
            car=self,
            status__in=["Pending", "Confirmed"],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        return not bookings.exists()


    def __str__(self):
        return self.name

class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    PAID = 'Paid', 'Paid'
    FAILED = 'Failed', 'Failed'


class Booking(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Confirmed','Confirmed'),
        ('Cancelled','Cancelled')
    ]
    booking_code = models.CharField(default=uuid.uuid4, max_length=36, unique=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    car=models.ForeignKey(Car,on_delete=models.CASCADE)
    start_date=models.DateField()
    end_date=models.DateField()
    booked_on = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    location = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        # Prevent past dates
        if self.start_date < date.today():
            raise ValidationError("Start date cannot be in the past.")
        if self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")
        
    def calculate_total_price(self):
        days=(self.end_date-self.start_date).days+1
        return days*self.car.price_per_day
    def save(self, *args, **kwargs):
        self.total_price = self.calculate_total_price()
        super(Booking, self).save(*args, **kwargs)

class Payment(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=100)  # e.g., 'Credit Card', 'eSewa'
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.booking.booking_code} - {self.payment_status}"