# 🌬️ OpenAQ for Home Assistant

> **A Home Assistant custom integration that brings real-time outdoor air quality data into your smart home dashboard — powered by the OpenAQ v3 API.**

Monitor NO₂, O₃, PM2.5, PM10 and more directly from your nearest government-certified air quality monitoring station, without writing a single line of YAML.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/crionline/openaq-ha)](https://github.com/crionline/openaq-ha/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-41BDF5.svg)](https://www.home-assistant.io)
[![OpenAQ API](https://img.shields.io/badge/OpenAQ-v3%20API-00A5E0.svg)](https://docs.openaq.org)

<a href="https://buymeacoffee.com/lanec" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50"></a>

---

## 🤔 Why Use This Integration?

Setting up air quality monitoring in Home Assistant typically means:
- Finding the right API manually
- Writing custom `rest` sensors and parsing JSON templates
- Dealing with authentication headers in YAML
- Hardcoding sensor IDs with no UI feedback

**OpenAQ for HA removes all of that.** Install via HACS, enter your API key, and the integration automatically discovers the nearest certified monitoring stations based on your Home Assistant home coordinates. Pick a station from the list and you're done — no YAML, no REST templates, no manual sensor IDs.

---

## ⚡ Quick Start

### Prerequisites

- Home Assistant 2023.1 or newer
- [HACS](https://hacs.xyz) installed
- A free OpenAQ API key → [explore.openaq.org/register](https://explore.openaq.org/register)

### 1 — Install via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=crionline&repository=openaq-ha&category=integration)

Click the button above, or manually:

```
HACS → Integrations → ⋮ → Custom Repositories
→ URL: https://github.com/crionline/openaq-ha
→ Category: Integration
→ Install → Restart Home Assistant
```

### 2 — Add the Integration

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=openaq)

Or manually: **Settings → Devices & Services → Add Integration → search "OpenAQ"**

### 3 — Configure

**Step 1 – API Key**

Enter your OpenAQ API key. The integration validates it immediately.

**Step 2 – Select your monitoring station**

A list of certified air quality stations within **15 km** of your HA home location appears automatically:

```
● Berlin Wedding – Amrumer Str. (DE)
● Berlin Mitte – Karl-Marx-Allee (DE)
● Berlin Neukölln – Silbersteinstraße (DE)
```

Select one — or toggle **"Enter location ID manually"** for advanced use.

### 4 — Done ✅

Entities are created immediately:

```yaml
sensor.openaq_no2    # NO₂ mass in µg/m³
sensor.openaq_o3     # O₃ mass in µg/m³
sensor.openaq_pm25   # PM2.5 in µg/m³
```

---

## 🗂️ Project Structure

```
openaq-ha/
├── custom_components/
│   └── openaq/
│       ├── __init__.py          # Entry setup + DataUpdateCoordinator (2h polling)
│       ├── api.py               # Async OpenAQ v3 API client (aiohttp)
│       ├── config_flow.py       # 2-step UI config flow (API key → location picker)
│       ├── sensor.py            # SensorEntity per parameter (NO₂, O₃, PM2.5…)
│       ├── const.py             # Domain, base URL, polling interval, radius
│       ├── manifest.json        # HA integration metadata
│       ├── strings.json         # UI strings
│       └── translations/
│           ├── en.json          # English
│           └── it.json          # Italian
├── hacs.json                    # HACS metadata
├── LICENSE
└── README.md
```

---

## 📊 Sensor Entities & Attributes

Each parameter exposed by the station becomes a separate `sensor` entity.

| Entity ID | Parameter | Unit |
|---|---|---|
| `sensor.openaq_no2` | Nitrogen Dioxide | µg/m³ |
| `sensor.openaq_o3` | Ozone | µg/m³ |
| `sensor.openaq_pm25` | Fine Particulate Matter | µg/m³ |
| `sensor.openaq_pm10` | Coarse Particulate Matter | µg/m³ |
| `sensor.openaq_so2` | Sulphur Dioxide | µg/m³ |
| `sensor.openaq_co` | Carbon Monoxide | µg/m³ |

Every entity also exposes these **extra state attributes**:

| Attribute | Description |
|---|---|
| `latest_datetime_local` | Timestamp of the latest measurement (local timezone) |
| `latest_datetime_utc` | Timestamp of the latest measurement (UTC) |
| `display_name` | Human-readable parameter name (e.g. `NO₂ mass`) |
| `summary_min` | Historical minimum value |
| `summary_max` | Historical maximum value |
| `summary_avg` | Historical average value |
| `summary_median` | Historical median value |
| `sensor_id` | OpenAQ internal sensor ID |

---

## 🔧 Manual Installation

If you prefer not to use HACS:

```bash
# From your Home Assistant config directory
mkdir -p custom_components/openaq
cd custom_components/openaq

# Clone or copy the integration files
git clone https://github.com/crionline/openaq-ha.git /tmp/openaq-ha
cp -r /tmp/openaq-ha/custom_components/openaq/* .
```

Then restart Home Assistant and proceed with the configuration steps above.

---

## 🗺️ Roadmap

- [ ] **Options Flow** — change polling interval and search radius after setup, without removing and re-adding the integration
- [ ] **Multiple locations** — monitor more than one station simultaneously (e.g. home vs. workplace)
- [ ] **AQI calculation** — compute a composite Air Quality Index from available parameters and expose it as an additional sensor

---

## 📄 License

Distributed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Credits

- Air quality data provided by [OpenAQ](https://openaq.org) — open, real-time air quality data from government monitoring networks worldwide.
- Built for the [Home Assistant](https://www.home-assistant.io) ecosystem.
