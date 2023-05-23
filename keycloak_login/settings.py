import jsonschema
from girder.exceptions import ValidationException
from girder.utility import setting_utilities


class PluginSettings:
    CONFIG = 'keycloak.config'


@setting_utilities.default(PluginSettings.CONFIG)
def _defaultConfig():
    return {}


@setting_utilities.validator(PluginSettings.CONFIG)
def _validateServers(doc):
    serversSchema = {
        'type': 'object',
        'properties': {
            'host': {
                'type': 'string',
                'minLength': 1
            },
            'client': {
                'type': 'string',
                'minLength': 1
            },
            'realm': {
                'type': 'string'
            },
            'secret': {
                'type': 'string'
            }
        },
        'required': ['host', 'client', 'realm', 'secret']

    }
    try:
        jsonschema.validate(doc['value'], serversSchema)
    except jsonschema.ValidationError as e:
        raise ValidationException('Invalid LDAP servers list: ' + str(e))

    config = doc['value']
    config['host'] = config['host']
    config['client'] = config.get('client', '')
    config['realm'] = config.get('realm', '')
    config['secret'] = config.get('secret', '')
