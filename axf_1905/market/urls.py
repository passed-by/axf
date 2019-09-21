from django.conf.urls import url

from . import views

urlpatterns = [
    url('^market/(\d+)/(\d+)/(\d+)/$', views.index, name='index'),
    url('^savedata/$', views.savedata, name='savedata')
]