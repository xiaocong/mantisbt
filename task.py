#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update statistics data.

Usage:
task.py [--config=<config>]
task.py (-h | --help)
task.py --version

Options:
-h --help                   显示帮助.
--version                   显示版本信息.
"""
from docopt import docopt
from mongoengine import *
from ConfigParser import ConfigParser

from mantis import MantisBT
from model import initDB, Arrival


def main(args):
    initDB(args["--config"] or 'test.conf')

    config = ConfigParser()
    config.readfp(open(args["--config"] or 'test.conf'))
    username = config.get('MANTIS', 'username')
    password = config.get('MANTIS', 'password')
    wsdl_url = config.get('MANTIS', 'wsdl')

    mbt = MantisBT(username, password, url=wsdl_url)
    sum = mbt.arrival_summary(map(lambda p: p["name"], mbt.projects))
    for k in sum:
        Arrival(
            project=k,
            total=sum[k]['total'],
            priority=sum[k]['priority'],
            severity=sum[k]['severity'],
            resolution=sum[k]['resolution'],
            category=sum[k]['category'],
            reporter=sum[k]['reporter'],
            handler=sum[k]['handler'],
            status=sum[k]['status'],
            date=sum[k]['date'],
            week=sum[k]['week'],
            month=sum[k]['month']
        ).save()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='MantisStat 1.0')
    main(arguments)
