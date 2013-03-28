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
import pickle
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

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                   )
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

def update(collection, hosts_groups):
    """Update the database to include each host supplied"""
    log.debug("in update")

    #grab a list of "known good" hosts from the database
    cursor = collection.find({'_id': 'all_hosts'})
    all_hosts = cursor[0]['hosts']

    #prepare list of groups that currently exist in the database
    existing_groups = []
    cursor = collection.find()
    for group in cursor:
        existing_groups.append(group['_id'])

    for group in hosts_groups:
        #determine if our currently selected group exists already and delete 
        #it if it does
        if group in existing_groups:
            #remove the group if it already exists, thus removing potentially
            #bad/dead hosts
            collection.remove({'_id': group})

        #prepare selectors for the hosts that are in the group and the groups
        #that make up this group
        associated_hosts = list(set(all_hosts) & set(hosts_groups[group]['hosts']))
        associated_groups = hosts_groups[group]['groups']

        #update the database with our findings
        collection.update(
            {'_id': group}, 
            {"$set": {
                'hosts': associated_hosts,
                'groups': associated_groups
                }
            },
            upsert=True
        )

if __name__ == "__main__":

    import argparse

    cmd_parser = argparse.ArgumentParser(description='Add hosts to the database (does not do grouping).')
    cmd_parser.add_argument('-f', '--file', dest='group_file', action='store',
        help='Path to file containing grouping information', default=None)
    cmd_parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='Enable debugging during execution', default=None)
    args = cmd_parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    hosts_groups = eval( open(args.group_file).read())
    ansible_collection = configure()
    update(ansible_collection, hosts_groups)
