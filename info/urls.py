from django.conf.urls import patterns, url
from info import views
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
    url(r'^get/(?P<pk>[0-9]+)/$', views.user_get, name='user-get-api'),
    url(r'^login/$', views.obtain_auth_token, name='login-api'),
    url(r'^logout/$', views.logout_view, name='login-api'),
    url(r'^change/password/$', views.user_change_password, name='change-password-api'),
    url(r'^registration/$', views.user_registration, name='registration-api'),
    url(r'^create/$', views.user_registration_controller, name='registration-api'),
    url(r'^id_proofs/$', views.id_proof_list, name='id-proof-api'),
    url(r'^password/reset/$', views.password_reset_view, name='password-reset-api'),
    url(r'^password/reset/confirm/(?P<otp>[0-9]+)/$', views.password_reset_confirm_view, name='password-reset-confirm-api'),
    url(r'^otp/confirm/$', views.otp_valid, name='otp-confirm-api'),
    url(r'^active/$', views.staff_user_active, name='staff-active-api'),
)
