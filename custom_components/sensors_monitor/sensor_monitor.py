from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval, async_track_time_change, async_track_state_change_event
from homeassistant.util.dt import now
from .const import *

def _to_float(val):
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return None

async def async_setup_monitor(hass: HomeAssistant, entry_id: str, cfg: dict):
    binary_sensors = cfg[CONF_BINARY_SENSORS]
    sensors_plain = cfg[CONF_SENSORS_PLAIN]
    thresholds = cfg[CONF_THRESHOLDS]
    notify_on = cfg[CONF_NOTIFY_ON]
    notify_off = cfg[CONF_NOTIFY_OFF]
    notify_alerts = cfg[CONF_NOTIFY_ALERTS]
    notify_tts = cfg[CONF_NOTIFY_TTS]
    interval = cfg[CONF_INTERVAL]
    schedule = cfg[CONF_REPORT_SCHEDULE]

    threshold_entities = [r["entity_id"] for r in thresholds if "entity_id" in r]
    last_alert_state = {}

    async def _notify(service: str, title: str, message: str):
        await hass.services.async_call(
            "notify",
            service.split(".")[1] if "." in service else service,
            {"title": title, "message": message}
        )

    async def _broadcast(services, title: str, message: str):
        for srv in services:
            await _notify(srv, title, message)

    async def _speak(players, message: str):
        for p in players:
            await hass.services.async_call("tts", "yandex_station_say", {"entity_id": p, "message": message})

    def _check_threshold(state, rule):
        val = _to_float(state.state) if state else None
        if val is None:
            return False
        above = rule.get("above")
        below = rule.get("below")
        ok = True
        if above is not None and not (val > above):
            ok = False
        if below is not None and not (val < below):
            ok = False
        return ok

    def _format_msg(rule, val):
        msg = rule.get("message") or f"{rule['entity_id']} = {val}"
        return msg.replace("{value}", f"{val}")

    async def _report(_now):
        lines_bin = []
        lines_thr = []
        lines_plain = []

        # binary sensors active
        for ent in binary_sensors:
            st = hass.states.get(ent)
            if st and st.state == "on":
                delta = (now().timestamp() - st.last_changed.timestamp())
                h = int(delta // 3600); m = int((delta % 3600) // 60); s = int(delta % 60)
                lines_bin.append(f"• {st.name} (активно {h}ч {m}м {s}с)")

        # thresholds
        for r in thresholds:
            ent = r["entity_id"]
            st = hass.states.get(ent)
            if _check_threshold(st, r):
                val = _to_float(st.state)
                lines_thr.append(f"• {ent}: {_format_msg(r, val)}")

        # plain sensors
        for ent in sensors_plain:
            st = hass.states.get(ent)
            if st:
                unit = st.attributes.get('unit_of_measurement', '')
                unit = f" {unit}" if unit else ""
                lines_plain.append(f"• {st.name}: {st.state}{unit}")

        msg = []
        if lines_bin:
            msg.append("📡 Binary Sensors:\n" + "\n".join(lines_bin))
        if lines_thr:
            msg.append("🌡 Threshold Sensors:\n" + "\n".join(lines_thr))
        if lines_plain:
            msg.append("📊 Plain Sensors:\n" + "\n".join(lines_plain))

        if msg:
            text = "\n\n".join(msg)
            await _broadcast(notify_alerts, "📈 Отчёт датчиков", text)
            if notify_tts:
                await _speak(notify_tts, f"Отчёт по датчикам: {len(lines_bin)} бинарных, {len(lines_thr)} пороговых, {len(lines_plain)} обычных")

    # interval & schedule
    async_track_time_interval(hass, _report, timedelta(minutes=interval))
    for hh, mm in schedule:
        async_track_time_change(hass, _report, hour=hh, minute=mm)

    @callback
    async def _bin_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if not new or not old or ent not in binary_sensors:
            return
        if new.state == "on" and old.state != "on":
            await _notify(notify_on, f"🚨 Тревога: {new.name}", "Датчик перешёл в ON")
            if notify_tts:
                await _speak(notify_tts, f"{new.name} тревога")
        elif new.state == "off" and old.state != "off":
            await _notify(notify_off, f"✅ Норма: {old.name}", "Датчик перешёл в OFF")
            if notify_tts:
                await _speak(notify_tts, f"{old.name} в норме")

    async_track_state_change_event(hass, binary_sensors, _bin_changed)

    @callback
    async def _thr_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        if not new or ent not in threshold_entities:
            return
        rules = [r for r in thresholds if r.get("entity_id") == ent]
        in_alert = any(_check_threshold(new, r) for r in rules)
        was_alert = last_alert_state.get(ent, False)

        if in_alert and not was_alert:
            for r in rules:
                if _check_threshold(new, r):
                    val = _to_float(new.state)
                    msg = _format_msg(r, val)
                    await _broadcast(notify_alerts, f"⚠️ Порог: {ent}", msg)
                    if notify_tts:
                        await _speak(notify_tts, msg)
            last_alert_state[ent] = True
        elif (not in_alert) and was_alert:
            await _broadcast(notify_alerts, f"✅ В норме: {ent}", "Показания в норме")
            if notify_tts:
                await _speak(notify_tts, f"{ent} в норме")
            last_alert_state[ent] = False

    async_track_state_change_event(hass, threshold_entities, _thr_changed)

    async def handle_send_report(call):
        await _report(now())
    hass.services.async_register(DOMAIN, "send_report", handle_send_report)
