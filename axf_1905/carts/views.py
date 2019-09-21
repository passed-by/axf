import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from market.models import Goods
from django_redis import get_redis_connection

def index(request):

    if request.session.get('username'):
        username = request.session.get('username')
        redis_cli = get_redis_connection('cart')
        data = redis_cli.get(f'cart-{username}')
    else:
        # 1,从cookie里面取出数据
        data = request.COOKIES.get('cookie_data')


    totalprice = 0
    # 2，先判断cookie里面有没有数据
    if data:
        # 2,把字符串转成字典
        data = json.loads(data)
        print(data)
        print(type(data))
        # 3，通过商品的id，把商品数据取出来
        data_list = []
        for d in data: # {gid:{'count':1, 'selected':1}}

            print(d)
            print(type(d))
            # 查数据
            goods = Goods.objects.get(id=d)

            # 把需要用到的数据，组装成字典格式
            data_dict = {
                'id': goods.id,
                'img': goods.productimg,
                'name': goods.productlongname,
                'price': goods.price,
                'num': data[d]['count'],
                'selected': data[d]['selected'],
            }

            if data[d]['selected'] == '1':
                totalprice += goods.price * int(data[d]['count'])

            data_list.append(data_dict)

    else:
        data_list = []


    context = {
        'data_list': data_list,
        'totalprice': totalprice
    }


    return render(request, 'cart.html', context)





def selects(request):
    # 1,获取状态的值
    selected = request.POST.get('selected')

    # 2,取出cookie_data的值
    if request.session.get('username'):
        username = request.session.get('username')
        redis_cli = get_redis_connection('cart')
        cookie_data = redis_cli.get(f'cart-{username}')
    else:
        cookie_data = request.COOKIES.get('cookie_data')


    cookie_data = json.loads(cookie_data)

    # 3，改变每个商品的选中状态
    for data in cookie_data:
        cookie_data[data]['selected'] = selected

    # 3,设置cookie
    cookie_data = json.dumps(cookie_data)

    res = JsonResponse({'data': 'ok'})

    if request.session.get('username'):
        redis_cli.set(f'cart-{username}', cookie_data)
    else:
        res.set_cookie('cookie_data', cookie_data)

    return res