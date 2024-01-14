"""
URL configuration for STARTUP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from home import views as home_views
#from home.views import FirebaseToCSVView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('',auth_views.LoginView.as_view(template_name='login/login.html'), name='Login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='login/logout.html'), name='Logout'),
    path('home',home_views.home, name='home-user'),
    path('crops', home_views.crops, name='crops-user'),
    path('mycrop/<iot_code>/<sensor>/<crop>', home_views.mycrop, name='mycrop-user'),
    path('reg_iot', home_views.iot_reg, name='reg-iot-user'),
    #path('iot_registration', home_views.iot_reg, name='reg_iot-user'),
    #path('export-firebase-to-csv/', FirebaseToCSVView.as_view(), name='export_firebase_to_csv'),
    #trylngg
    #ON/OFF FOR MOTOR AND TEMP SUBMIT
    path('onButton',home_views.onButton, name='onButton'),
    path('offButton', home_views.offButton, name='offButton'),
    path('temp',home_views.temp, name='temp'),
    #LOGIN/LOGOUT/FORGOT
    path('', include('login.urls')),
    path('',auth_views.LoginView.as_view(template_name='login/login.html'), name='Login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='login/logout.html'), name='Logout'),
    path('forgot_password/',
         auth_views.PasswordResetView.as_view(template_name='login/forgotpass.html'), 
         name='forgot_password'),

    path('password-reset/done',
        auth_views.PasswordResetDoneView.as_view(template_name='login/forgotpass_done.html'), 
        name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='login/forgotpass_confirm.html'), 
        name='password_reset_confirm'),    

    path('password-reset/complete',
        auth_views.PasswordResetCompleteView.as_view(template_name='login/forgotpass_complete.html'), 
        name='password_reset_complete'),

    #Settings
    path('settings',home_views.settings, name='settings'),
    path('password',auth_views.PasswordChangeView.as_view(template_name='home/password.html'), name='password'),
    path('password-change/complete',
        auth_views.PasswordChangeDoneView.as_view(template_name='home/pass_comp.html'), 
        name='password_change_done'),
    path('notifications', home_views.notifCount, name='notifications'),
    path('crop-progress-report/<iot_code>/<sensor>/<crop>', home_views.crop_progress_report_view, name='crop_progress_report'),
    path('irrigation-records/<iot_code>/<sensor>/<crop>', home_views.irrigation_records_view, name='irrigation_records-user'),
    path('remove',home_views.remove, name='remove'),
    path('harvest1',home_views.harvest1, name='harvest1'),
    path('history',home_views.history, name='history'),
    
    ]
    
