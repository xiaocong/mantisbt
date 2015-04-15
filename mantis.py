"""
Update mantis ticket.

Usage:
mantis.py [--wsdl=<wsdl>] --username=<username> --password=<password> --changeid=<gerrit_changeid> resolve <ticket>...
mantis.py (-h | --help)
mantis.py --version

Options:
-h --help     Show this screen.
--version     Show version.
"""
from docopt import docopt
from pysimplesoap.client import SoapClient


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

    def comment(self, ticket, content):
        self.client.mc_issue_note_add(
            username=self.username,
            password=self.password,
            issue_id=int(ticket),
            note={
                "text": content
            }
        )

    def issue(self, ticket):
        return self.client.mc_issue_get(
            username=self.username,
            password=self.password,
            issue_id=ticket
        )

    def status(self):
        return self.client.mc_enum_status(
            username=self.username,
            password=self.password
        )


def main(args):
    mantis = MantisBT(
        args["--username"],
        args["--password"],
        url=args["--wsdl"] or "http://mantis.smartisan.cn/api/soap/mantisconnect.php?wsdl"
    )
    print mantis.status()
    if args["resolve"]:  # code committed and resolve related tickets
        content = "Resolved at gerrit change: %s" % args["--changeid"]
        for ticket in args["<ticket>"]:
            mantis.comment(ticket, content)
            print mantis.issue(ticket)
            #TODO change ticket status

if __name__ == '__main__':
    arguments = docopt(__doc__, version='MantisBT 1.0')
    main(arguments)
