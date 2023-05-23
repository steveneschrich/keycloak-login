import pytest

from girder.plugin import loadedPlugins


@pytest.mark.plugin('keycloak_login')
def test_import(server):
    assert 'keycloak_login' in loadedPlugins()
