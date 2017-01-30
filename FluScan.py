#!/usr/bin/python
# coding=utf-8

import datetime
import ipaddress
from struct import unpack
from socket import AF_INET, inet_pton
from geolocate import GeoLocate
from datahost import DataHost
from mongo import ConexionMongoDB


def ip_private(_ip):
    ip = unpack('!I', inet_pton(AF_INET, _ip))[0]
    l = (
        [2130706432, 4278190080],
        [3232235520, 4294901760],
        [2886729728, 4293918720],
        [167772160, 4278190080]
    )
    for addr in l:
        if (ip & addr[1]) == addr[0]:
            return True
    return False


def ip_order(_ip1, _ip2):
    _ip1_split = _ip1.split('.')
    _ip2_split = _ip2.split('.')
    for i in range(0, 4):
        if _ip2_split[i] < _ip1_split[i]:
            return _ip1, _ip2
        elif _ip2_split[i] > _ip1_split[i]:
            return _ip2, _ip1
    return _ip2, _ip1


def ip_add(_ip):
    _ip_split = _ip.split('.')
    if int(_ip_split[3]) < 255:
        return "%s.%s.%s.%d" % (_ip_split[0], _ip_split[1], _ip_split[2], int(_ip_split[3])+1)
    elif int(_ip_split[2]) < 255:
        return "%s.%s.%d.%d" % (_ip_split[0], _ip_split[1], int(_ip_split[2])+1, 0)
    elif int(_ip_split[1]) < 255:
        return "%s.%d.%d.%d" % (_ip_split[0], int(_ip_split[1])+1, 0, 0)
    elif int(_ip_split[0]) < 255:
        return "%d.%d.%d.%d" % (int(_ip_split[0])+1, 0, 0, 0)
    else:
        return _ip

    
def cloudflare_iptest(iptest):
    from ipaddress import IPv4Address, IPv4Network

    f = file("Cloudflare/IPv4Range", "r")
    ranges = f.read().splitlines()
    f.close()
    del f

    for range in ranges:
        if IPv4Address(iptest) in IPv4Network(range):
            print str(iptest) + "---- is in ------->" + str(range)
            return True
    return False


def main(_ip1, _ip2):
    _ip3 = _ip1
    _ip3_prev = ""
    conexion = ConexionMongoDB()
    conexion.open_conexion()
    while _ip3_prev != _ip2:
        if not cloudflare_iptest(realip):
            if not ip_private(_ip3):
                dictionary = {}
                document = []
                geo = GeoLocate(_ip3, 'db') # Select depth of GeoIP {insights, city, country, db}
                dh = DataHost(_ip3)
                dictionary['data-client-datetime'] = datetime.datetime.utcnow()
                dictionary['data-client-geocode'] = geo.geolocate_doc()
                dictionary['data-client-portscan'] = dh.ports()
                document.append(dictionary)
                del dh
                del geo
                conexion.insert_doc('client', document)
            else:
                print "IP %s PRIVATE, not scaned" % _ip3
            _ip3_prev = _ip3
            _ip3 = ip_add(_ip3)
        else:
            print 'IP %s in range of Claudflare' % _ip3
    conexion.close_conexion()
    del conexion


if __name__ == "__main__":
    ip1 = ''
    ip2 = ''
    ip2, ip1 = ip_order(ip1, ip2)
    main(ip1, ip2)
