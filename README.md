# 📡 Sensors Monitor — интеграция для Home Assistant

Интеграция отслеживает:
- 📡 **Binary Sensors** (`binary_sensor`) — тревоги при ON/OFF
- 🌡 **Threshold Sensors** (`sensor` с правилами `above`/`below`)
- 📊 **Plain Sensors** (`sensor`) — просто текущие значения в отчётах

Уведомления: `notify_on`, `notify_off`, `notify_alerts`, TTS на Яндекс.Станциях.
Отчёты: по интервалу и по расписанию. Сервис: `sensors_monitor.send_report`.

## Пример
```yaml
binary_sensors:
  - binary_sensor.motion_hall

sensors_plain:
  - sensor.temperature_humidity_sensor_aeeb_temperature

sensors_thresholds: |
  sensor.co2_office; above=1000; message=⚠️ CO₂ высокий: {value} ppm

notify_on: notify.dom
notify_off: notify.mobile_dom
notify_alerts: |
  notify.dom
  notify.email_dom
notify_tts: |
  media_player.yandex_station_spalnya

interval: 10
report_schedule: |
  09:00
  21:00
```
