from data.tropopause_data import fetch_pressure_level_data
from analysis.tropopause import compute_epv_profile
from core.config import TROPOPAUSE_LEVELS

print("TROPOPAUSE_LEVELS =", TROPOPAUSE_LEVELS)

raw = fetch_pressure_level_data(55.41, 37.9, "2026-09-19")
h = raw.get("hourly", {})

print("\n--- ключи в hourly ---")
for k in sorted(h.keys()):
    if k != "time":
        v = h[k]
        idx9 = v[9] if len(v) > 9 else None
        print(f"  {k}: len={len(v)}, [9]={idx9}")

print("\n--- результат compute_epv_profile для часа 9 ---")
result = compute_epv_profile(raw, 55.41, 37.9, 9)
print("tropopause_level_hPa =", result["tropopause_level_hPa"])
print("\nПрофиль:")
for p in result["profile"]:
    print(f"  {p['level']} гПа: T={p['temp_c']} θ={p['theta_k']} PV={p.get('pv_pvu')} is_strat={p.get('is_stratosphere')}")