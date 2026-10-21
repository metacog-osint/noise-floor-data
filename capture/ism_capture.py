#!/usr/bin/env python3
"""Capture the ESA SWE / CLS ISM worldwide ionospheric nowcast (S4, sigma-phi, TEC) once per valid hour.

ESA publishes only the current nowcast; there is no archive, so this job builds one.
Output (one file per valid hour, skipped if already captured):
  ism/YYYY/MM/ism_YYYYMMDDTHHZ.csv.gz  columns: s4, s4_err, sigma_phi, sigma_phi_err, tec, tec_err
  Integers: S4 and sigma-phi (rad) x 1000, their errors x 100; TEC and its error in whole TECU. Rows follow ism/grid.csv
  (lon, lat; 2.5 deg; 145 x 71 = 10,295 cells).
  ism/summary.csv  one row per valid hour: per-region max S4 and sigma-phi, global max, ICAO GNSS
  exceedance counts (S4 >= 0.5 / 0.8, sigma-phi >= 0.4 / 0.7 rad).
Stdlib only. Usage: python capture/ism_capture.py [REPO_ROOT]
Data: (c) ESA. "Data provided by the European Space Agency (ESA) as part of its Space Safety Programme (S2P)".
"""
import gzip, os, re, sys, urllib.request, datetime as dt

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://swe.ssa.esa.int/assets/ism/ism_nowcast/"
PRODUCTS = [("s4", 1000, 100), ("sigma_phi", 1000, 100), ("tec", 1, 1)]  # (name, value scale, error scale)
REGIONS = {"centcom": (12, 42, 30, 65), "eucom": (35, 72, -25, 45), "africom": (-35, 35, -20, 50),
           "indopacom": (-10, 45, 95, 150), "northcom": (15, 50, -125, -65), "southcom": (-56, 15, -95, -30)}
REC = re.compile(r"<ns2:date>([^<]+)</ns2:date><ns2:stringValue>([^<]+)</ns2:stringValue><ns2:stringValue>([^<]+)"
                 r"</ns2:stringValue><ns2:stringValue>([^<]+)</ns2:stringValue><ns2:stringValue>([^<]+)</ns2:stringValue>")


def fetch(name):
    req = urllib.request.Request(BASE + f"{name}_nowcast_grid.xml", headers={"User-Agent": "noise-floor-data/1.0"})
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=120).read().decode("utf-8")
        except Exception as e:
            err = e
    raise SystemExit(f"fetch {name} failed: {err}")


def main():
    grids, times, cells = {}, set(), None
    for name, _, _ in PRODUCTS:
        recs = REC.findall(fetch(name))
        if len(recs) < 10000:
            raise SystemExit(f"{name}: only {len(recs)} cells")
        times |= {r[0] for r in recs}
        ll = [(r[1], r[2]) for r in recs]
        if cells is None: cells = ll
        elif ll != cells: raise SystemExit(f"{name}: grid order differs")
        grids[name] = [(float(r[3]), float(r[4])) for r in recs]
    if len(times) != 1:
        print("mixed valid times across products:", sorted(times)); 
    vt = dt.datetime.strptime(min(times)[:19], "%Y-%m-%dT%H:%M:%S")
    os.makedirs(os.path.join(ROOT, "ism"), exist_ok=True)
    gpath = os.path.join(ROOT, "ism", "grid.csv")
    if not os.path.exists(gpath):
        with open(gpath, "w") as f: f.write("lon,lat\n" + "".join(f"{a},{b}\n" for a, b in cells))
    out = os.path.join(ROOT, "ism", f"{vt:%Y}", f"{vt:%m}", f"ism_{vt:%Y%m%dT%H}Z.csv.gz")
    if os.path.exists(out):
        print("already captured", vt); return
    os.makedirs(os.path.dirname(out), exist_ok=True)
    lines = ["s4,s4_err,sigma_phi,sigma_phi_err,tec,tec_err"]
    for i in range(len(cells)):
        row = []
        for name, k, ke in PRODUCTS:
            v, e = grids[name][i]; row += [str(int(round(v * k))), str(int(round(e * ke)))]
        lines.append(",".join(row))
    with gzip.open(out, "wt", compresslevel=9) as f: f.write("\n".join(lines) + "\n")
    # summary
    lon = [float(a) for a, _ in cells]; lat = [float(b) for _, b in cells]
    s4 = [v for v, _ in grids["s4"]]; sp = [v for v, _ in grids["sigma_phi"]]
    cols = ["valid_utc", "captured_utc", "global_max_s4", "global_max_sigma_phi",
            "n_s4_mod", "n_s4_sev", "n_sp_mod", "n_sp_sev"] + [f"{r}_max_{p}" for r in REGIONS for p in ("s4", "sigma_phi")]
    vals = [f"{vt:%Y-%m-%dT%H:%MZ}", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            f"{max(s4):.3f}", f"{max(sp):.3f}", sum(v >= 0.5 for v in s4), sum(v >= 0.8 for v in s4),
            sum(v >= 0.4 for v in sp), sum(v >= 0.7 for v in sp)]
    for r, (a, b, c, d) in REGIONS.items():
        idx = [i for i in range(len(cells)) if a <= lat[i] <= b and c <= lon[i] <= d]
        vals += [f"{max(s4[i] for i in idx):.3f}", f"{max(sp[i] for i in idx):.3f}"]
    spath = os.path.join(ROOT, "ism", "summary.csv")
    new = not os.path.exists(spath)
    with open(spath, "a") as f:
        if new: f.write(",".join(cols) + "\n")
        f.write(",".join(str(v) for v in vals) + "\n")
    print("captured", vt, os.path.getsize(out), "bytes; global max S4", vals[2], "sigma-phi", vals[3])


if __name__ == "__main__":
    main()
