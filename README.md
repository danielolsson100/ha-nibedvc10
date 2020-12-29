# ha-nibedvc10

NIBE DVC 10 command and control script to be used from Home Assistant.

https://www.nibe.eu/sv-se/produkter/ventilation/dvc-10

No API doc is not available from vendor, the code is done by reverse engineering the network traffic

## Setup

1. Copy the script to `<config dir>/python_scripts/nibe_dvc10.py`
2. Modify your `<config dir>/configuration.yaml` like below
3. Restart Home Assistant and add the switch to your GUI in HA

```yaml
- platform: command_line
  switches:
    nibe_dvc10_office:
      friendly_name: NIBE DVC 10 - Office
      command_on: "python3 /config/python_scripts/nibe_dvc10.py 192.168.1.20 start"
      command_off: "python3 /config/python_scripts/nibe_dvc10.py 192.168.1.20 stop"
```
