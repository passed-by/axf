from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/$', views.index, name='index'),
    url(r'^not_pay/$', views.not_pay, name='not_pay'),
    url(r'^orderpay/(\d+)/$', views.orderpay, name='orderpay'),
    # url(r'^pay/(\d+)/$', views.pay, name='pay'),
    # url(r'^payback/$', views.payback, name='payback')
]