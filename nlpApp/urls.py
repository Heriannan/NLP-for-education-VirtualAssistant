from django.conf.urls import url
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^courseEnquire/$', views.url_courseEnquire, name='courseEnquire'),
    url(r'^courseRegistration/$', views.url_courseRegistration, name='courseRegistration'),
    url(r'^courseDetail/$', views.url_courseDetail, name='courseDetail'),
    url(r'^courseReport/$', views.url_courseReport, name='courseReport'),
    url(r'^login_authentication/$', views.login_authentication, name='login_authentication'),
    url(r'^signup_account/$', views.signup_account, name='signup_account'),
    url(r'^ajax_courseRegistration/$', views.ajax_courseRegistration, name='ajax_courseRegistration'),
    url(r'^ajax_courseUpdate/$', views.ajax_courseUpdate, name='ajax_courseUpdate'),
    url(r'^ajax_search/$', views.ajax_search, name='ajax_search'),
    ]