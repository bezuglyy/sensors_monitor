from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import *
from .sensor_monitor import async_setup_monitor

def _as_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        parts = [p.strip() for p in value.replace("\r", "").replace("\n", ",").split(",")]
        return [p for p in parts if p]
    return []

def _parse_schedule(value):
    items = value if isinstance(value, list) else str(value).splitlines()
    times = []
    for line in items:
        line = line.strip()
        if not line:
            continue
        try:
            hh, mm = [int(x) for x in line.split(":")]
            times.append((hh, mm))
        except Exception:
            continue
    return times

def _parse_thresholds(text):
    rules = []
    if not text:
        return rules
    lines = text if isinstance(text, list) else str(text).splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(";")]
        if not parts:
            continue
        entity_id = parts[0]
        if not entity_id:
            continue
        rule = {"entity_id": entity_id}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                if k in ("above", "below"):
                    try:
                        rule[k] = float(v.replace(",", "."))
                    except Exception:
                        pass
                elif k == "message":
                    rule[k] = v
        rules.append(rule)
    return rules

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    cfg = {**entry.data, **entry.options}

    binary_sensors = _as_list(cfg.get(CONF_BINARY_SENSORS, []))
    sensors_plain = _as_list(cfg.get(CONF_SENSORS_PLAIN, []))
    thresholds = _parse_thresholds(cfg.get(CONF_THRESHOLDS, ""))

    notify_on = cfg.get(CONF_NOTIFY_ON, "notify.dom")
    notify_off = cfg.get(CONF_NOTIFY_OFF, "notify.dom")
    notify_alerts = _as_list(cfg.get(CONF_NOTIFY_ALERTS, "notify.dom"))
    notify_tts = _as_list(cfg.get(CONF_NOTIFY_TTS, []))
    interval = int(cfg.get(CONF_INTERVAL, 10))
    schedule = _parse_schedule(cfg.get(CONF_REPORT_SCHEDULE, []))

    norm = {
        CONF_BINARY_SENSORS: binary_sensors,
        CONF_SENSORS_PLAIN: sensors_plain,
        CONF_THRESHOLDS: thresholds,
        CONF_NOTIFY_ON: notify_on,
        CONF_NOTIFY_OFF: notify_off,
        CONF_NOTIFY_ALERTS: notify_alerts if notify_alerts else ["notify.dom"],
        CONF_NOTIFY_TTS: notify_tts,
        CONF_INTERVAL: interval,
        CONF_REPORT_SCHEDULE: schedule,
    }
    hass.data[DOMAIN][entry.entry_id] = norm
    await async_setup_monitor(hass, entry.entry_id, norm)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
