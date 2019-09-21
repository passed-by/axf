import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import FoodType, Goods
from django_redis import get_redis_connection

# Create your views here.
def index(request, typeid, twoid, sortid):
    # 1 取出分类信息
    foodtype = FoodType.objects.order_by("typesort")

    # 2 默认取出热销榜的数据
    # 先找出热销榜的分类id
    if typeid == '0':
        cid = foodtype[0].typeid
        childcate = foodtype[0].childtypenames
    else:
        cid = typeid
        childdata = FoodType.objects.get(typeid=cid)
        childcate = childdata.childtypenames

    # 找出分类id所对应的商品信息
    goods = Goods.objects.filter(categoryid=cid)

    # 找出二级分类id对应的所有商品，如果二级分类的id为0，那么找出一级分类对应的所有商品
    # 如果不为0，那么就要根据二级分类id查找商品
    if twoid != '0':
        goods = goods.filter(childcid=twoid)

    # 根据价格和销量排序
    order_data = [
        ['综合排序', '0'],
        ['价格升序', '1', 'price'],
        ['价格降序', '2', '-price'],
        ['销量升序', '3', 'productnum'],
        ['销量降序', '4', '-productnum'],
    ]

    # 如果排序的id是0，那么就不变
    # 如果是1，order_by('price')
    # 2, order_by('-price')
    # 3, order_by('productnum')
    # 4, order_by('-productnum')
    if sortid != '0':
        goods = goods.order_by(order_data[int(sortid)][2])

    # 找出大分类对应的所有子分类
    # 数据表中的格式 ：  "全部分类:0#酸奶乳酸菌:103537#牛奶豆浆:103538#面包蛋糕:103540
    # 转换成字典格式 {'0': '全部分类', '103537': '酸奶乳酸菌', '103538': '牛奶豆浆'}
    childcateone = childcate.split('#')  # ['全部分类:0', '进口零食:103547', '饼干糕点:103544']

    childcatetwo = {}
    for one in childcateone:
        onedata = one.split(':')
        childcatetwo[onedata[1]] = onedata[0]

    context = {
        'foodtype': foodtype,
        'goods': goods,
        'cid': int(cid),
        'childcatetwo': childcatetwo,
        'twoid': twoid,
        'order_data': order_data,
        'sortid': sortid
    }

    return render(request, 'market.html', context)


def savedata(request):
    # 1, 获取数据
    gid = request.POST.get('gid')
    count = request.POST.get('count')
    selected = request.POST.get('selected', '1')



    # 如果登陆，数据存储到redis里面

    # 如果request.session.get('username')有值，就代表用户已经登陆
    if request.session.get('username'):

        username = request.session.get('username')

        # 数据在redis里面怎么存储
        # 确定存储的格式，就是字典形式的字符串

        # 1，实例化redis对象
        redis_cli = get_redis_connection('cart')
        # 2,获取redis的购物车数据
        cookie_data = redis_cli.get(f'cart-{username}')

    else:

        # 先把cookie_data的值查出来
        cookie_data = request.COOKIES.get('cookie_data')

    # 如果cookie_data有数据
    if cookie_data:
        cookie_data = json.loads(cookie_data)
        # 如果cookie_data含有gid的数据就覆盖，如果没有就新增
        cookie_data[gid] = {'count': count, 'selected': selected}
    else: # 如果没有数据

        # 2, 把数据组装成格式为
        # { '商品的id':{'count':'购买的数量', 'selected':'商品的选中状态'} }
        # 放入cookie中
        cookie_data = {gid: {'count': count, 'selected': selected}}


    # 如果gid的数量是0，那么就删除此gid对应的数据
    if count == '0':
        del cookie_data[gid]


    # 3, cookie里面只能放字符串,所以需要把字典格式转成字符串
    cookie_data = json.dumps(cookie_data)
    res = JsonResponse({'data': 'ok'})

    if request.session.get('username'):
        redis_cli.set(f'cart-{username}', cookie_data)

    else:
        # 4, 设置cookie
        res.set_cookie('cookie_data', cookie_data)

    return res
