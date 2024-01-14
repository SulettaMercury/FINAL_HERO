from django.urls import path
from . import views

urlpatterns = [
    path('register',views.register, name='register'),
    #path('forgot_password', views.forgot_pass, name='forgot_password'),
]