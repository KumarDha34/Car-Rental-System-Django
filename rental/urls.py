from django.urls import path
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path('', views.index, name='index'),
    path("signup/",views.user_signup,name="user_signup"),
    path('login/', views.user_login, name='user_login'),
    path('accounts/login/', RedirectView.as_view(url='/login/', permanent=False)),
    path("logout/",views.user_logout,name="user_logout"),

    # Dashboard
    path('user_dashboard/',views.user_dashboard,name="user_dashboard"),
    path('admin_dashboard/',views.admin_dashboard,name="admin_dashboard"),

    #Brand Management
    path('brand/add/', views.add_brand, name='add_brand'),
    path('brand/manage/', views.manage_brands, name='manage_brands'),
    path('brand/edit/<int:brand_id>/', views.edit_brand, name='edit_brand'),
    path('brand/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),

    # Car Management
    path('car/add/',views.add_car,name='add_car'),
    path('car/manage/',views.manage_cars,name='manage_cars'),
    path('car/edit/<int:car_id>/',views.edit_car,name='edit_car'),
    path('car/delete/<int:car_id>/',views.delete_car,name='delete_car'),

    # User List
    path('car/user/',views.user_list,name='user_list'),
    # Car List
    path('cars_list/',views.car_list,name='car_list'),
    # Car Details
    path('car_details/<int:car_id>/',views.car_details,name='car_details'),
    #Book
    path('book/<int:car_id>/',views.book_car,name='book_car'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('manage_bookings/', views.manage_bookings, name='manage_bookings'),
    path('update_booking_status/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('initiate_payment/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment_success/<str:booking_code>/', views.payment_success, name='payment_success'),
    # user Profile
    path('profile/',views.profile_view,name="profile")
]
