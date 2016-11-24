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

import pykube

class AppCluster(resource.Resource):
    """A resource that creates a App Cluster.
    """

    support_status = support.SupportStatus(version='0.0.1')

    PROPERTIES = (
        NAME, SERVICES
    ) = (
        'name', 'services'
    )

    _SERVICES = (
        SERVICE_NAME,
        DOCKER_REPOSITORY_URL,
        PORT
    ) = (
        'service_name', 'docker_repository_url', 'port'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('The app cluster name.'),
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
                    DOCKER_REPOSITORY_URL: properties.Schema(
                        properties.Schema.STRING,
                        _('The url of git repository that source code refers for service.'),
                        required=True,
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

    def k8s_parse_obj(self, name, service):

        docker_registry_url = "192.168.0.66:5000"
        lang_pack_map = {
            "node": "node:0.0.1",
        }
        lang_pack = lang_pack_map.get(service.lang_pack)

        service_name = service.service_name
        docker_image_url = docker_registry_url + "/" + lang_pack
        port_num = service.port

        obj = {
            "apiVersion": "v1",
            "kind": "ReplicationController",
            "metadata": {
                "name": name+'-'+service_name,
                "namespace": "default"
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "app": name+'-'+service_name,
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": name+'-'+service_name,
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": service_name,
                                "image": docker_image_url,
                                "ports": [
                                    {"containerPort": port_num}
                                ]
                            }
                        ]
                    }
                }
            }
        }

        return obj

    def k8s_create(self, args):
        api = pykube.HTTPClient(pykube.KubeConfig.from_file("/home/micros/.kube/config"))

        name = args.name

        for service in args.services:
            obj = self.k8s_parse_obj(name, service)
            pykube.ReplicationController(api, obj).create()

    def k8s_delete(self, args):
        api = pykube.HTTPClient(pykube.KubeConfig.from_file("/home/micros/.kube/config"))

        name = args.name

        for service in args.services:
            obj = self.k8s_parse_obj(name, service)
            pykube.ReplicationController(api, obj).delete()

    def handle_create(self):
        physical_resource_name = self.physical_resource_name()

        args = {
            'name': self.properties[self.NAME],
            'services': self.properties[self.SERVICES],
            'physical_resource_name': physical_resource_name,
        }
        self.k8s_create(args)
        self.resource_id_set(physical_resource_name())

    def handle_delete(self):
        physical_resource_name = self.physical_resource_name()

        args = {
            'name': self.properties[self.NAME],
            'services': self.properties[self.SERVICES],
            'physical_resource_name': physical_resource_name,
        }
        self.k8s_delete(args)

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        None


def resource_mapping():
    return {
        'OS::Astro::AppCluster': AppCluster
    }
