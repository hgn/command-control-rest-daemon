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



def execute_command(cmd):
    print("execute: {}".format(cmd))
    use_shell = False
    if 'shell' in cmd and cmd['shell'] == True:
        use_shell = True
    process = subprocess.Popen(cmd['cmd'].split(), shell=use_shell)
    if 'wait' in cmd and cmd['wait'] == True:
        process.wait()



def execute_commands(commands):
    for cmd in commands['commands']:
        if "sleep-before" in cmd:
            time.sleep(float(cmd["sleep-before"]))
        execute_command(cmd)
        if "sleep-after" in cmd:
            time.sleep(float(cmd["sleep-after"]))
    return 'ok'


def webfailure(msg):
    response_data = {'status': 'failure', "message": msg}
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json")


async def handle_exec(request):
    loop = request.app['LOOP']
    try:
        request_data = await request.json()
    except json.decoder.JSONDecodeError:
        response_data = {'status': 'failure', "message": "data not properly formated"}
        body = json.dumps(response_data).encode('utf-8')
        return aiohttp.web.Response(body=body, content_type="application/json")


    if "detach" in request_data and request_data['detach'] == True:
        status = 'ok'
        loop.call_soon(functools.partial(execute_commands, request_data))
    else:
        status = execute_commands(request_data)

    response_data = { 'status': status }
    body = json.dumps(response_data).encode('utf-8')
    return aiohttp.web.Response(body=body, content_type="application/json")


def handle_file_upload(request):
    if not "data" in request:
        return webfailure("no data to upload")
    if not "path" in request:
        return webfailure("no path for upload given")
    path = request['path']
    if os.path.isfile(path):
        return webfailure("file already available at {}, cannot overwrite".format(path))


def handle_file_dowload(request):
    if not "path" in request:
        return webfailure("no path argument given")
    if not os.path.isfile(request['path']):
        return webfailure("path not a file: {}".format(request['path']))
    print("downloading {}".format(request['path']))


async def handle_file(request):
    loop = request.app['LOOP']
    try:
        request_data = await request.json()
    except json.decoder.JSONDecodeError:
        return webfailure("data not properly formated")

    if "mode" not in request_data:
        return webfailure("no mode specified")

    mode = request_data['mode']
    if mode == "upload":
        return handle_file_upload(request_data)
    if mode == "download":
        return handle_file_dowload(request_data)
    return webfailure("mode must be download or upload")


def http_init(loop):
    app = aiohttp.web.Application(loop=loop)
    app['LOOP'] = loop
    app.router.add_route('POST', "/api/v1/exec", handle_exec)
    app.router.add_route('POST', "/api/v1/file", handle_file)
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
