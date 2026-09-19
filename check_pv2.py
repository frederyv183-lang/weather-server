from data.tropopause_data import fetch_pressure_level_data
from analysis.tropopause import compute_epv_profile

# Принудительно новый запрос — обходим кэш
raw = fetch_pressure_level_data(55.41, 37.9, "2026-09-18")  # вчерашняя дата
result = compute_epv_profile(raw, 55.41, 37.9, 12)

print("tropopause_level:", result["tropopause_level_hPa"])
for p in result["profile"]:
    print(f"  {p['level']} гПа: T={p['temp_c']} θ={p['theta_k']} PV={p.get('pv_pvu')}")