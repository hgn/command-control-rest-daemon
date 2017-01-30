#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import urllib.request

def construct_cmd(cmds, wait=False, shell=False):
    container = dict()
    cmd_list = list()
    cmd_entry = dict()
    for cmd in cmds:
        cmd_entry['cmd'] = cmd
        cmd_entry['wait'] = wait
        cmd_entry['shell'] = shell
        cmd_entry['sleep-before'] = 0
        cmd_entry['sleep-after']  = 0
        cmd_list.append(cmd_entry)
    container['commands'] = cmd_list
    return container

def disable_proxy(disable_proxy=True):
    # install no proxy, for proxied environments the
    # system proxy is ignore here, for localhost communication
    # this is fine, if you want to communicate via a proxy please
    # remove the following lines
    proxy_support = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)


def transmit(url, cmds, wait=False, shell=False, timeout=3):
    disable_proxy()
    # change request behavior
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Chrome/22.0.1229.94; Windows NT)')

    # build command data list
    data = construct_cmd(cmds, wait=wait, shell=shell)
    tx_data = json.dumps(data).encode('utf-8')

    # no error handling, caller can catch error respectively if required
    with urllib.request.urlopen(req, tx_data, timeout=timeout) as res:
        resp = json.loads(str(res.read(), "utf-8"))
        return resp

def main():
    url = "http://0.0.0.0:50023/api/v1/exec"

    # test 1)
    cmds = [ "ls -R /" ]
    transmit(url, cmds)

    # test 2)
    cmds = [ "sleep 2", "sleep 2", "sleep 2" ]
    transmit(url, cmds, wait=True, timeout=10)

    # test 3)
    #cmds = [ "killall -9 ipproof-server", "sleep 2", "ipproof-server -t udp -vvv" ]
    #transmit(url, cmds, wait=True, timeout=10)


if __name__ == '__main__':
    print("Control & Command REST Daemon Example, 2017\n")
    main()
