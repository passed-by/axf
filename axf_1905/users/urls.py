from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^sendsms/$', views.sendsms, name='sendsms'),
    url(r'^info/$', views.info, name='info'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^email/$', views.email, name='email'),
    url(r'^active/$', views.active, name='active'),
]