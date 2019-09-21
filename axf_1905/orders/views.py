import datetime
import os
import time


# from alipay import AliPay
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse

from django_redis import get_redis_connection
import json

from market.models import Goods
from .models import Order, OrderDetail
from users.models import User

def index(request):

    # 1,判断用户有没有登陆
    # 如果没有登陆跳到登陆页面

    # 判断session里面有没有存用户名
    if not request.session.get('username'):
        return redirect(reverse('users:login'))


    # 生成订单的逻辑
    # 1，获取购物车中的数据，从redis中取数据
    username = request.session.get('username')
    redis_cli = get_redis_connection('cart')
    cart_data = json.loads(redis_cli.get(f"cart-{username}"))

    # 2，判断redis中商品的选中状态
    cart_dict = {}
    for cart in cart_data:
        if cart_data[cart]['selected'] == '1':
            # {'gid1':'count1', 'gid2':'count2'}
            cart_dict[int(cart)] = int(cart_data[cart]['count'])


    # 开启事务
    with transaction.atomic():

        # 创建事务的保存点
        save_id = transaction.savepoint()

        # 3，生成总订单信息
        user = User.objects.get(username=username)

        # 生成订单号:'20190102141414'+uid
        order_code = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)


        order = Order.objects.create(
            uid=user.id,
            order_code=order_code,
            total_count=sum(cart_dict.values()),
            total_amount=0,
            status=1
        )


        totalcount = 0
        # 4,生成子订单
        for gid, count in cart_dict.items():

            # 判断库存够不够

            # 悲观锁
            # good = Goods.objects.select_for_update().get(id=gid)

            while True:
                good = Goods.objects.get(id=gid) # storenums = 1

                if count > good.storenums:
                    # 回滚事务
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('商品库存不足')


                # 模拟并发操作
                # time.sleep(5)


                # 乐观锁，减库存的时候判断，当前的库存是否等于之前查询过的库存
                res = Goods.objects.filter(id=good.id, storenums=good.storenums).update(
                    storenums=good.storenums - count,
                    productnum=good.productnum + count
                )


                # 如果没有更新成功
                if not res:
                    continue  # 如果库存够，并发执行失败后，让他从新执行
                    # transaction.savepoint_rollback(save_id)
                    # return HttpResponse('当前人多，请等待')


                # 减库存加销量
                # good.storenums = good.storenums - count
                # good.productnum = good.productnum + count
                #
                # good.save()



                # 生成子订单
                OrderDetail.objects.create(
                    uid=user.id,
                    order_code=order_code,
                    goods_id=gid,
                    counts=count,
                    price=good.price
                )

                totalcount += good.price * count

                # 清除选中商品的redis数据
                del cart_data[str(gid)]

                break


        order.total_amount = totalcount
        order.save()

        # 重新添加redis数据
        redis_cli.set(f'cart-{username}', json.dumps(cart_data))

        transaction.savepoint_commit(save_id)


    # return HttpResponse('订单生成成功')
    return redirect(reverse("orders:orderpay", args=(order_code,)))



def not_pay(request):

    # 包括的订单的信息
    # 订单号、商品图片、商品的名字、商品的价格、商品数量
    username = request.session.get('username')
    user = User.objects.get(username=username)

    orders = Order.objects.filter(uid=user.id, status=1)

    '''
    数据格式
    {
      'order_code':[
        {'img':'', 'name': '', 'price': ''},  # 子订单的信息
        {'img':'', 'name': '', 'price': ''}
      ],
      'order_code':[
        {'img':'', 'name': '', 'price': ''},  # 子订单的信息
        {'img':'', 'name': '', 'price': ''}
      ]
    }
    '''
    data_dict = {}
    for order in orders:

        data_list = []
        orderdetails = OrderDetail.objects.filter(order_code=order.order_code)
        for orderdetail in orderdetails:

            good = Goods.objects.get(id=orderdetail.goods_id)
            good_dict = {
                'img': good.productimg,
                'name': good.productlongname,
                'price': orderdetail.price,
                'count': orderdetail.counts
            }

            data_list.append(good_dict)

        data_dict[order.order_code] = data_list


    context = {
        'data_dicts': data_dict
    }


    return render(request, 'order_list_not_pay.html', context)


def orderpay(request, order_code):

    order = Order.objects.get(order_code=order_code)

    data = []

    orderdetails = OrderDetail.objects.filter(order_code=order_code)
    for orderdetail in orderdetails:
        good = Goods.objects.get(id=orderdetail.goods_id)
        good_dict = {
            'img': good.productimg,
            'name': good.productlongname,
            'price': orderdetail.price,
            'count': orderdetail.counts
        }

        data.append(good_dict)


    context = {
        'totalamount': order.total_amount,
        'datas': data,
        'order_code':order_code
    }

    return render(request, 'order_detail.html', context)



# def pay(request, order_code):
#
#     alipay = AliPay(
#         appid='2016092700609211',
#         app_notify_url=None,  # 默认回调url
#         app_private_key_path=os.path.join(settings.BASE_DIR, "alipay/app_private_key.pem"),
#         alipay_public_key_path=os.path.join(settings.BASE_DIR, "alipay/alipay_public_key.pem"),
#         sign_type="RSA2",
#         debug=True
#     )
#
#     order = Order.objects.get(order_code=order_code)
#
#     # 生成登录支付宝连接
#     order_string = alipay.api_alipay_trade_page_pay(
#         out_trade_no=order_code,
#         total_amount=float(order.total_amount),
#         subject='商品支付信息',
#         return_url='http://127.0.0.1:8000/payback/',
#     )
#
#     alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
#     return redirect(alipay_url)
#
#
#
# # 支付宝回调接口
# def payback(request):
#
#     query_dict = request.GET
#     data = query_dict.dict()
#
#     # 获取并从请求参数中剔除signature
#     signature = data.pop('sign')
#
#     # 创建支付宝支付对象
#     alipay = AliPay(
#         appid='2016092700609211',
#         app_notify_url=None,  # 默认回调url
#         app_private_key_path=os.path.join(settings.BASE_DIR, "alipay/app_private_key.pem"),
#         alipay_public_key_path=os.path.join(settings.BASE_DIR, "alipay/alipay_public_key.pem"),
#         sign_type="RSA2",
#         debug=True
#     )
#     # 校验这个重定向是否是alipay重定向过来的
#     success = alipay.verify(data, signature)
#     if success:
#         order_code = data['out_trade_no']
#         Order.objects.filter(order_code=order_code).update(status=2)
#         return HttpResponse('支付成功')
#     else:
#         # 验证失败
#         return HttpResponse('支付失败')