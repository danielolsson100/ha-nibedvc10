"""Constants for the NIBE DVC 10 integration."""

DOMAIN = "nibe_dvc10"

UDP_PORT = 4000
SCAN_INTERVAL = 30  # seconds

# UDP protocol — base header "mobile" in ASCII hex
_BASE_HEX = "6d6f62696c65"

CMD_GET_STATUS     = _BASE_HEX + "010d"
CMD_TOGGLE_POWER   = _BASE_HEX + "030d"
CMD_FAN_LOW        = _BASE_HEX + "0401"
CMD_FAN_MEDIUM     = _BASE_HEX + "0402"
CMD_FAN_HIGH       = _BASE_HEX + "0403"
CMD_AIRFLOW_ONEWAY = _BASE_HEX + "0600"
CMD_AIRFLOW_TWOWAY = _BASE_HEX + "0601"
CMD_AIRFLOW_IN     = _BASE_HEX + "0602"
CMD_TOGGLE_MODE    = _BASE_HEX + "0901"

# Status response byte indices
IDX_POWER        = 7   # 01=ON, 00=OFF
IDX_MODE         = 9   # 00=Day, 01=Night, 02=Party
IDX_FAN          = 19  # 01=Low, 02=Medium, 03=High, 04=Manual
IDX_FAN_MANUAL   = 21  # 0x00=9% ... 0xFF=100% (manual speed percentage)
IDX_AIRFLOW      = 23  # 00=OneWay, 01=TwoWay, 02=In

# Select option values
FAN_SPEED_LOW    = "low"
FAN_SPEED_MEDIUM = "medium"
FAN_SPEED_HIGH   = "high"
FAN_SPEEDS = [FAN_SPEED_LOW, FAN_SPEED_MEDIUM, FAN_SPEED_HIGH]

MODE_DAY   = "day"
MODE_NIGHT = "night"
MODES = [MODE_DAY, MODE_NIGHT]

AIRFLOW_ONEWAY = "one_way"
AIRFLOW_TWOWAY = "two_way"
AIRFLOW_IN     = "in"
AIRFLOWS = [AIRFLOW_ONEWAY, AIRFLOW_TWOWAY, AIRFLOW_IN]

# Lookup maps (raw byte → option string)
FAN_BYTE_TO_OPT     = {1: FAN_SPEED_LOW, 2: FAN_SPEED_MEDIUM, 3: FAN_SPEED_HIGH}
MODE_BYTE_TO_OPT    = {0: MODE_DAY, 1: MODE_NIGHT}
AIRFLOW_BYTE_TO_OPT = {0: AIRFLOW_ONEWAY, 1: AIRFLOW_TWOWAY, 2: AIRFLOW_IN}
