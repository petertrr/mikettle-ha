from mikettle.mikettle import (
    MI_ACTION,
    MI_MODE,
    MI_SET_TEMPERATURE,
    MI_CURRENT_TEMPERATURE,
    MI_KW_TYPE,
    MI_CURRENT_KW_TIME,
    MI_SET_KW_TIME,
)
from datetime import timedelta

CONF_PRODUCT_ID = "product_id"

DEFAULT_PRODUCT_ID = 275
DEFAULT_FORCE_UPDATE = False
DEFAULT_NAME = "Mi Kettle"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)

# Sensor types are defined like: Name, units, icon
SENSOR_TYPES = {
    MI_ACTION: ["Action", "", "mdi:state-machine"],
    MI_MODE: ["Mode", "", "mdi:settings-outline"],
    MI_SET_TEMPERATURE: ["Set temperature", "°C", "mdi:thermometer-lines"],
    MI_CURRENT_TEMPERATURE: ["Current temperature", "°C", "mdi:thermometer"],
    MI_KW_TYPE: ["Keep warm type", "", "mdi:thermostat"],
    MI_CURRENT_KW_TIME: ["Keep warm time", "min", "mdi:clock-outline"],
    MI_SET_KW_TIME: ["Set keep warm time", "min", "mdi:clock-outline"]
}