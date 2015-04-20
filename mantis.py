#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update mantis ticket.

Usage:
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> --changeid=<gerrit_changeid> resolve <ticket>...
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> arrival
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> priorities
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> severities
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> status
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> resolutions
mantis.py (-h | --help)
mantis.py --version

Options:
-h --help     Show this screen.
--version     Show version.
"""
from docopt import docopt
from pysimplesoap.client import SoapClient
from collections import defaultdict
import json
import re

import config


def toDate(dt):
    return dt.strftime("%Y%m%d")


def toWeek(dt):
    return dt.strftime("%YW%W")


def toMonth(dt):
    return dt.strftime("%Y%m")


class MantisBT(object):

    def __init__(self, username, password, url):
        if not url.endswith("?wsdl"):
            if url.endswith("/api/soap/mantisconnect.php"):
                url += "?wdsl"
            elif url.endswith("/"):
                url += "api/soap/mantisconnect.php?wsdl"
            else:
                url += "/api/soap/mantisconnect.php?wsdl"

        self.client = SoapClient(wsdl=url, trace=False)
        self.username = username
        self.password = password
        self._status = None
        self._priorities = None
        self._severities = None
        self._resolutions = None

    def comment(self, ticket, content):
        self.client.mc_issue_note_add(
            username=self.username,
            password=self.password,
            issue_id=int(ticket),
            note={
                "text": content
            }
        )

    def issue(self, issue_id):
        return self.client.mc_issue_get(
            username=self.username,
            password=self.password,
            issue_id=issue_id
        )

    @property
    def status(self):
        if not self._status:
            self._status = map(
                lambda n: n.get("item"),
                self.client.mc_enum_status(
                    username=self.username,
                    password=self.password
                )['return']
            )
        return self._status

    @property
    def priorities(self):
        if not self._priorities:
            self._priorities = map(
                lambda n: n.get("item"),
                self.client.mc_enum_priorities(
                    username=self.username,
                    password=self.password
                )['return']
            )
        return self._priorities

    @property
    def severities(self):
        if not self._severities:
            self._severities = map(
                lambda n: n.get("item"),
                self.client.mc_enum_severities(
                    username=self.username,
                    password=self.password
                )['return']
            )
        return self._severities

    @property
    def resolutions(self):
        if not self._resolutions:
            self._resolutions = map(
                lambda n: n.get("item"),
                self.client.mc_enum_resolutions(
                    username=self.username,
                    password=self.password
                )['return']
            )
        return self._resolutions

    def value_of(self, prop, name):
        default = "null"
        if not name:
            return default
        m = re.match(r"@(\d+)@", name)
        if m:
            _id = int(m.group(1))
            for v in getattr(self, prop):
                if v.id == _id:
                    return v.name
            else:
                return default
        else:
            return name

    def isTicketResolved(self, status):
        return status >= config.TICKET_RESOLVED_STATUS

    def projectId(self, project_name):
        return self.client.mc_project_get_id_from_name(
            username=self.username,
            password=self.password,
            project_name=project_name
        )['return']

    def maxTicketId(self, proj):
        if type(proj) is str:
            proj = self.projectId(proj)
        return self.client.mc_issue_get_biggest_id(
            username=self.username,
            password=self.password,
            project_id=proj
        )['return']

    def tickets(self, project_names):
        if type(project_names) is not list:
            project_names = [project_names]
        pids = map(lambda n: self.projectId(n), project_names)
        max_id = max(map(lambda proj: self.maxTicketId(proj), pids))
        for i in xrange(max_id):
            try:
                issue = self.client.mc_issue_get(
                    username=self.username,
                    password=self.password,
                    issue_id=i+1
                )['return']
                if issue['project']['id'] in pids:
                    yield issue
            except:
                pass

    def live_tickets(self, project_name):
        pid = self.projectId(project_name)
        page = 0
        per_page = 100
        while True:
            page += 1
            ts = self.client.mc_project_get_issue_headers(
                username=self.username,
                password=self.password,
                project_id=pid,
                page_number=page,
                per_page=per_page
            )['return']
            for t in ts:
                yield t['item']
            if len(ts) is 0:
                break

    def arrival_summary(self, project_names):
        def default_sum():
            return {
                "total": 0,
                "priority": defaultdict(int),
                "severity": defaultdict(int),
                "category": defaultdict(int),
                "reporter": defaultdict(int)
            }

        def default_proj_sum():
            return {
                "total": 0,
                "priority": defaultdict(int),
                "severity": defaultdict(int),
                "resolution": defaultdict(int),
                "category": defaultdict(int),
                "reporter": defaultdict(int),
                "status": defaultdict(int),
                "date": defaultdict(default_sum),
                "week": defaultdict(default_sum),
                "month": defaultdict(default_sum),
            }

        sum = defaultdict(default_proj_sum)
        for t in self.tickets(project_names):
            project = t["project"]["name"]
            category = t["category"]
            severity = self.value_of("severities", t["severity"]["name"])
            priority = self.value_of("priorities", t["priority"]["name"])
            resolution = self.value_of("resolutions", t["resolution"]["name"])
            status = self.value_of("status", t["status"]["name"])
            reporter = t["reporter"].get("name") or t["reporter"].get("email")
            sum[project]["total"] += 1
            sum[project]["severity"][severity] += 1
            sum[project]["priority"][priority] += 1
            sum[project]["category"][category] += 1
            sum[project]["resolution"][resolution] += 1
            sum[project]["status"][status] += 1
            sum[project]["reporter"][reporter] += 1
            date = toDate(t["date_submitted"])
            sum[project]["date"][date]["total"] += 1
            sum[project]["date"][date]["priority"][priority] += 1
            sum[project]["date"][date]["severity"][severity] += 1
            sum[project]["date"][date]["category"][category] += 1
            sum[project]["date"][date]["reporter"][reporter] += 1
            week = toWeek(t["date_submitted"])
            sum[project]["week"][week]["total"] += 1
            sum[project]["week"][week]["priority"][priority] += 1
            sum[project]["week"][week]["severity"][severity] += 1
            sum[project]["week"][week]["category"][category] += 1
            sum[project]["week"][week]["reporter"][reporter] += 1
            month = toMonth(t["date_submitted"])
            sum[project]["month"][month]["total"] += 1
            sum[project]["month"][month]["priority"][priority] += 1
            sum[project]["month"][month]["severity"][severity] += 1
            sum[project]["month"][month]["category"][category] += 1
            sum[project]["month"][month]["reporter"][reporter] += 1
            # print t["id"], t["version"], t["summary"]
        return sum


def main(args):
    mantis = MantisBT(
        args["--username"],
        args["--password"],
        url=args["--wsdl"] or "http://mantis.smartisan.cn/api/soap/mantisconnect.php?wsdl"
    )
    if args["arrival"]:
        print json.dumps(mantis.arrival_summary(config.PROJECTS_NAME), indent=2)
    elif args["priorities"]:
        for p in mantis.priorities:
            print p.id, p.name
    elif args["severities"]:
        for p in mantis.severities:
            print p.id, p.name
    elif args["status"]:
        for p in mantis.status:
            print p.id, p.name
    elif args["resolutions"]:
        for p in mantis.resolutions:
            print p.id, p.name

if __name__ == '__main__':
    arguments = docopt(__doc__, version='MantisBT 1.0')
    main(arguments)
