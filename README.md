# KEYCLOAK Login

`Girder` plugin to extend the `Girder` authentication by adding `keycloak` integration.

This plugin first tries to do the login against `keycloak`, if the user i not on the `keycloak` database, the plugin is going to let the `Girder` authetication to continue the process and review the internal database if the user is there.

# Requierements

- `keycloak:17.0.1` or newer
- `Python3`

# Installation
 In open the project folder and run:
 ```
 Python3 -m pip install .
 ```
 
# Running

The most convenient way to develop on `Keyckloak-login` is to use the devops scripts from the [Digital Slide Archive](https://github.com/DigitalSlideArchive/digital_slide_archive/tree/master/devops).

# Usage

## TODO

