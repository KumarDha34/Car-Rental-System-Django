from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.http import HttpResponse
from .forms import LoginForm,UserSignupForm,ProfileUpdateForm
from django.db.models import Q
from datetime import date
from .models import CustomUser,Brand,Car,Booking,Payment
from django.contrib.auth.decorators import login_required
from .forms import BrandForm,CarForm,BookingForm
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Sum
# Create your views here.


# Index View (Home Page)
def index(request):
    return render(request, 'rental/index.html')


# User Signup VIew
def user_signup(request):
    if request.method=="POST":
        form=UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Account created! Please Login")
            return redirect("user_login")
    else:
        form=UserSignupForm()
    return render(request,'rental/signup.html',{"form":form})


# User and Admin Login View
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                if user.is_admin:
                    return redirect("admin_dashboard")  # Redirect Admins
                else:
                    return redirect("user_dashboard")  # Redirect Users
            else:
                messages.error(request, "Invalid email or password!")
    else:
        form = LoginForm()

    return render(request, "rental/login.html", {"form": form}) 
    
#LogoutView
def user_logout(request):
    logout(request)
    return redirect("user_login")

def user_dashboard(request):
    user=request.user
    bookings=Booking.objects.filter(user=user)
    upcoming_bookings = bookings.filter(status='Confirmed', start_date__gte=date.today()).order_by('start_date')[:3]
    context = {
        'upcoming_bookings': upcoming_bookings,
        'total_bookings': bookings.count(),
        'completed_trips': bookings.filter(status='Completed').count(),
        'cancelled_trips': bookings.filter(status='Rejected').count(),
    }
    return render(request,'rental/user_dashboard.html',context)

def admin_dashboard(request):
    total_cars = Car.objects.count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status="Pending").count()
    confirmed_bookings = Booking.objects.filter(status="Confirmed").count()
    cancelled_bookings = Booking.objects.filter(status="Cancelled").count()
    active_users = CustomUser.objects.filter(is_superuser=False).count()

    # Calculate total earnings from successful payments
    total_earnings = Payment.objects.filter(payment_status="Paid").aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'total_cars': total_cars,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'active_users': active_users,
        'total_earnings': total_earnings,
    }

    return render(request, 'rental/admin_dashboard.html', context)

# Brand 
@login_required
def add_brand(request):
    if request.method=="POST":
        form=BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_brands')
    else:
        form=BrandForm()
    return render(request,'rental/add_brand.html',{'form':form})

@login_required
def manage_brands(request):
    brands=Brand.objects.all()
    query=request.GET.get('search')

    if query:
        brands=brands.filter(name__icontains=query)
    
    #pagination
    paginator=Paginator(brands,4)
    page=request.GET.get('page')

    try:
        brands=paginator.page(page)
    except PageNotAnInteger:
        brands=paginator.page(1)
    except EmptyPage:
        brands=paginator.page(paginator.num_pages)
    return render(request,'rental/manage_brands.html',{'brands':brands})

@login_required
def edit_brand(request,brand_id):
    brand=get_object_or_404(Brand,id=brand_id)
    if request.method=="POST":
        form=BrandForm(request.POST,instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request,'Brand Updates Successfully')
            return redirect('manage_brands')
    else:
        form = BrandForm(instance=brand)
    return render(request,'rental/edit_brands.html',{'form':form})

@login_required
def delete_brand(request,brand_id):
    brand=get_object_or_404(Brand,id=brand_id)
    if request.method=="POST":
        brand.delete()
        messages.success(request,'Brand is Deleted Successfully!')
        return redirect('manage_brands')
    return render(request,'rental/delete_brand.html',{'brand':brand})

@login_required
def add_car(request):
    if request.method=="POST":
        form=CarForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,'Car Added Successfully!')
            return redirect('manage_cars')
    else:
        form=CarForm()
    return render(request,'rental/add_car.html',{'form':form})

@login_required
def manage_cars(request):
    cars=Car.objects.all()
    query=request.GET.get('search')

    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(model__icontains=query)
        )
    
    #pagination
    paginator=Paginator(cars,4)
    page=request.GET.get('page')

    try:
        cars=paginator.page(page)
    except PageNotAnInteger:
        cars=paginator.page(1)
    except EmptyPage:
        cars=paginator.page(paginator.num_pages)
    return render(request,'rental/manage_cars.html',{'cars':cars})

@login_required
def edit_car(request,car_id):
    car=get_object_or_404(Car,id=car_id)
    if request.method=="POST":
        form=CarForm(request.POST,instance=car)
        if form.is_valid():
            form.save()
            messages.success(request,"Car Updated Successfully")
            return redirect("manage_cars")
    else:
        form=CarForm(instance=car)
    return render(request,'rental/edit_car.html',{'form':form})

@login_required
def delete_car(request,car_id):
    car=get_object_or_404(Car,id=car_id)
    if request.method=="POST":
        car.delete()
        messages.success(request,"Car deleted Successfully")
        return redirect("manage_cars")
    return render(request,'rental/delete_car.html',{'car':car})

