#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp.web
import addict
import time
import sys
import os
import json
import datetime
import argparse
import pprint
import subprocess

# default false, can be changed via program arguments (-v)
DEBUG_ON = False

# exit codes for shell, failre cones can be sub-devided
# if required and shell/user has benefit of this information
EXIT_OK      = 0
EXIT_FAILURE = 1


def err(msg):
    sys.stderr.write(msg)
    sys.exit(EXIT_FAILURE)

def warn(msg):
    sys.stderr.write(msg)


def debug(msg):
    if not DEBUG_ON: return
    sys.stderr.write(msg)


def debugpp(d):
    if not DEBUG_ON: return
    pprint.pprint(d, indent=2, width=200, depth=6)
    sys.stderr.write("\n")


def msg(msg):
    sys.stdout.write(msg)


def execute_command(command):
    print(command)
    return subprocess.check_output(command.split(), shell=True).decode("utf-8") 

async def handle_raw(request):
    try:
        request_data = await request.json()
    except json.decoder.JSONDecodeError:
        response_data = {'status': 'failure', "message": "data not properly formated"}
        body = json.dumps(response_data).encode('utf-8')
        return aiohttp.web.Response(body=body, content_type="application/json")

    ret = list()
    for cmd in request_data:
        ret.append(execute_command(cmd))

    response_data = {'status': 'ok', "data" : ret}
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json")


def http_init(loop):
    app = aiohttp.web.Application(loop=loop)
    app.router.add_route('POST', "/v1/raw/", handle_raw)
    server = loop.create_server(app.make_handler(),
                                conf.common.v4_listen_addr,
                                conf.common.v4_listen_port)
    fmt = "HTTP IPC server started at http://{}:{}\n"
    msg(fmt.format(conf.common.v4_listen_addr, conf.common.v4_listen_port))
    loop.run_until_complete(server)


def main(conf):
    loop = asyncio.get_event_loop()
    http_init(loop)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        loop.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--configuration", help="configuration", type=str, default=None)
    parser.add_argument("-v", "--verbose", help="verbose", action='store_true', default=False)
    args = parser.parse_args()
    if not args.configuration:
        err("Configuration required, please specify a valid file path, exiting now\n")
    return args


def load_configuration_file(args):
    with open(args.configuration) as json_data:
        return addict.Dict(json.load(json_data))


def init_global_behavior(args, conf):
    global DEBUG_ON
    if conf.common.debug or args.verbose:
        msg("Debug: enabled\n")
        DEBUG_ON = True
    else:
        msg("Debug: disabled\n")


def conf_init():
    args = parse_args()
    conf = load_configuration_file(args)
    init_global_behavior(args, conf)
    return conf


if __name__ == '__main__':
    msg("Control & Command REST Daemon, 2016\n")
    conf = conf_init()
    main(conf)
