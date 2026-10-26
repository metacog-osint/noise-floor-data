# noise-floor-data (private)

Raw data archives for [Noise Floor](https://github.com/metacog-osint/noise-floor) that cannot be published.

## ism/ — ESA SWE ISM ionospheric nowcast archive

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
120 hours kept, 21-26 Oct), so the capture also runs every 30 minutes (:26 and :56 UTC) from Tom's PC: Noise Floor's
`collectors/ism_local.py`, Windows task "noise-floor ESA scintillation capture", commits marked "(local)". GitHub
stays on as the backup. Files are byte-identical whichever machine captures an hour, and `summary.csv` merges by
union (`.gitattributes`), so a rare double capture can leave two rows for one hour: dedupe on `valid_utc`.

### Terms (why this repo is private)

ESA S2P Space Weather Data Terms and Conditions (read 21 Oct 2026):
- Data may be used and transformed, including in derived products and services, provided the data itself is not sold,
  licensed or redistributed for commercial gain (3.1).
- Free datasets may be redistributed only to third parties who accept the same terms (3.2), so the raw grids stay here.
- Derived work must state: "Data provided by the European Space Agency (ESA) as part of its Space Safety Programme (S2P)"
  and attribute "© ESA (year of reception)" (3.3, 4.3).
- Terms: https://swe.ssa.esa.int/documents/d/guest/s2p_swe_data_terms_and_conditions