@login_required
def user_list(request):
    query = request.GET.get('search')
    users = CustomUser.objects.filter(is_admin=False)

    if query:
        users = users.filter(
            Q(fullname__icontains=query) |
            Q(email__icontains=query)
        )

    # pagination
    paginator = Paginator(users, 4)
    page = request.GET.get('page')

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    return render(request, 'rental/user_list.html', {'users': users})

# Car list
@login_required
def car_list(request):
    # Fetch all brands and cars (adjust based on your filtering logic)
    brands = Brand.objects.all()
    cars = Car.objects.all()
    
    # Handle search and brand filter
    search = request.GET.get('search', '')
    brand_id = request.GET.get('brand', '')
    start_date=request.GET.get('start_date')
    end_date=request.GET.get('end_date')
    
    if search:
        cars = cars.filter(
            Q(name__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(model__icontains=search)
        )
    if brand_id:
        cars = cars.filter(brand__id=brand_id)
    # Filters by availability
    if start_date and end_date:
        cars=[car for car in cars if car.is_available(start_date,end_date)]
    # Pagination logic
    paginator = Paginator(cars, 3)  # Show 10 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cars': page_obj,
        'brands': brands,
        'search': search,
        'brand': brand_id,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'rental/car_list.html', context)

@login_required
def car_details(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Check if the car is booked and not available due to either:
    # - Pending booking (waiting for admin approval)
    # - Confirmed booking with payment done
    current_bookings = Booking.objects.filter(
        car=car
    ).filter(
        Q(status="Pending") |
        Q(status="Confirmed", payment__payment_status="Paid")
    )

    not_available = current_bookings.exists()

    return render(request, 'rental/car_details.html', {
        'car': car,
        'not_available': not_available
    })


import hmac
import hashlib
import base64
import time

SECRET_KEY = "8gBm/:&EnhH.1/q"

def generate_signature(secret_key, total_amount, transaction_uuid, product_code):
    message = f"{total_amount}{transaction_uuid}{product_code}"
    hmac_obj = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
    return base64.b64encode(hmac_obj.digest()).decode('utf-8')

@login_required
def book_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car
            booking.user = request.user
            booking.total_price = booking.calculate_total_price()
            booking.status = 'Pending'  # Set status to Pending
            booking.save()

            messages.success(request, 'Booking created successfully. Please wait for admin approval.')
            return redirect('my_bookings')  # Redirect to My Bookings
    else:
        form = BookingForm()

    return render(request, 'rental/book_car.html', {'car': car, 'form': form})

@login_required
def my_bookings(request):
    bookings=Booking.objects.filter(user=request.user)

    return render(request, 'rental/my_bookings.html', {'bookings': bookings})


@login_required
def manage_bookings(request):
    bookings = Booking.objects.all().order_by('-id')

    return render(request, 'rental/manage_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        action = request.POST.get('action')

        if action == 'approve':
            booking.status = 'Confirmed'
            booking.save()
            # ✅ Do NOT delete, allow user to proceed with payment

        elif action == 'reject':
            booking.status = 'Cancelled'
            booking.save()

    return redirect('manage_bookings')


def update_payment_status(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    payment = Payment.objects.get(booking=booking)

    if payment.payment_status == 'Paid':
        booking.payment_status = 'Paid'
        booking.save()

    return redirect('booking_details', booking_id=booking.id)


@login_required
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != "Confirmed":
        messages.error(request, "Payment is only allowed after admin approval.")
        return redirect('my_bookings')

    transaction_uuid = f"BOOK{booking.id}_{int(time.time())}"
    booking.booking_code = transaction_uuid
    booking.save()

    signature = generate_signature(
        SECRET_KEY,
        booking.total_price,
        transaction_uuid,
        "EPAYTEST"
    )

    params = {
        'amt': str(booking.total_price),
        'txAmt': '0',
        'psc': '0',
        'pdc': '0',
        'tAmt': str(booking.total_price),
        'pid': transaction_uuid,
        'scd': 'EPAYTEST',
        'su': f"http://localhost:8000/payment_success/{transaction_uuid}/",
        'fu': f"http://localhost:8000/payment_failure/",
        'signature': signature,
    }

    return render(request, 'rental/payment_form.html', params)


@login_required
def payment_success(request, booking_code):
    try:
        booking = Booking.objects.get(booking_code=booking_code)

        amt = request.GET.get('amt')
        refId = request.GET.get('refId')

        if amt and refId:
            # Save payment details
            Payment.objects.create(
                booking=booking,
                payment_method="eSewa",
                transaction_id=refId,
                amount=amt,
                payment_status="Paid"
            )

            # Update booking payment_status
            booking.payment_status = "Paid"
            booking.save()

            messages.success(request, "Payment successful!")

    except Booking.DoesNotExist:
        messages.error(request, "Invalid booking code.")
        return redirect('my_bookings')

    return render(request, 'rental/payment_success.html', {
        'booking': booking,
        'booking_code': booking_code
    })

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'rental/profile.html', {'form': form, 'user': user})
