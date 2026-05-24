# OpenAQ — Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/crionline/openaq-ha)](https://github.com/crionline/openaq-ha/releases)
[![License](https://img.shields.io/github/license/crionline/openaq-ha)](LICENSE)

A custom Home Assistant integration that pulls **air quality data** from [OpenAQ](https://openaq.org) (v3 API) and exposes each sensor as a `sensor` entity.

---

## Installation via HACS (recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=crionline&repository=openaq-ha&category=integration)

1. Click the button above, or manually:
   - Open HACS → Integrations → ⋮ → Custom Repositories
   - Add `https://github.com/crionline/openaq-ha` as type **Integration**
2. Search for **OpenAQ** and install it
3. Restart Home Assistant

---

## Manual Installation

1. Copy the `custom_components/openaq/` folder into your HA `config/custom_components/` directory
2. Restart Home Assistant

---

## Configuration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=openaq)

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **OpenAQ**
3. **Step 1 – API Key**: Enter your OpenAQ API key (get one free at [explore.openaq.org/register](https://explore.openaq.org/register))
4. **Step 2 – Select location**: A list of air quality stations within 15 km of your HA home location is shown automatically. Select one, or enable manual entry to type a location ID directly.

---

## Features

- Fetches all sensors available for a given OpenAQ location
- Exposes each parameter (NO₂, O₃, PM2.5, PM10, SO₂, CO, …) as a `sensor` entity
- Updates every **2 hours** (matching typical hourly data availability)
- Exposes extra attributes: latest datetime (local & UTC), summary min/max/avg/median
- Icons per parameter type
- Config flow via UI — no YAML needed
- Italian and English translations included

---

## Entities

For each sensor in the location, an entity is created:

| Entity ID | Example value |
|---|---|
| `sensor.openaq_no2` | NO₂ in µg/m³ |
| `sensor.openaq_o3` | O₃ in µg/m³ |
| `sensor.openaq_pm25` | PM2.5 in µg/m³ |
| `sensor.openaq_pm10` | PM10 in µg/m³ |

### Attributes

| Attribute | Description |
|---|---|
| `latest_datetime_local` | Timestamp of latest measurement (local time) |
| `latest_datetime_utc` | Timestamp of latest measurement (UTC) |
| `display_name` | Human-readable parameter name (e.g. NO₂ mass) |
| `summary_min` | Historical minimum |
| `summary_max` | Historical maximum |
| `summary_avg` | Historical average |
| `summary_median` | Historical median |
| `sensor_id` | OpenAQ internal sensor ID |

---

## API Key

OpenAQ offers a free API key. Register at [explore.openaq.org/register](https://explore.openaq.org/register). The key is required to authenticate all requests to the OpenAQ v3 API.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
