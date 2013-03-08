#!/usr/bin/env python

import MySQLdb
import sys
import os
import json
import argparse
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
if os.path.isfile('/etc/ansible-hosts/ansible-hosts.conf'):
    config = '/etc/ansible-hosts/ansible-hosts.conf'
else:
    config = os.path.join(os.path.dirname(__file__), '../conf/ansible-hosts.conf')
parser.read(config)

dbhost = parser.get('puppet_dashboard', 'host')
dbuser = parser.get('puppet_dashboard', 'user')
dbpass = parser.get('puppet_dashboard', 'pass')
dbname = parser.get('puppet_dashboard', 'name')
con = None

def connect_to_db():
    """Connect to the puppet-dashboard database"""

    try:
        con = MySQLdb.connect(host=dbhost,user=dbuser,db=dbname)
        return con

    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

def list_hosts(conn):
    """List all hosts in the dabatase"""

    #conduct our query
    conn.query("SELECT name FROM nodes")
    result = conn.store_result()
    #store our results locally
    raw_result = result.fetch_row(maxrows=0)
    #close connection as we are now done accessing the database
    conn.close()
    #prepare a list to store just the files/modules we want to tally
    hostlist = []
    for i in raw_result:
        hostlist.append(i[0])

    return hostlist

def list_host_variables(conn, host):
    """List all variables for the given host. NOTE: this doesn't currently do anything"""

    conn.close()

if __name__ == "__main__":

    cmd_parser = argparse.ArgumentParser(description='Return a filtered or full list of hosts in puppet-dashboard\'s database')
    cmd_parser.add_argument('-l', '--list', dest='list_hosts', action='store_true',
        default=False, help='Return variables for the given host')
    args = cmd_parser.parse_args()

    dbcon = connect_to_db()

    if args.list_hosts:
        print ' '.join(list_hosts(dbcon))
        sys.exit(0)
    else:
        print "Usage: --list"
        sys.exit(1)
