# SmartCocoon API

This Python library allows you to control [SmartCocoon fans](https://mysmartcocoon.com/).

## Status

This is not an official API from SmartCocoon and is in the the very early stages of developement.

This API is built for the main purpose of integrating into Home Assistant but can be used independently.

### Supported devices

* SmartCocoon Smart Vents

## Features

The following feature are supported:

* Connect to the SmartCocoon cloud service
* Obtain configuration data as it has been set up through the SmartCocoon mobile app
* Ability to control fans
    * Turn on/off
    * Set speed
    * Set Auto mode
    * Set Eco mode

## Examples

You can refer to the tests/test_integration.py to see an example of integration with the
SmartCocoon API

## Work to do

* The fans are using MQTT but this is not being leveraged yet
* Discovery has not been implemented, not sure if this is possible
* Fan status will currently require polling if the fan is changed directly in the app