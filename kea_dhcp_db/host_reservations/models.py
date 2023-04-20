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

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData


TABLES = [
    'hosts',
    'host_identifier_type',
    'ipv6_reservations',
    'dhcp4_options',
    'dhcp6_options',
    'dhcp_option_scope',
]


def initialize(engine):
    metadata = MetaData()
    metadata.reflect(engine, only=TABLES)
    base = automap_base(metadata=metadata)
    base.prepare()

    return (base.classes.hosts,
            base.classes.host_identifier_type,
            base.classes.ipv6_reservations,
            base.classes.dhcp4_options,
            base.classes.dhcp6_options,
            base.classes.dhcp_option_scope)
