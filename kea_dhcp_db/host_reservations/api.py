#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
import ipaddress

from kea_dhcp_db.host_reservations import models
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import create_engine


class Api:

    def __init__(self, db_host, db_name, db_username, db_password):

        db_connection_url = (
            f'mysql+pymysql://'
            f'{db_username}:{db_password}@{db_host}/{db_name}')
        self.engine = create_engine(db_connection_url)

        (self.Hosts,
         self.HostIdentifierType,
         self.IPv6Reservations,
         self.DHCPv4Options,
         self.DHCPv6Options,
         self.DHCPOptionScope) = models.initialize(self.engine)

    def get(self, **kwargs):
        """Get host reservations

        :param kwargs: kwargs to filter by
        :return: query
        """
        with Session(self.engine) as session:
            query = session.query(self.Hosts).filter_by(**kwargs)
            query = query.options(joinedload(
                self.Hosts.ipv6_reservations_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp4_options_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp6_options_collection))
            query_result = query.all()

        return query_result

    def get_all(self):
        """Get all host reservations

        :returns: query
        """
        with Session(self.engine) as session:
            query = session.query(self.Hosts)
            query = query.options(joinedload(
                self.Hosts.ipv6_reservations_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp4_options_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp6_options_collection))
            query_result = query.all()

        return query_result

    def get_by_hostname(self,
                        hostname: str,
                        subnet_id: Optional[int] = None):
        """Get host reservations by hostname

        :param hostname: Hostname
        :param subnet_id: (Optional) kea-dhcp Subnet ID
        :returns: query
        """
        filters = {'hostname': hostname}
        if subnet_id:
            filters['subnet_id'] = subnet_id
        with Session(self.engine) as session:
            query = session.query(self.Hosts).filter_by(hostname=hostname)
            query = query.options(joinedload(
                self.Hosts.ipv6_reservations_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp4_options_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp6_options_collection))
            query_result = query.all()

        return query_result

    def _get_by_ipv4_address(self,
                             ip_address: str,
                             subnet_id: Optional[int] = None):
        filters = dict()
        filters['ipv4_address'] = int(ipaddress.IPv4Address(ip_address))
        if subnet_id:
            filters['subnet_id'] = subnet_id
        with Session(self.engine) as session:
            query = session.query(self.Hosts).filter_by(filters)
            query = query.options(joinedload(
                self.Hosts.ipv6_reservations_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp4_options_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp6_options_collection))

            query_result = query.all()

        return query_result

    def _get_by_ipv6_address(self, ip_address, subnet_id):
        # TODO(hjensas) This needs a join of hosts and ipv6_reservations
        pass

    def get_by_ip_address(self,
                          ip_address: str,
                          subnet_id: Optional[int] = None):
        """Get host reservations by address

        :param ip_address: IP address
        :param subnet_id: (Optional) kea-dhcp Subnet ID
        :returns: query
        """
        if not subnet_id:
            subnet_id = 0  # 0 == global reservation

        if ipaddress.ip_address(ip_address).version == 4:
            return self._get_by_ipv4_address(ip_address, subnet_id)
        elif ipaddress.ip_address(ip_address).version == 6:
            return self._get_by_ipv6_address(ip_address, subnet_id)

    def get_by_identifier(self,
                          identifier_type: int,
                          identifier: str):
        """Get host resevations by identifier

        :param identifier_type: Identifier type
        :param identifier: Identifier
        :returns: query
        """
        with Session(self.engine) as session:
            query = session.query(self.Hosts).filter_by(
                dhcp_identifier_type=identifier_type,
                dhcp_identifier=identifier)
            query = query.options(joinedload(
                self.Hosts.ipv6_reservations_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp4_options_collection))
            query = query.options(joinedload(
                self.Hosts.dhcp6_options_collection))
            query_result = query.all()

        return query_result

    def add(self,
            identifier_type: int,
            identifier: str,
            hostname: Optional[str] = None,
            ip_address: Optional[str] = None,
            next_server: Optional[str] = None,
            server_hostname: Optional[str] = None,
            boot_filename: Optional[str] = None,
            subnet_id: Optional[int] = None,
            client_classes: Optional[list] = None,
            option_data: Optional[list] = None):
        """Add host reservation

        :param identifier_type: Identifier type
        :param identifier: Identifier
        :param hostname: (Optional) Hostname
        :param ip_address: (Optional) IP address
        :param next_server: (Optional) Next server
        :param server_hostname: (Optional) Server hostname
        :param boot_filename: (Optional) Boot filename
        :param subnet_id: (Optional) kea-dhcp Subnet ID
        :param client_classes: (Optional) List of client classes
        :param option_data (Optional) List of option data dicts
        """
        host = self.Hosts()
        host.dhcp_identifier_type = identifier_type
        host.dhcp_identifier = identifier
        if hostname:
            host.hostname = hostname
        if ip_address:
            if ipaddress.ip_address(ip_address).version == 4:
                host.ipv4_address = int(ipaddress.ip_address(ip_address))
                if subnet_id:
                    host.dhcp4_subnet_id = subnet_id
                if next_server:
                    host.dhcp4_next_server = next_server
                if server_hostname:
                    host.dhcp4_server_hostname = server_hostname
                if boot_filename:
                    host.dhcp4_boot_file_name = boot_filename
                if client_classes:
                    host.dhcp4_client_classes = client_classes
            elif ipaddress.ip_address(ip_address).version == 6:
                reservation = self.IPv6Reservations()
                reservation.address = ip_address
                host.ipv6_reservations_collection.append(reservation)
                if subnet_id:
                    host.dhcp6_subnet_id = subnet_id
                if client_classes:
                    host.dhcp6_client_classes = client_classes
        with Session(self.engine) as session:
            session.add(host)
            session.commit()

    def delete(self, host_id):
        """Delete host reservation

        :param host_id: Host ID
        """
        with Session(self.engine) as session:
            query = session.query(self.Hosts).filter_by(host_id=host_id)
            count = query.delete()
            if count == 0:
                # TODO(hjensas): Add proper exceptions
                raise Exception(f'Host with id: {host_id} not found.')

    def update(self,
               host_id: int,
               identifier_type: int,
               identifier: str,
               hostname: Optional[str] = None,
               ip_address: Optional[str] = None,
               next_server: Optional[str] = None,
               server_hostname: Optional[str] = None,
               boot_filename: Optional[str] = None,
               subnet_id: Optional[int] = None,
               client_classes: Optional[list] = None,
               option_data: Optional[list] = None):
        """Update host reservation

        :param host_id: Host ID
        :param identifier_type: Identifier type
        :param identifier: Identifier
        :param hostname: (Optional) Hostname
        :param ip_address: (Optional) IP address
        :param next_server: (Optional) Next server
        :param server_hostname: (Optional) Server hostname
        :param boot_filename: (Optional) Boot filename
        :param subnet_id: (Optional) kea-dhcp Subnet ID
        :param client_classes: (Optional) List of client classes
        :param option_data (Optional) List of option data dicts
        """
        pass
