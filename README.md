# NIBE DVC 10 — Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/danielolsson100/ha-nibedvc10?label=release)](https://github.com/danielolsson100/ha-nibedvc10/releases)

Local integration for the **NIBE DVC 10** ventilation unit. Communicates directly over UDP (port 4000) using the reverse-engineered device protocol — no cloud, no account required.

## Features

| Entity | Type | Description |
|--------|------|-------------|
| Power | Switch | Turn the unit on or off |
| Fan Speed | Select | Low / Medium / High preset |
| Mode | Select | Day / Night |
| Airflow Direction | Select | Supply (one-way) / Balanced (two-way) / Intake only |
| Fan Speed | Sensor | Current fan speed (read-only) |
| Mode | Sensor | Current mode (read-only) |
| Airflow Direction | Sensor | Current airflow direction (read-only) |
| Manual Fan Speed | Sensor | Manual fan speed percentage (9–100 %) |

## Requirements

- Home Assistant 2024.1 or newer
- NIBE DVC 10 ventilation unit on the same local network
- UDP port 4000 reachable from the Home Assistant host

## Installation

### HACS (recommended)

1. In Home Assistant, go to **HACS → Integrations**.
2. Click the three-dot menu (⋮) in the top right and choose **Custom repositories**.
3. Add `https://github.com/danielolsson100/ha-nibedvc10` as an **Integration**.
4. Search for **NIBE DVC 10** and click **Download**.
5. Restart Home Assistant.

### Manual

1. Copy the `custom_components/nibe_dvc10` directory into your Home Assistant `custom_components` folder.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **NIBE DVC 10**.
3. Enter the IP address of your ventilation unit on the local network.
4. Click **Submit** — the integration will verify connectivity before saving.

The IP address can be changed later via the **Configure** button on the integration card.

## Protocol notes

The DVC 10 communicates over UDP port 4000 using an undocumented protocol. Commands begin with the ASCII prefix `mobile` (`6d6f62696c65`) followed by a command byte pair. Status responses begin with `master` (`6d617374657200`) and carry a ~36-byte payload encoding power, mode, fan speed, and airflow state.

This implementation was reverse-engineered from device traffic — there are no official vendor documents.

## License

MIT — see [LICENSE](LICENSE).
