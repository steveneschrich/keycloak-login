import template from "../templates/configView.pug";
import "../stylesheets/configView.styl";

import View from "@girder/core/views/View";
import PluginConfigBreadcrumbWidget from "@girder/core/views/widgets/PluginConfigBreadcrumbWidget";
import { restRequest } from "@girder/core/rest";
import events from "@girder/core/events";

const ConfigView = View.extend({
    events: {
        "submit .g-keycloak-server-form": function (event) {
            event.preventDefault();
            this.$(".g-validation-failed-message").empty();
            const host = this.$(`#g-keycloak-server-host`).val();
            const client = this.$(`#g-keycloak-server-client`).val();
            const realm = this.$(`#g-keycloak-server-realm`).val();
            const secret = this.$(`#g-keycloak-server-secret-key`).val();

            restRequest({
                method: "PUT",
                url: "system/setting",
                data: {
                    key: "keycloak.config",
                    value: JSON.stringify({
                        host: host,
                        client: client,
                        realm: realm,
                        secret: secret,
                    }),
                },
                error: null,
            })
                .done(() => {
                    events.trigger("g:alert", {
                        icon: "ok",
                        text: "Config saved.",
                        type: "success",
                        timeout: 3000,
                    });
                })
                .fail((resp) => {
                    this.$(".g-validation-failed-message").text(
                        resp.responseJSON.message
                    );
                });
        },
        "click .g-keycloak-test": function (event) {
            const btn = $(event.currentTarget);
            const host = this.$(`#g-keycloak-server-host`).val();
            const client = this.$(`#g-keycloak-server-client`).val();
            const realm = this.$(`#g-keycloak-server-realm`).val();
            const secret = this.$(`#g-keycloak-server-secret-key`).val();

            restRequest({
                url: "system/keycloak_server/status",
                method: "GET",
                data: {
                    host,
                    client,
                    realm,
                    secret,
                },
            }).done((resp) => {
                btn.girderEnable(true);
                if (resp.connected) {
                    this.$(`#g-keycloak-server-conn-ok`).removeClass("hide");
                } else {
                    this.$(`#g-keycloak-server-conn-fail`)
                        .removeClass("hide")
                        .find(".g-msg")
                        .text(resp.error);
                }
            });

            btn.girderEnable(false);
            this.$(`#g-keycloak-server-conn-ok`).addClass("hide");
            this.$(`#g-keycloak-server-conn-fail`).addClass("hide");
        },
    },
    initialize: function () {
        restRequest({
            method: "GET",
            url: "system/setting",
            data: {
                key: "keycloak.config",
            },
        }).done((resp) => {
            this.keycloakConfig = resp;
            this.render();
        });
    },

    render: function () {
        this.$el.html(
            template({
                config: this.keycloakConfig,
            })
        );

        if (!this.breadcrumb) {
            this.breadcrumb = new PluginConfigBreadcrumbWidget({
                pluginName: "Keycloak login",
                el: this.$(".g-config-breadcrumb-container"),
                parentView: this,
            }).render();
        }

        return this;
    },
});

export default ConfigView;
