# 📡 Sensors Monitor — интеграция для Home Assistant

## 🔧 Назначение
`sensors_monitor` — это кастомная интеграция для Home Assistant, которая позволяет:
- Отслеживать **состояние бинарных датчиков** (`binary_sensor`, например: движение, дверь, протечка, дым).
- Контролировать **значения обычных сенсоров** (`sensor`) с заданными порогами (`above`/`below`).
- Отправлять уведомления в разные каналы (`notify`, email, мобильные приложения).
- Озвучивать события через **Яндекс.Станции** (TTS).
- Формировать **периодические отчёты** (по расписанию и с интервалом).

---

## ⚙️ Возможности
1. **Binary Sensors**
   - При `ON`: уведомление «🚨 Тревога: Датчик движения (Гостиная)»
   - При `OFF`: уведомление «✅ Норма: Датчик движения (Гостиная)»

2. **Sensors с порогами**
   Задаются правила:
   ```yaml
   sensor.temperature_bedroom; above=28; message=🔥 Жарко в спальне: {value}°C
   sensor.humidity_bathroom; above=80; message=💧 Влажность в ванной: {value}%
   sensor.co2_office; above=1000; message=⚠️ Повышенный CO₂: {value} ppm
   sensor.temperature_kids; below=18; message=❄️ Холодно в детской: {value}°C
   ```
   - При превышении порога → уведомление/озвучка.
   - При возврате в норму → уведомление «✅ В норме».

3. **Уведомления**
   - `notify_on` — сервис уведомлений при `ON`
   - `notify_off` — сервис уведомлений при `OFF`
   - `notify_alerts` — куда слать тревоги по сенсорам и отчёты (можно несколько сервисов)
   - `notify_tts` — список `media_player` для озвучки событий

4. **Отчёты**
   - По интервалу (например, каждые 10 минут)
   - По расписанию (например, в 09:00 и 21:00)
   - В отчёте: список всех активных событий + длительность

5. **Сервис `sensors_monitor.send_report`**
   - Можно вызвать вручную через «Инструменты разработчика → Службы»
   - При вызове формирует отчёт и рассылает в `notify_alerts`

---

## 🛠️ Установка
1. Скопируй папку `custom_components/sensors_monitor/` в `/config/custom_components/`.
2. Перезапусти Home Assistant.
3. В настройках добавь новую интеграцию → **Sensors Monitor**.
4. Заполни поля в мастере:
   - Binary sensors
   - Thresholds (правила)
   - Notify On/Off/Alerts
   - Notify TTS (например, `media_player.yandex_station_spalnya`)
   - Interval (минуты)
   - Report Schedule (время отчётов, построчно)

---

## 📄 Пример конфигурации
```yaml
binary_sensors:
  - binary_sensor.motion_hall
  - binary_sensor.door_balcony

sensors_thresholds: |
  sensor.temperature_bedroom; above=28; message=🔥 Жарко в спальне: {value}°C
  sensor.humidity_bathroom; above=80; message=💧 Влажность в ванной: {value}%
  sensor.co2_office; above=1000; message=⚠️ CO₂ высокий: {value} ppm
  sensor.temperature_kids; below=18; message=❄️ Холодно в детской: {value}°C

notify_on: notify.dom
notify_off: notify.mobile_dom
notify_alerts: |
  notify.dom
  notify.email_dom
notify_tts: |
  media_player.yandex_station_detskaya
  media_player.yandex_station_gostinaya
  media_player.yandex_station_spalnya

interval: 15
report_schedule: |
  09:00
  21:00
```

---

## 🔔 Пример уведомлений
- 🚨 Тревога: Датчик движения в гостиной (ON)
- ✅ Норма: Датчик движения в гостиной (OFF)
- ⚠️ Порог: sensor.temperature_bedroom — Жарко в спальне: 29 °C
- ✅ В норме: sensor.temperature_bedroom
- ⏱️ Отчёт:
  ```
  • Датчик движения в гостиной (активно 0ч 12м 5с)
  • sensor.co2_office: ⚠️ CO₂ высокий: 1150 ppm
  ```

---

## 📢 Поддержка TTS
При включённых Яндекс.Станциях система может голосом озвучивать:
- «Тревога: датчик движения в гостиной»
- «Температура в спальне — жарко: 29 градусов»
- «Все датчики в норме»
