from django.db import models

# Create your models here.

# 订单总表
# `uid` int(11) NOT NULL,
# `order_code` varchar(100) NOT NULL,
# `total_count` int(11) NOT NULL,
# `total_amount` double NOT NULL,
# `status` smallint(6) NOT NULL,
class Order(models.Model):
    uid = models.IntegerField(verbose_name="用户id")
    order_code = models.CharField(max_length=100, verbose_name="订单编号")
    total_count = models.IntegerField(verbose_name="订单总数量")
    total_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="订单总金额")
    status = models.SmallIntegerField(verbose_name="1未支付，2未发货，3未收货")

    class Meta:
        db_table = 'axf_order'



# 订单子表
# `uid` int(11) NOT NULL,
# `order_code` varchar(100) NOT NULL,
# `goods_id` int(11) NOT NULL,
# `counts` int(11) NOT NULL,
# `price` double NOT NULL,
class OrderDetail(models.Model):
    uid = models.IntegerField(verbose_name="用户id")
    order_code = models.CharField(max_length=100, verbose_name="订单编号")
    goods_id = models.IntegerField(verbose_name="商品id")
    counts = models.IntegerField(verbose_name="商品数量")
    price = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="商品单价")

    class Meta:
        db_table = 'axf_order_detail'
