ansible-hosts
=============

A MongoDB driven Ansible (https://github.com/ansible/ansible) hosts inventory.  The goal of this project is to provide a set of scripts/apps to populate, manage and query a MongoDB database for use as a hosts inventory for Ansible.  ansible-hosts can currently import data from the following sources:

- command line (space seperated list)
- zabbix
- puppet-dashboard

In the future, I'd like to support the following inventory systems:

- cobbler


Dependencies
============

At the very least, ansible-hosts requires a MongoDB database to be online and accessible.  In order to populate it from sources like puppet-dashboard or zabbix, remote access to those databases will be required as well.  And since ansilbe talks json, python-json will be required on the hosts that will be executing these scripts.

Loading data
============

Hosts are loaded into the ansible-hosts database after being scraped from other sources.  The ansible\_hosts\_loader.py script takes a space seperated list of hosts and populates the ansible-hosts MongoDB.

Grouping hosts
==============

Hosts can be grouped by providing a flat file formatted as a python dictionary describing the groups and the hosts which are contained within.  For example, to create 2 groups each with 3 hosts:
```
{
'group1': {
          hosts: [
                 'host1.example.com',
                 'host2.example.com',
                 'host3.example.com'
                 ],
          groups: []
},
'group2': {
          hosts: [
                 'hostA.example.com',
                 'hostB.example.com',
                 'hostC.example.com'
                 ],
          groups: []
}
}
```
Groups can also contain other groups.

Below is a host grouping example:
```
{
'groupA': {
          hosts: [
                 'hostA1.example.com',
                 'hostA2.example.com',
                 'hostA3.example.com'
                 ],
          groups: []
},
'groupB': {
          hosts: [
                 'hostB1.example.com',
                 'hostB2.example.com',
                 'hostB3.example.com'
                 ],
          groups: []
},
'groupC': {
          hosts: [],
          groups: [
                  'groupA',
                  'groupB'
                  ]
}
}
```

puppet-dashboard
================

In order for ansible-hosts to be able to pull data from puppet-dashboard, the database must be accepting external connections (if the script is running remotely), and a user must exist that allows select on the table dashboard.nodes.  Use the following sql to create a user with these privileges:
```
create user 'ansible';
grant select on dashboard.nodes;
flush privileges;
```
The exact query that is being run against this database is:
```
SELECT name FROM nodes
```

zabbix
======

Similar to puppet-dashboard, ansible-hosts needs to be able to contact the zabbix database (likely remotely).  A user must exist in the database for ansible to use and that user must have select privs on the table zabbix.hosts. Use the following sql to create a user with these privileges;
```
create user 'ansible';
grant select on 'zabbix.hosts' to 'ansible';
flush privileges;
```
The exact query that is being run against this database is:
```
SELECT dns FROM hosts WHERE dns<>''
```
