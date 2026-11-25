# noise-floor-data

Public raw data archive for [Noisefloor](https://github.com/metacog-osint/noise-floor): hourly ESA ionospheric
scintillation grids, daily copies of EASA's GNSS interference tables, and earlier copies of a Baltic navigational
warnings page (made 26 Oct to 21 Nov 2026; no new files are added).

> **Using the ESA data means accepting ESA's terms.** By accessing, downloading or using anything under `ism/`, you
> accept the [ESA S2P Space Weather Data Terms and Conditions](https://swe.ssa.esa.int/documents/d/guest/s2p_swe_data_terms_and_conditions).
> If you do not accept them, do not access, download or use this data. If you pass the data on, the recipient must
> accept the same terms.
>
> Data provided by the European Space Agency (ESA) as part of its Space Safety Programme (S2P). © ESA (year of reception).

## ESA data terms

This is a summary of the terms as read on 21 Nov 2026. ESA's text controls if the two differ.

- **Use:** the data may be used for peaceful purposes, including scientific, technical, educational and application
  development work, and in derived products and services (3.1).
- **No commercial gain:** the data may not be sold, licensed or redistributed to third parties for commercial gain (3.1).
- **Passing it on:** these free datasets may be redistributed only to third parties who accept ESA's terms, and whoever
  redistributes them is responsible to ESA for that acceptance (3.2).
- **Required credit:** any publication, product or other work that uses the data must cite the dataset and state "Data
  provided by the European Space Agency (ESA) as part of its Space Safety Programme (S2P)" (3.3). It must also attribute
  "© ESA (year of reception)", for example © ESA 2026 for data received in 2026 (4.3).
- **No endorsement:** do not state or imply that ESA or its staff endorse a product, process or service (3.1).
- **Rights and warranty:** ESA keeps all rights in the data (4.1) and provides it as is, without warranty (5.3). This
  repository grants no licence of its own to the data.

## ism/: ESA SWE ISM ionospheric nowcast archive

ESA's Ionospheric Scintillation Monitoring service (CLS, on the ESA Space Weather Service Network) publishes a worldwide
nowcast of amplitude scintillation (S4), phase scintillation (sigma-phi) and TEC on a 2.5° grid, but only the current
hour; there is no public archive. `.github/workflows/ism-hourly.yml` runs `capture/ism_capture.py` twice an hour (:11 and :41 UTC)
and commits each new valid hour.

| Path | Contents |
|---|---|
| `ism/grid.csv` | Cell order (lon, lat), 145 × 71 = 10,295 cells |
| `ism/YYYY/MM/ism_YYYYMMDDTHHZ.csv.gz` | One valid hour. S4 and sigma-phi (rad) × 1000, their errors × 100; TEC and error in whole TECU |
| `ism/summary.csv` | One row per valid hour: global and per-region max S4 and sigma-phi; counts of cells at ICAO GNSS moderate/severe (S4 0.5/0.8, sigma-phi 0.4/0.7 rad) |

About 27 KB per hour (~240 MB a year). ESA posts each nowcast about 2 hours after its valid time. Hours are missed if
no capture runs while an hour is current; gaps show in `summary.csv`.

**Two capture machines (from 26 Oct 2026).** GitHub ran the twice-hourly schedule only every 2-5 hours (25 of about
120 hours kept, 21-26 Oct), so the capture also runs every 30 minutes (:26 and :56 UTC) from a second machine, using
Noisefloor's `collectors/ism_local.py`. Its commits are marked "(local)". GitHub stays on as the backup. Files are
byte-identical whichever machine captures an hour, and `summary.csv` merges by union (`.gitattributes`), so a rare
double capture can leave two rows for one hour: dedupe on `valid_utc`.

## notices/: daily copies of official notice pages

These pages show only what is current, so dated copies keep a history. They are historical copies and are not for
navigation.

| Path | Contents |
|---|---|
| `notices/easa/YYYY-MM-DD.json` | EASA's tables of FIRs with GNSS interference reports (7 and 30 days), one file per UTC day |
| `notices/easa/wayback-<timestamp>.json` | The same tables, parsed from Internet Archive copies of EASA's page |
| `notices/baltico/YYYY-MM-DD.html.gz` | Copies made 26 Oct to 21 Nov 2026 of the Swedish Maritime Administration's page of Baltic navigational warnings in force (BALTICO). No new files are added |
| `notices/baltico/YYYY-MM-DD.json` | The warnings parsed from those copies, with GNSS-related ones marked |

- **EASA:** source: European Union Aviation Safety Agency (EASA), "GNSS outages and alterations". EASA allows
  reproduction with the source acknowledged.
- **BALTICO:** source: [Swedish Maritime Administration](https://navvarn.sjofartsverket.se/en/Navigationsvarningar/).
  The page states no terms. This repository grants no licence to these copies, and all rights stay with the publisher.
  Noisefloor's daily capture of this page no longer writes here.

## AI assistance

This repository is built with AI coding assistance (Anthropic's Claude Code). The Intelligence Company is responsible for everything published here.
