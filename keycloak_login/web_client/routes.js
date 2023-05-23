/* eslint-disable import/first */

import events from "@girder/core/events";
import router from "@girder/core/router";
import { exposePluginConfig } from "@girder/core/utilities/PluginUtils";

exposePluginConfig("keycloak_login", "plugins/keycloak/config");

import ConfigView from "./views/ConfigView";

router.route("plugins/keycloak/config", "keycloakConfig", function () {
    events.trigger("g:navigateTo", ConfigView);
});
