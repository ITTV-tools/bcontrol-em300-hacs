# BControl EM300 for Home Assistant

Custom Home Assistant integration for B-Control EM300 energy meters.

## Features

- Config flow setup from Home Assistant UI
- Polling via `bcontrolpy`
- Automatic creation of meter sensors
- Device registration in Home Assistant
- Configurable polling interval via integration options
- Excludes static values (for example serial and status) from sensor entities

## Installation (HACS)

1. Open HACS in Home Assistant
2. Go to `Integrations`
3. Add this repository as a custom repository (category: Integration)
4. Install `BControl EM300`
5. Restart Home Assistant
6. Add integration: `Settings -> Devices & services -> Add integration`

## Configuration

During setup, enter:

- Host (IP or hostname)
- Password

After setup, open the integration options to change:

- Polling interval (seconds)

## Development notes

- Domain: `bcontrol_em300`
- Main library: `bcontrolpy==0.0.7`

## Support

- Issues: https://github.com/ITTV-Tools/bcontrol-em300-hacs/issues
