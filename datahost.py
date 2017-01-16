#!/usr/bin/python
# coding=utf-8

import socket
from ports import getcommonports


class DataHost(object):

    def __init__(self, ip):
        self.banner = ''
        self.result = ''
        self._ip = ip
        self.dicc_open_ports = {}

    def __del__(self):
        pass

    def __portscan(self, _host, _port):

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.10)
            self.result = sock.connect_ex((_host, _port))
            sock.send('GET HTTP/1.1 \r\n')
            self.banner = sock.recv(1024)
            sock.close()
        except:
            pass

    def ports(self):
        common_ports = getcommonports()
        print "Scaning ports for IP %s" % str(self._ip)
        for value in common_ports:
            self.__portscan(self._ip, value)
            if not self.result:
                self.dicc_open_ports[str(value)] = str(self.banner)
                print 'Port: [' + str(value) + '] Protocol: [' + str(common_ports[value]) + ']'
                print 'Banner: [' + str(self.banner) + ']'
        print "End scaning ports for IP %s" % str(self._ip)
        return self.dicc_open_ports
