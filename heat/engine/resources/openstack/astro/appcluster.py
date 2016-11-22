#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from heat.common.i18n import _
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource
from heat.engine import support

import operator
import pykube
import backports.ssl_match_hostname


class AppCluster(resource.Resource):
    """A resource that creates a App Cluster.
    """

    support_status = support.SupportStatus(version='0.0.1')

    PROPERTIES = (
        NAME, GIT_REPOSITORY_URL, SERVICES
    ) = (
        'name', 'git_repository_url', 'services'
    )

    _SERVICES = (
        SERVICE_NAME,
        LANG_PACK,
        PORT
    ) = (
        'service_name', 'lang_pack', 'port',
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('The app cluster name.')
        ),
        GIT_REPOSITORY_URL: properties.Schema(
            properties.Schema.STRING,
            _('The url of git repository that source code refers for service.'),
            required=True,
        ),
        SERVICES: properties.Schema(
            properties.Schema.LIST,
            _('Services for app cluster.'),
            required=True,
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    SERVICE_NAME: properties.Schema(
                        properties.Schema.STRING,
                        _('The service name.'),
                        required=True
                    ),
                    LANG_PACK: properties.Schema(
                        properties.Schema.STRING,
                        _('The language package of service.'),
                        required=True
                    ),
                    PORT: properties.Schema(
                        properties.Schema.INTEGER,
                        _('The port of service'),
                        constraints=[
                            constraints.Range(min=0),
                        ],
                        required=True,
                    ),
                },
            )
        )
    }

    def k8s_create(self, args):
        None

    def k8s_delete(self, args):
        None

    def handle_create(self):
        args = {
            'name': self.properties[self.NAME],
            'git_repository_url': self.properties[self.GIT_REPOSITORY_URL],
            'services': self.properties[self.SERVICES]
        }
        self.k8s_create(args)
        self.resource_id_set(self.physical_resource_name())


def resource_mapping():
    return {
        'OS::Astro::AppCluster': AppCluster
    }
