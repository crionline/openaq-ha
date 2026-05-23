# OpenAQ — Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration that pulls **air quality data** from [OpenAQ](https://openaq.org) (v3 API) and exposes each sensor as a `sensor` entity.

## Features

- Fetches all sensors available for a given OpenAQ location
- Exposes each parameter (NO₂, O₃, PM2.5, PM10, SO₂, CO, …) as a `sensor` entity
- Updates every **2 hours** (matching typical hourly data availability)
- Exposes extra attributes: latest datetime (local & UTC), summary min/max/avg/median
- Icons per parameter type
- Config flow via UI (no YAML needed)

## Installation via HACS

1. Open HACS → Integrations → ⋮ → Custom Repositories
2. Add `https://github.com/crionline/openaq-ha` as type **Integration**
3. Search for **OpenAQ** and install
4. Restart Home Assistant

## Manual Installation

1. Copy `custom_components/openaq/` into your HA `config/custom_components/` folder
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **OpenAQ**
3. Enter:
   - **API Key**: get one free at [openaq.org](https://explore.openaq.org/register)
   - **Location ID**: e.g. `8433` for Orbassano - Gozzano (Turin)

## Entities created

For each sensor in the location, an entity is created:

| Entity ID | Example |
|---|---|
| `sensor.openaq_no2` | NO₂ in µg/m³ |
| `sensor.openaq_o3` | O₃ in µg/m³ |
| `sensor.openaq_pm25` | PM2.5 in µg/m³ |

### Attributes

| Attribute | Description |
|---|---|
| `latest_datetime_local` | Timestamp of latest measurement (local time) |
| `latest_datetime_utc` | Timestamp of latest measurement (UTC) |
| `display_name` | Human-readable parameter name |
| `summary_min` | Historical minimum |
| `summary_max` | Historical maximum |
| `summary_avg` | Historical average |
| `summary_median` | Historical median |
| `sensor_id` | OpenAQ internal sensor ID |

## API Key

OpenAQ offers a free API key. Register at [explore.openaq.org/register](https://explore.openaq.org/register).
