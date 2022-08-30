import requests
from ruxit.api.base_plugin import RemoteBasePlugin
import logging
import adal
import os
import json

logger = logging.getLogger(__name__)
tenant = os.environ['AZURE_TENANT_ID']
authority_url = 'https://login.microsoftonline.com/' + tenant
client_id = os.environ['AZURE_CLIENT_ID']
client_secret = os.environ['AZURE_CLIENT_SECRET']
suscription = os.environ['AZURE_SUBSCRIPTION_ID']
resource = 'https://management.azure.com/'
context = adal.AuthenticationContext(authority_url)
token = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
headers = {'Authorization': 'Bearer ' + token['accessToken'], 'Content-Type': 'application/json'}
params = {'api-version': '2022-01-01'}

class AzureVnetPlugin(RemoteBasePlugin):
    
    def initialize(self, **kwargs):
        logger.info("Config: %s", self.config)
        #self.url = self.config["url"]

    def query(self, **kwargs):
        #Create topology
        #url = self.url + "/topology"
        url = 'https://management.azure.com/subscriptions/' + suscription + '/providers/Microsoft.Network/virtualNetworks'
        #topology = requests.get(url, timeout=10).json()
        topology = requests.get(url, headers=headers, params=params)
        #salida json
        print(json.dumps(topology.json(), indent=4, separators=(',', ': ')))

        for group_t in topology:
            group_name = group_t['name']
            group = self.topology_builder.create_group(group_name, group_name)
            for device_t in group_t['devices']:
                device_name = device_t['name']
                device = group.create_device(device_name, device_name)
                logger.info("Topology: group name=%s, device name=%s", group.name, device.name)
                #Collect stats
                stats = device_t['stats']
                device.absolute(key='vnetname', value=stats['name'])
                device.absolute(key='type', value=stats['type'])
                device.relative(key='subnets', value=stats['subnets'])
                #device.absolute(key='countercd', value=stats['counter'])
                #device.relative(key='randomcd', value=stats['random'])

#url = 'https://management.azure.com/subscriptions/' + suscription + '/providers/Microsoft.Network/virtualNetworks'
#r = requests.get(url, headers=headers, params=params)
#print(json.dumps(r.json(), indent=4, separators=(',', ': ')))
