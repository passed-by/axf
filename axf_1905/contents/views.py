from django.http import HttpResponse
from django.shortcuts import render
from . import models

# Create your views here.
def index(request):

    # 取轮播图数据
    wheel = models.AxfWheel.objects.all()

    # 取出导航数据
    nav = models.AxfNav.objects.all()

    # 取出必买数据
    mustbuy = models.MustBuy.objects.all()

    # 取出商店数据
    shop1 = models.AxfShop.objects.all()[0:1]
    shop2 = models.AxfShop.objects.all()[1:3]
    shop3 = models.AxfShop.objects.all()[3:7]
    shop4 = models.AxfShop.objects.all()[7:11]

    context = {
        "wheels": wheel,
        "navs": nav,
        "mustbuys": mustbuy,
        'shops1': shop1,
        'shops2': shop2,
        'shops3': shop3,
        'shops4': shop4,
    }

    return render(request, 'home.html', context)