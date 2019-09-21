from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^index/$', views.index, name='index')  # 首页路由
]