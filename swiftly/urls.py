from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from src import views

from django.conf import settings
from django.conf.urls.static import static

from src.customer import views as customer_views
from src.courier import views as courier_views, apis as courier_apis

# customer urls
customer_urlpatterns = [
    path('', customer_views.home, name='home'),
    path('profile/', customer_views.profile_page, name='profile'),
    path('payment_method/', customer_views.payment_method_page, name='payment_method'),
    path('create_job/', customer_views.create_job_page, name='create_job'),

    path('jobs/currrent/', customer_views.current_jobs_page, name='current_jobs'),
    path('jobs/archived/', customer_views.archived_jobs_page, name='archived_jobs'),
    path('jobs/job_ details/<job_id>/', customer_views.job_details_page, name='job_details'),
]

# courier urls
courier_urlpatterns = [
    path('', courier_views.home, name='home'),
    path('jobs/available/', courier_views.available_jobs_page, name='available_jobs'),
    path('jobs/available-job-details/<id>/', courier_views.available_job_details_page, name='available_job_details'),
    path('jobs/current/', courier_views.current_job_page, name='current_job'),

    path('api/jobs/available/', courier_apis.available_jobs_api, name='available_jobs_api'),
]

# main urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),
    path('', views.home, name='home'),

    path('sign-in/', auth_views.LoginView.as_view(template_name="sign_in.html"), name='login'),
    path('sign-out/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('sign-up/', views.sign_up, name='sign_up'),

    path('customer/', include((customer_urlpatterns, 'customer'))),
    path('courier/', include((courier_urlpatterns, 'courier'))),
]

# configuring media files url
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

