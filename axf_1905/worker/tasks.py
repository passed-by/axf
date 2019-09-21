import time
from celery import Celery

broker = 'redis://127.0.0.1:6379'
backend = 'redis://127.0.0.1:6379/0'
app = Celery('my_task', broker=broker, backend=backend)

#1,把费时的操作变成一个任务
@app.task
def add():
    for i in range(10):
        time.sleep(1)
        print(i)


def run():

    add.delay()  # 把费时的任务放入到队列里面

    print('run')