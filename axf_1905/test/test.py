import time
from threading import Thread


def run1():
    time.sleep(2)
    print('run1')


def run2():
    time.sleep(2) 
    print('run2')



if __name__ == '__main__':

    t1 = Thread(target=run1)
    t2 = Thread(target=run2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
    print('main')