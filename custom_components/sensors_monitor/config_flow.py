import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig, TextSelector, NumberSelector
from .const import *

def _normalize_ml(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        parts = []
        for chunk in value.replace("\r", "").split("\n"):
            parts.extend(chunk.split(","))
        return [p.strip() for p in parts if p.strip()]
    return []

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            user_input[CONF_NOTIFY_ALERTS] = _normalize_ml(user_input.get(CONF_NOTIFY_ALERTS, "notify.dom"))
            user_input[CONF_NOTIFY_TTS] = _normalize_ml(user_input.get(CONF_NOTIFY_TTS, []))
            return self.async_create_entry(title="Мониторинг датчиков", data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_BINARY_SENSORS): EntitySelector(
                EntitySelectorConfig(domain=["binary_sensor"], multiple=True)
            ),
            vol.Optional(CONF_SENSORS_PLAIN): EntitySelector(
                EntitySelectorConfig(domain=["sensor"], multiple=True)
            ),
            vol.Optional(CONF_THRESHOLDS, default=""): TextSelector({"multiline": True}),

            vol.Required(CONF_NOTIFY_ON, default="notify.dom"): TextSelector({"multiline": False}),
            vol.Required(CONF_NOTIFY_OFF, default="notify.dom"): TextSelector({"multiline": False}),
            vol.Required(CONF_NOTIFY_ALERTS, default="notify.dom"): TextSelector({"multiline": True}),
            vol.Optional(CONF_NOTIFY_TTS, default=""): TextSelector({"multiline": True}),

            vol.Required(CONF_BINARY_INTERVAL, default=10): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),
            vol.Required(CONF_THRESHOLD_INTERVAL, default=10): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),
            vol.Required(CONF_PLAIN_INTERVAL, default=10): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),

            vol.Optional(CONF_BINARY_SCHEDULE, default="08:00\n20:00"): TextSelector({"multiline": True}),
            vol.Optional(CONF_THRESHOLD_SCHEDULE, default="09:00\n21:00"): TextSelector({"multiline": True}),
            vol.Optional(CONF_PLAIN_SCHEDULE, default="10:00\n22:00"): TextSelector({"multiline": True}),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlow(config_entry)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            user_input[CONF_NOTIFY_ALERTS] = _normalize_ml(user_input.get(CONF_NOTIFY_ALERTS, "notify.dom"))
            user_input[CONF_NOTIFY_TTS] = _normalize_ml(user_input.get(CONF_NOTIFY_TTS, []))
            return self.async_create_entry(title="", data=user_input)

        data = self.config_entry.data
        options = self.config_entry.options
        def _get(k, d=None): return options.get(k, data.get(k, d))

        alerts_val = _get(CONF_NOTIFY_ALERTS, "notify.dom")
        alerts_text = "\n".join(alerts_val) if isinstance(alerts_val, list) else str(alerts_val)
        tts_val = _get(CONF_NOTIFY_TTS, [])
        tts_text = "\n".join(tts_val) if isinstance(tts_val, list) else str(tts_val)

        schema = vol.Schema({
            vol.Optional(CONF_BINARY_SENSORS, default=_get(CONF_BINARY_SENSORS, [])): EntitySelector(
                EntitySelectorConfig(domain=["binary_sensor"], multiple=True)
            ),
            vol.Optional(CONF_SENSORS_PLAIN, default=_get(CONF_SENSORS_PLAIN, [])): EntitySelector(
                EntitySelectorConfig(domain=["sensor"], multiple=True)
            ),
            vol.Optional(CONF_THRESHOLDS, default=_get(CONF_THRESHOLDS, "")): TextSelector({"multiline": True}),

            vol.Required(CONF_NOTIFY_ON, default=_get(CONF_NOTIFY_ON, "notify.dom")): TextSelector({"multiline": False}),
            vol.Required(CONF_NOTIFY_OFF, default=_get(CONF_NOTIFY_OFF, "notify.dom")): TextSelector({"multiline": False}),
            vol.Required(CONF_NOTIFY_ALERTS, default=alerts_text): TextSelector({"multiline": True}),
            vol.Optional(CONF_NOTIFY_TTS, default=tts_text): TextSelector({"multiline": True}),

            vol.Required(CONF_BINARY_INTERVAL, default=_get(CONF_BINARY_INTERVAL, 10)): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),
            vol.Required(CONF_THRESHOLD_INTERVAL, default=_get(CONF_THRESHOLD_INTERVAL, 10)): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),
            vol.Required(CONF_PLAIN_INTERVAL, default=_get(CONF_PLAIN_INTERVAL, 10)): NumberSelector({"min": 1, "max": 120, "mode": "slider"}),

            vol.Optional(CONF_BINARY_SCHEDULE, default=_get(CONF_BINARY_SCHEDULE, "08:00\n20:00")): TextSelector({"multiline": True}),
            vol.Optional(CONF_THRESHOLD_SCHEDULE, default=_get(CONF_THRESHOLD_SCHEDULE, "09:00\n21:00")): TextSelector({"multiline": True}),
            vol.Optional(CONF_PLAIN_SCHEDULE, default=_get(CONF_PLAIN_SCHEDULE, "10:00\n22:00")): TextSelector({"multiline": True}),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
