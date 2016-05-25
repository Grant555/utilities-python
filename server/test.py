#!/user/bin/python3
# 文件：.py
# 作者：Christopher Lee
# 博客：http://www.cnblogs.com/chriscabin
# 主页：https://www.github.com/chrisleegit
# 邮箱：christopherlee1993@outlook.com
# 功能：
# 参数：
# 版本：0.1
# 备注：无
# 日志：
import random
import socket
import subprocess
import socket
import threading
import time


class MyThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        server = socket.socket()
        server.bind(('0.0.0.0', 8888))
        server.listen()
        while True:
            print('Hello, world')
            time.sleep(1)


class StartMyThread:
    def __init__(self):
        self._thread = None

    def start(self):
        self._thread = MyThread()
        self._thread.start()


def test_1():
    while True:
        time.sleep(1)
        print('test_1 is alive')


def test_2():
    while True:
        time.sleep(1)
        print('test_2 is alive')


def main():
    StartMyThread().start()
    threading.Thread(target=test_1).start()
    threading.Thread(target=test_2).start()
    MyThread().start()

if __name__ == '__main__':
    main()
