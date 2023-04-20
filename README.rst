==================
python-kea-dhcp-db
==================

Python API for Kea DHCP database backend

Provides a python API for the Kea DHCP database backend. SQLAlchemy's `Automap
<https://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html>`_ is used
to automatically generate mapped classes and relationships from a selection of
tables in the database schema.

* Free software: Apache license
* Documentation: TODO
* Source: TODO
* Bugs: TODO

Features
--------

* Host reservations - Implements:

  * ``add``
  * TODO: ``update``
  * ``delete``
  * ``get``
  * ``get_all``
  * ``get_by_hostname``
  * ``get_by_ip_address`` (TODO: Need's update to support IPv6 address)
  * ``get_by_identifier``

* Configuration - TODO!
