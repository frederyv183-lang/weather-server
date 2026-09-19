from data.tropopause_data import fetch_pressure_level_data
from analysis.tropopause import analyze_day
raw = fetch_pressure_level_data(55.41, 37.9, "2026-09-19")
result = analyze_day(raw, 55.41, 37.9)
h12 = result["hours"][12]
print("has_fold:", h12["has_fold"])
print("max_pv:", h12["max_pv"])
print("profile:")
for p in h12.get("profile", []):
    print(f"  {p['level']} гПа: PV={p.get('pv_pvu')}")