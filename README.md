ansible-hosts
=============

A MongoDB driven Ansible (https://github.com/ansible/ansible) hosts inventory.  The goal of this project is to provide a set of scripts/apps to populate, manage and query a MongoDB database for use as a hosts inventory for Ansible.  ansible-hosts can currently import data from the following sources:

- puppet-dashboard

In the future, I'd also like to support the following sources:

- zabbix

dependancies
============

At the very least, ansible-hosts requires a MongoDB database to be online and accessible.  In order to populate it from sources like puppet-dashboard or zabbix, remote access to those databases will be required as well.  And since ansilbe talks json, python-json will be required on the hosts that will be executing these scripts.
