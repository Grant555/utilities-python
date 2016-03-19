#
# coding: utf-8
#
# Author: Christopher Lee
# CnBlog: http://www.cnblogs.com/ChrisCabin
# GitHub: https://www.github.com/ChrisLeeGit
# 
# Version: 0.1
# Description: 基于paramiko模块,创建反向SSH隧道. 可以创建多条在后台运行的反向隧道.
# Reference: https://github.com/paramiko/paramiko/blob/master/demos/rforward.py
#

import sys
import os
import paramiko
import threading
import socket
import select

g_verbose = True

# 最多可以建立的tunnel个数,每个tunnel的id由用户确定
g_max_tunnels = 10


def verbose(s):
    if g_verbose:
        print(s)


def check_address(address=None):
    assert isinstance(address, tuple), \
        'Address is not `tuple` type'.format(address)

    assert isinstance(address[0], str), \
        'IP is not `str` type'.format(address[0])

    assert isinstance(address[1], int), \
        'Port is not `int` type'.format(address[1])


class TunnelThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=None):
        super(TunnelThread, self).__init__(group, target, name, args)
        self._en_thread = True

    def stop(self):
        verbose('stop the thread.')
        threading.Thread._stop(self)


class ReverseTunnelForwarder(object):
    def __init__(self,
                 ssh_address=None,
                 ssh_username=None,
                 ssh_password=None,
                 remote_bind_address=None,
                 local_bind_address=None,
                 set_keepalive=0.0,
                 compress=False
                 ):
        self.ssh_address = ssh_address
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.remote_bind_address = remote_bind_address
        self.local_bind_address = local_bind_address
        self.set_keepalive = set_keepalive
        self.compress = compress

        # 检查传入的地址,确保没有问题
        check_address(self.ssh_address)
        check_address(self.local_bind_address)
        check_address(self.remote_bind_address)

        # 创建一个ssh client,并完成初始化
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport = None

        # 一个字典,用于存放要建立的tunnel
        self.reverse_tunnels = dict()

    def _get_transport(self):

        # 尝试去连接到远程服务器
        try:
            self.ssh_client.connect(self.ssh_address[0],
                                    self.ssh_address[1],
                                    username=self.ssh_username,
                                    password=self.ssh_password,
                                    compress=self.compress)
            transport = self.ssh_client.get_transport()
            transport.set_keepalive(self.set_keepalive)

            verbose('Connected to host "{}:{}"'.format(self.ssh_address[0],
                                                       self.ssh_address[1]))
            return transport
        except Exception as e:
            print('Failed to connect to ssh host "{}:{}"'.
                  format(str(e), self.ssh_address[0], self.ssh_address[1]))
            sys.exit(1)

    @staticmethod
    def _handler(chan, host, port):
        sock = socket.socket()
        try:
            sock.connect((host, port))
        except Exception as e:
            verbose('Forwarding request to {}:{} failed: {}'.format(host, port, e))
            return

        verbose('Open tunnel: {} -> {} -> {}'.format(chan.origin_addr, chan.getpeername(), (host, port)))

        while True:
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                sock.send(data)
        chan.close()
        sock.close()
        verbose('Tunnel closed from {}'.format(chan.origin_addr))

    def _build_reverse_forward_tunnel(self, remote_bind_address, local_bind_address):
        verbose('build_reverse_forward_tunnel: {}:{}'.format(remote_bind_address, local_bind_address))
        self.transport.request_port_forward(remote_bind_address[0], remote_bind_address[1])

        while True:
            chan = self.transport.accept(1000)
            if chan is None:
                continue
            tunnel_tr = TunnelThread(target=self._handler,
                                     args=(chan, (local_bind_address[0], local_bind_address[1])))

            # tunnel_tr = threading.Thread(target=self._handler,
            #                              args=(chan, local_bind_address[0],
            #                                    local_bind_address[1]))
            tunnel_tr.setDaemon(True)
            tunnel_tr.start()
            tunnel_tr.stop()

    def add_tunnel(self, tunnel_id, remote_bind_address, local_bind_address):
        assert isinstance(tunnel_id, str)
        check_address(remote_bind_address)
        check_address(local_bind_address)

        if tunnel_id in self.reverse_tunnels.keys():
            print('Error: same tunnel id exists')
            return None
        elif len(self.reverse_tunnels) > g_max_tunnels:
            print('Error: too many tunnels exist')
            return None
        else:
            thr = threading.Thread(target=self._build_reverse_forward_tunnel,
                                   args=(remote_bind_address, local_bind_address))
            thr.start()

            # 保存下新启动的线程
            self.reverse_tunnels[tunnel_id] = (remote_bind_address, local_bind_address)

            return thr

    def start(self):
        self.transport = self._get_transport()
        self.add_tunnel('0', self.remote_bind_address, self.local_bind_address)

    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()


def main():
    tunnel = ReverseTunnelForwarder(('lingfeimo.com', 22),
                                    'chris',
                                    'chris',
                                    ('0.0.0.0', 2288),
                                    ('127.0.0.1', 22))

    tunnel.start()
    tunnel.add_tunnel('1', ('0.0.0.0', 2289), ('127.0.0.1', 22))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('C-c: port forwarding stopped')
        sys.exit(0)
