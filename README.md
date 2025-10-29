![Мониторинг датчиков](custom_components/sensors_monitor/icons/banner.png)

# 📡 Sensors Monitor — Home Assistant (v1.2.0)

Интеграция для уведомлений и отчётов по датчикам:
- 📡 **Binary Sensors** (`binary_sensor`) — тревоги при ON/OFF
- 🌡 **Threshold Sensors** (`sensor` с правилами `above`/`below`)
- 📊 **Plain Sensors** (`sensor`) — значения в отчётах

🆕 В v1.2.0: **отдельные интервалы и расписания** для каждого типа сенсоров.

## ⚙️ Пример конфигурации
```yaml
binary_sensors:
  - binary_sensor.motion_hall
  - binary_sensor.door_balcony

sensors_plain:
  - sensor.ble_temperature
  - sensor.temperature_humidity_sensor_aeeb_temperature

sensors_thresholds: |
  sensor.temperature_bedroom; above=28; message=🔥 Жарко в спальне: {value}°C
  sensor.co2_office; above=1000; message=⚠️ CO₂ высокий: {value} ppm

notify_on: notify.dom
notify_off: notify.mobile_dom
notify_alerts: |
  notify.dom
  notify.email_dom
notify_tts: |
  media_player.yandex_station_spalnya

binary_interval: 5
threshold_interval: 15
plain_interval: 30

binary_schedule: |
  08:00
  20:00
threshold_schedule: |
  09:00
  21:00
plain_schedule: |
  10:00
  22:00
```

## Сервис
`switches_monitor.send_report` — вручную формирует отчёт (все типы).

## Установка
1. Скопируйте `custom_components/sensors_monitor` в `/config/custom_components/`
2. Перезапустите Home Assistant
3. Добавьте интеграцию через UI


👨‍💻 Разработчик: **Евгений Безумный**
