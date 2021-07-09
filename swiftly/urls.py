from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from src import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('', views.home, name='home'),

    path('sign-in/', auth_views.LoginView.as_view(template_name="sign_in.html"), name='login'),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('sign-up/', views.sign_up, name='sign_up'),

    path('customer/', views.customer_page, name='customer_page'),
    path('courier/', views.courier_page, name='courier_page'),
]
