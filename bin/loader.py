#!/usr/bin/python
# vim: set expandtab:
"""
**********************************************************************
GPL License
***********************************************************************
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

***********************************************************************/

:author: David Wahlstrom
:email: david.wahlstrom@gmail.com

"""

import sys
import logging
import os
from pymongo import Connection
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
if os.path.isfile('/etc/ansible-hosts/ansible-hosts.conf'):
    config = '/etc/ansible-hosts/ansible-hosts.conf'
else:
    config = os.path.join(os.path.dirname(__file__), '../conf/ansible-hosts.conf')
parser.read(config)

mongodb_host = parser.get('ansible-hosts', 'host')
dbname = parser.get('ansible-hosts', 'database')
collection_name = parser.get('ansible-hosts', 'collection')

logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%y.%m.%d %H:%M:%S')
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("ansible_mongo_hosts").addHandler(console)
log = logging.getLogger("ansible_mongo_hosts")


def configure():
    """Read configuration file and intialize connection to the mongodb instance"""
    log.debug('in configure')

    host = mongodb_host
    log.debug('connecting to mongodb host: %s' % host)
    database = dbname
    log.debug('connecting to database name: %s' % database)
    collection = collection_name
    log.debug('using collection name: %s' % collection)
    con = Connection(host)
    log.debug('selecting database/collection: %s/%s' % (database, collection))
    col = con[database][collection]
    return col


def update(collection, all_hosts):
    """Update the database to include each host supplied"""
    log.debug("in update")

    cursor = collection.find({'_id': 'all_hosts'})

    current_hosts = []
    for d in cursor:
        current_hosts = current_hosts + d['hosts']

    complete_list = current_hosts + all_hosts

    final_host_list = dict(zip(complete_list, complete_list)).keys()
    log.debug("list of hosts to be added to \"all_hosts\": %s" % final_host_list)

    collection.update(
        {'_id': 'all_hosts'},
        {"$set": {
            'hosts': final_host_list,
            'groups': ''}},
        upsert=True
    )

if __name__ == "__main__":

    import argparse

    cmd_parser = argparse.ArgumentParser(description='Add hosts to the database (does not do grouping).')
    cmd_parser.add_argument(
        '-H',
        '--hosts',
        dest='host_list',
        action='append',
        help='Space seperated list of hosts to add to the database',
        default=None,
        nargs='*')
    cmd_parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Enable debugging during execution',
        default=None)
    args = cmd_parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    if not args.host_list:
        print "Please supply -H followed by a space seperated list of hosts"
        sys.exit(1)

    host_list = args.host_list[0]
    if len(host_list) < 1:
        print "Please supply at least one host"
        sys.exit(1)
    else:
        ansible_collection = configure()
        update(ansible_collection, host_list)
