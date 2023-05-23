import random
import string
import os
import logging

from girder import events, plugin
from keycloak import KeycloakOpenID
from girder.api import access
from girder.models.user import User
from girder.exceptions import ValidationException
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import boundHandler
from girder.exceptions import RestException
from dotenv import load_dotenv
from girder.models.setting import Setting

from .settings import PluginSettings

_PASSWORD_LENGHT = 6

load_dotenv()


def _keyCloakInitialize(KEYCLOAK_HOST, KEYCLOAK_CLIENT, KEYCLOAK_REALM, KEYCLOAK_SECRET):
    try:
        keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_HOST,
                                         client_id=KEYCLOAK_CLIENT,
                                         realm_name=KEYCLOAK_REALM,
                                         client_secret_key=KEYCLOAK_SECRET)
        return keycloak_openid
    except:
        raise Exception('KeyCloak connection error for host %s.' % KEYCLOAK_HOST)


def _registerKeyCloakUser(attrs, email):
    first, last, _username, user = None, None, None, None
    if attrs.get('given_name'):
        first = attrs['given_name']
    if attrs.get('family_name'):
        last = attrs['family_name']
    if attrs.get('preferred_username'):
        username = attrs['preferred_username']
        if username.isnumeric():
            _username = 'user-' + username
        else:
            _username = username
    if not first or not last or not username:
        raise Exception('No Keycloak name entry found for %s.' % email)
    try:
        _password = ''.join(random.choices(string.ascii_uppercase
                                           + string.digits, k=_PASSWORD_LENGHT))
        user = User().createUser(_username,
                                 password=_password, firstName=first, lastName=last, email=email)
        if username.isnumeric():
            User().update({'_id': user['_id']}, {"$set": {"login": username}})

        user['login'] = username
        return user
    except ValidationException as e:
        print(e)
        if e.field != 'login':
            raise


def _getKeyCloakUser(attrs):
    email = attrs.get('email')
    if not email:
        raise Exception('No email record present for the given Keycloak user.')

    existing = User().findOne({
        'email': email
    })

    if existing != None:
        return existing

    return _registerKeyCloakUser(attrs, email)


def _keyCloakAuth(event):
    login, password = event.info['login'], event.info['password']

    if not login or not password:
        return

    keycloakSetting = Setting().get('keycloak.config')
    if not keycloakSetting:
        return

    KEYCLOAK_HOST = keycloakSetting.get('host')
    KEYCLOAK_CLIENT = keycloakSetting.get('client')
    KEYCLOAK_REALM = keycloakSetting.get('realm')
    KEYCLOAK_SECRET = keycloakSetting.get('secret')

    keycloak_openid = _keyCloakInitialize(
        KEYCLOAK_HOST, KEYCLOAK_CLIENT, KEYCLOAK_REALM, KEYCLOAK_SECRET)
    try:
        token = keycloak_openid.token(login, password)
        userinfo = keycloak_openid.userinfo(token['access_token'])
        user = _getKeyCloakUser(userinfo)
        if user:
            event.stopPropagation().preventDefault().addResponse(user)
    except:
        logging.warning(
            "Keycloak authentication failed, continuing with girder authentication process..")


@access.public
@boundHandler
@autoDescribeRoute(
    Description('Test connection status to a KeyCoak server.')
    .notes('You must be an administrator to call this.')
    .param('host', 'The HOST of the server (including port)')
    .param('client', 'The client identity to bind with.')
    .param('realm', 'The realm identity to bind with.')
    .param('secret', 'The realm key secret.')
    .errorResponse('You are not an administrator.', 403)
)
def _keyCloakServerTest(self, host, client, realm, secret):
    try:
        keycloak_openid = _keyCloakInitialize(host, client, realm, secret)
        keycloak_openid.well_known()
        return {
            'connected': True
        }
    except Exception as err:
        raise RestException('Keycloak connection error: "%s".' % err)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'keycloak-login'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        events.bind('model.user.authenticate', 'keycloak', _keyCloakAuth)
        info['apiRoot'].system.route('GET', ('keycloak_server', 'status'), _keyCloakServerTest)
        pass
