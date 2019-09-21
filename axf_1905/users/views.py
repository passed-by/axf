import os
import random

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import requests
from django.urls import reverse
from django_redis import get_redis_connection

from common.func import upload_to_qiniu, cookie_to_redis, send_email
from orders.models import Order
from users.models import User
from django.core.mail import send_mail

# Create your views here.

def login(request):
    if request.method == 'POST':
        # 1,接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 2，判断参数
        user = User.objects.filter(username=username)

        if not user.exists():
            return HttpResponse('用户不存在')

        if not check_password(password, user[0].password):
            return HttpResponse('密码错误')

        # 3、处理逻辑
        # 保存用户的登陆状态
        request.session['username'] = username

        res = redirect(reverse('users:info'))

        # 4,返回响应
        return cookie_to_redis(request, res)

    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':

        # 1,接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        avatar = request.FILES.get('avatar')
        phone = request.POST.get('phone')
        smscode = request.POST.get('smscode')

        # 2，判断参数
        # 判断用户名不能重复
        # User.objects.filter(username=username).count()

        # try:
        #     User.objects.get(username=username)
        # except User.DoesNotExist:
        #     pass

        res = User.objects.filter(username=username).exists()
        if res:
            return HttpResponse('用户名已存在')

        if password != password_confirm:
            return HttpResponse('密码不一致')

        # 判断验证码是否过期
        # redis_cli = get_redis_connection()
        # code = redis_cli.get(f'sms-{phone}')
        # if not code:
        #     return HttpResponse('验证码过期')
        #
        # if smscode != code.decode():
        #     return HttpResponse('验证码输入错误')

        # 3，处理逻辑

        user = User.objects.create(
            username=username,
            password=make_password(password),
            phone=phone,
            avatar=avatar,  # 新增的数据的时候，自动上传图片
        )

        upload_to_qiniu(avatar.name, os.path.join(settings.MEDIA_ROOT, 'uploads', avatar.name))

        user.avatar = 'http://py25tqtvc.bkt.clouddn.com/' + avatar.name

        user.save()

        # 4，返回响应
        return redirect(reverse('users:login'))

    else:
        return render(request, 'register.html')


# 发短信
def sendsms(request):
    smscode = random.randint(1000, 9999)
    phone = request.POST.get('phone')

    data = {
        "sid": "8036ece41e07ea5340794286185f9214",
        "token": "8a9c9099eb825ea314bcb620f9fdbc6b",
        "appid": "cceff1236cee4e1e87b87186dc10ad27",
        "templateid": "493813",
        "param": smscode,
        "mobile": phone,
    }

    # 用云之讯第三方发短信
    res = requests.post('https://open.ucpaas.com/ol/sms/sendsms', json=data)

    res = res.json()

    if res['code'] == '000000':

        # 保存验证码，保存在缓存里面，给一个过期时间
        # 实例化redis
        redis_cli = get_redis_connection()

        redis_cli.set(f'sms-{phone}', smscode, 60)

        return JsonResponse({'res': 'yes'})
    else:
        return JsonResponse({'res': 'no'})


def info(request):
    login = False
    user = ''
    not_pay = 0
    not_reveice = 0

    # 做登陆判断，如果登陆成功，用户信息页需要显示登陆的信息
    if request.session.get('username'):
        login = True

        # 获取用户信息
        username = request.session.get('username')

        user = User.objects.get(username=username)

        # 查询订单的状态，1代表为支付，2代表为收获
        not_pay = Order.objects.filter(uid=user.id, status=1).count()
        not_reveice = Order.objects.filter(uid=user.id, status=2).count()

    context = {
        'login': login,
        'user': user,
        'not_pay': not_pay,
        'not_reveice': not_reveice
    }

    return render(request, 'mine.html', context)


def logout(request):

    # 退出逻辑,删除session
    del request.session['username']

    return redirect(reverse('users:login'))


def email(request):


    username = request.session.get('username')
    user = User.objects.get(username=username)

    if request.method == 'GET':

        context = {
            'user': user
        }

        return render(request, 'email.html', context)

    else:

        # 获取邮箱数据
        # 获取type值
        email = request.POST.get('email')
        types = request.POST.get('type')

        # 如果types为1，表示是保存邮箱操作
        if types == '1':
            User.objects.filter(username=username).update(email=email)

            return redirect(reverse("users:email"))

        elif types == '2': # 代表激活邮件

            email = request.POST.get('email_active')

            send_email.delay(email) # 把任务放入队列

            return HttpResponse('发送邮件成功，请激活')



def active(request):

    # 接收邮箱，激活邮箱
    email = request.GET.get('email')
    User.objects.filter(email=email).update(is_active=1)

    return redirect(reverse('users:email'))