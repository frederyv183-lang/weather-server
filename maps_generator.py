# -*- coding: utf-8 -*-
"""
Генерация погодных карт для интерактивного просмотра (Leaflet).

Источники:
  - ICON-EU (DWD) — opendata.dwd.de, GRIB2 + bz2
  - GFS (NOAA)    — через herbie-data

Что делает:
  - Скачивает поля: pmsl, t_2m, u_10m, v_10m, tot_prec, clct
  - Обрезает данные под регион ЕТР (lon 20–60, lat 40–70)
  - Рисует прозрачные PNG-слои
  - Сохраняет в архив: static/maps/archive/YYYY/MM/DD/
  - Дублирует последний прогон в static/maps/ (для Leaflet)
  - Температура: заливка (шаг 2 °C) + изотермы (шаг 4 °C) + colorbar
  - Осадки: накопление за 6 часов
  - Pmsl: жирные изогипсы
  - Контуры берегов + крупные города + маркер Москвы
  - Шаги: +6, +12, +18, +24 ч

Кроссплатформенность:
  GRIB-файлы кэшируются в системной temp-папке
  (Linux: /tmp, Windows: %TEMP%\\weather_grib_cache).
"""

import os
import bz2
import shutil
import tempfile
import urllib.request
from datetime import datetime, timedelta, timezone

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# ============================================================
# КОНСТАНТЫ
# ============================================================
MAPS_DIR = "static/maps"
ARCHIVE_DIR = os.path.join(MAPS_DIR, "archive")
os.makedirs(MAPS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

CACHE_DIR = os.path.join(tempfile.gettempdir(), "weather_grib_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Регион: Европейская территория России
LON_MIN, LON_MAX = 20, 60
LAT_MIN, LAT_MAX = 40, 70

# Москва — маркер на карте
MOSCOW_LAT, MOSCOW_LON = 55.7558, 37.6173

# Крупные города
CITIES = [
    ("Москва",          55.7558, 37.6173),
    ("Санкт-Петербург", 59.9343, 30.3351),
    ("Калининград",     54.7104, 20.4522),
    ("Нижний Новгород", 56.2965, 43.9361),
    ("Казань",          55.8304, 49.0661),
    ("Самара",          53.1959, 50.1002),
    ("Волгоград",       48.7080, 44.5133),
    ("Ростов-на-Дону",  47.2225, 39.7188),
    ("Уфа",             54.7388, 55.9721),
    ("Пермь",           58.0105, 56.2502),
    ("Воронеж",         51.6720, 39.1843),
    ("Краснодар",       45.0355, 38.9753),
    ("Минск",           53.9025, 27.5619),
    ("Киев",            50.4501, 30.5234),
    ("Харьков",         49.9935, 36.2304),
    ("Одесса",          46.4825, 30.7233),
    ("Хельсинки",       60.1699, 24.9384),
    ("Таллин",          59.4370, 24.7536),
    ("Рига",            56.9496, 24.1052),
    ("Вильнюс",         54.6872, 25.2797),
    ("Варшава",         52.2297, 21.0122),
    ("Бухарест",        44.4268, 26.1025),
    ("Стамбул",         41.0082, 28.9784),
    ("Анкара",          39.9334, 32.8597),
    ("Баку",            40.4093, 49.8671),
    ("Тбилиси",         41.7151, 44.8271),
    ("Ереван",          40.1792, 44.4991),
]

# ICON-EU
ICON_BASE = "https://opendata.dwd.de/weather/nwp/icon-eu/grib"

# GFS (Herbie)
GFS_PRODUCT = "pgrb2.0p25"


# ============================================================
# ICON-EU
# ============================================================
def get_icon_run():
    """Ближайший доступный run ICON-EU (00/06/12/18 UTC, с задержкой 2 ч)."""
    now = datetime.now(timezone.utc) - timedelta(hours=2)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def download_icon_field(run, field, step):
    """Скачивает GRIB2-поле ICON-EU с DWD."""
    hh = f"{run.hour:02d}"
    stamp = run.strftime("%Y%m%d") + hh
    step3 = f"{step:03d}"
    fname = (
        f"icon-eu_europe_regular-lat-lon_single-level_"
        f"{stamp}_{step3}_{field.upper()}.grib2"
    )
    url = f"{ICON_BASE}/{hh}/{field}/{fname}.bz2"
    out = os.path.join(CACHE_DIR, fname)

    if not os.path.exists(out):
        with urllib.request.urlopen(url, timeout=60) as r:
            data = bz2.decompress(r.read())
        with open(out, "wb") as f:
            f.write(data)

    return out


def read_icon_field(run, field, step):
    """Читает поле ICON-EU и обрезает по региону ЕТР."""
    path = download_icon_field(run, field, step)
    ds = xr.open_dataset(path, engine="cfgrib")
    var = list(ds.data_vars)[0]

    if float(ds.latitude[0]) > float(ds.latitude[-1]):
        ds = ds.sortby("latitude")

    ds = ds.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX),
    )

    return ds[var].values, ds["latitude"].values, ds["longitude"].values


# ============================================================
# GFS (через Herbie)
# ============================================================
GFS_FIELDS = {
    "t_2m":     "TMP:2 m",
    "pmsl":     "PRMSL:mean sea level",
    "u_10m":    "UGRD:10 m",
    "v_10m":    "VGRD:10 m",
    "tot_prec": "APCP:surface",
    "clct":     "TCDC:entire atmosphere",
}


def get_gfs_run():
    """Ближайший доступный run GFS (00/06/12/18 UTC, с задержкой 3 ч)."""
    now = datetime.now(timezone.utc) - timedelta(hours=3)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def read_gfs_field(run, field, step):
    """Читает поле GFS через Herbie и обрезает по региону ЕТР."""
    from herbie import Herbie

    H = Herbie(
        run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product=GFS_PRODUCT,
        fxx=step,
    )
    ds = H.xarray(GFS_FIELDS[field])
    var = list(ds.data_vars)[0]

    if float(ds.latitude[0]) > float(ds.latitude[-1]):
        ds = ds.sortby("latitude")

    ds = ds.sel(
        latitude=slice(LAT_MIN, LAT_MAX),
        longitude=slice(LON_MIN, LON_MAX),
    )

    return ds[var].values, ds["latitude"].values, ds["longitude"].values


# ============================================================
# КОНТУРЫ БЕРЕГОВ + ГОРОДА
# ============================================================
def draw_coastlines(ax):
    ax.add_feature(
        cfeature.COASTLINE, linewidth=0.4,
        edgecolor="#555555", alpha=0.7, zorder=2,
    )
    ax.add_feature(
        cfeature.BORDERS, linewidth=0.3,
        edgecolor="#888888", alpha=0.4,
        linestyle="--", zorder=2,
    )


def draw_cities(ax):
    for name, lat, lon in CITIES:
        if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
            continue

        is_moscow = (name == "Москва")
        color = "#ff0000" if is_moscow else "#222222"
        size = 6 if is_moscow else 3.5
        fs = 10 if is_moscow else 7

        ax.plot(
            lon, lat, marker="o", markersize=size,
            markerfacecolor=color, markeredgecolor="white",
            markeredgewidth=1.2 if is_moscow else 0.8,
            transform=ccrs.PlateCarree(), zorder=100,
        )
        dx = 0.3 if is_moscow else 0.25
        ax.text(
            lon + dx, lat + 0.15, name,
            transform=ccrs.PlateCarree(),
            fontsize=fs,
            fontweight="bold" if is_moscow else "normal",
            color=color, ha="left", va="bottom", zorder=101,
            path_effects=[pe.withStroke(linewidth=1.8, foreground="white")],
        )


# ============================================================
# ОТРИСОВКА
# ============================================================
def draw_layer(data, lons, lats, layer_type, out_path,
               cmap=None, levels=None, alpha=0.7,
               draw_marker=True,
               draw_isolines=False, isoline_levels=None,
               isoline_color="black", isoline_width=1.0,
               isoline_fontsize=8, isoline_fmt="%d",
               colorbar_label=None,
               draw_cities_flag=True):
    """Рисует один слой как прозрачный PNG."""

    lon_mask = (lons >= LON_MIN) & (lons <= LON_MAX)
    lat_mask = (lats >= LAT_MIN) & (lats <= LAT_MAX)

    lons_c = lons[lon_mask]
    lats_c = lats[lat_mask]

    if layer_type == "quiver":
        u = data[0][np.ix_(lat_mask, lon_mask)]
        v = data[1][np.ix_(lat_mask, lon_mask)]
        data_c = (u, v)
    else:
        data_c = data[np.ix_(lat_mask, lon_mask)]

    fig = plt.figure(figsize=(10, 8), dpi=100)
    fig.patch.set_alpha(0.0)

    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.patch.set_alpha(0.0)
    ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX],
                  crs=ccrs.PlateCarree())

    ax.spines["geo"].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    cf = None
    if layer_type == "contourf":
        cf = ax.contourf(lons_c, lats_c, data_c, levels=levels, cmap=cmap,
                         transform=ccrs.PlateCarree(), extend="both",
                         alpha=alpha)

        if draw_isolines and isoline_levels is not None:
            cs_iso = ax.contour(
                lons_c, lats_c, data_c, levels=isoline_levels,
                colors=isoline_color, linewidths=isoline_width,
                transform=ccrs.PlateCarree(), alpha=0.9, zorder=4,
            )
            ax.clabel(cs_iso, inline=True,
                      fontsize=isoline_fontsize,
                      fmt=isoline_fmt, colors=isoline_color)

    elif layer_type == "contour":
        cs = ax.contour(lons_c, lats_c, data_c, levels=levels,
                        colors="black", linewidths=1.8,
                        transform=ccrs.PlateCarree(), zorder=3)
        ax.clabel(cs, inline=True, fontsize=10, fmt="%d", colors="black")

    elif layer_type == "quiver":
        s = 25
        ax.quiver(
            lons_c[::s], lats_c[::s],
            data_c[0][::s, ::s], data_c[1][::s, ::s],
            transform=ccrs.PlateCarree(), scale=400, width=0.002, zorder=4,
        )

    draw_coastlines(ax)

    if draw_cities_flag:
        draw_cities(ax)

    if cf is not None and colorbar_label:
        cbar = fig.colorbar(
            cf, ax=ax, orientation="horizontal",
            pad=0.03, shrink=0.55, aspect=25, fraction=0.03,
        )
        cbar.set_label(colorbar_label, fontsize=9)
        cbar.ax.tick_params(labelsize=8)
        cbar.outline.set_edgecolor("black")
        cbar.outline.set_linewidth(0.5)

    ax.set_axis_off()
    plt.savefig(out_path, transparent=True,
                pad_inches=0, facecolor="none")
    plt.close(fig)


# ============================================================
# СОХРАНЕНИЕ: АРХИВ + КОРЕНЬ
# ============================================================
def _save_layer_both(data, lons, lats, layer_type, model, stamp, step, field,
                     **draw_kwargs):
    """
    Сохраняет слой в архив + дублирует в корень static/maps/.
    Возвращает (archive_path, root_path).
    """
    # Архив: static/maps/archive/YYYY/MM/DD/
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]
    archive_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    os.makedirs(archive_dir, exist_ok=True)

    archive_path = os.path.join(
        archive_dir, f"{model}_{stamp}_{step:03d}_{field}.png"
    )
    root_path = os.path.join(
        MAPS_DIR, f"{model}_{stamp}_{step:03d}_{field}.png"
    )

    draw_layer(data, lons, lats, layer_type, archive_path, **draw_kwargs)
    shutil.copy2(archive_path, root_path)

    return archive_path, root_path


# ============================================================
# ОСАДКИ: РАЗНОСТЬ МЕЖДУ ШАГАМИ
# ============================================================
def read_precip_per_step(run, step):
    """Осадки за 6 часов (step-6 .. step)."""
    if step <= 6:
        d, lats, lons = read_icon_field(run, "tot_prec", step)
        return d, lats, lons

    d_now, lats, lons = read_icon_field(run, "tot_prec", step)
    d_prev, _, _ = read_icon_field(run, "tot_prec", step - 6)
    return d_now - d_prev, lats, lons


def read_precip_per_step_gfs(run, step):
    """Осадки за 6 часов для GFS."""
    if step <= 6:
        d, lats, lons = read_gfs_field(run, "tot_prec", step)
        return d, lats, lons

    d_now, lats, lons = read_gfs_field(run, "tot_prec", step)
    d_prev, _, _ = read_gfs_field(run, "tot_prec", step - 6)
    return d_now - d_prev, lats, lons


# ============================================================
# ГЕНЕРАЦИЯ
# ============================================================
def generate_all_layers(models, steps, fields):
    """Генерирует все PNG-слои, сохраняет в архив + корень."""
    results = []

    T_LEVELS_FILL = np.arange(-30, 46, 2)
    T_LEVELS_ISO = np.arange(-30, 46, 4)

    for model in models:
        if model == "icon-eu":
            run = get_icon_run()
            stamp = run.strftime("%Y%m%d") + f"{run.hour:02d}"

            for step in steps:
                if "t_2m" in fields:
                    d, lats, lons = read_icon_field(run, "t_2m", step)
                    _, root = _save_layer_both(
                        d - 273.15, lons, lats, "contourf",
                        model, stamp, step, "t2m",
                        cmap="RdYlBu_r", levels=T_LEVELS_FILL, alpha=0.75,
                        draw_isolines=True, isoline_levels=T_LEVELS_ISO,
                        isoline_color="black", isoline_width=0.8,
                        isoline_fontsize=8, isoline_fmt="%d",
                        colorbar_label="Температура 2м, °C",
                    )
                    results.append(root)

                if "pmsl" in fields:
                    d, lats, lons = read_icon_field(run, "pmsl", step)
                    _, root = _save_layer_both(
                        d / 100, lons, lats, "contour",
                        model, stamp, step, "pmsl",
                        levels=np.arange(960, 1040, 4),
                    )
                    results.append(root)

                if "u_10m" in fields and "v_10m" in fields:
                    u, lats, lons = read_icon_field(run, "u_10m", step)
                    v, _, _ = read_icon_field(run, "v_10m", step)
                    _, root = _save_layer_both(
                        (u, v), lons, lats, "quiver",
                        model, stamp, step, "wind",
                    )
                    results.append(root)

                if "tot_prec" in fields:
                    d, lats, lons = read_precip_per_step(run, step)
                    _, root = _save_layer_both(
                        d, lons, lats, "contourf",
                        model, stamp, step, "prec",
                        cmap="Blues", levels=np.arange(0, 20, 1),
                        alpha=0.75, colorbar_label="Осадки за 6 ч, мм",
                    )
                    results.append(root)

                if "clct" in fields:
                    d, lats, lons = read_icon_field(run, "clct", step)
                    _, root = _save_layer_both(
                        d, lons, lats, "contourf",
                        model, stamp, step, "clct",
                        cmap="Greys", levels=np.arange(0, 100, 10),
                        alpha=0.6, colorbar_label="Облачность, %",
                    )
                    results.append(root)

        elif model == "gfs":
            run = get_gfs_run()
            stamp = run.strftime("%Y%m%d") + f"{run.hour:02d}"

            for step in steps:
                if "t_2m" in fields:
                    d, lats, lons = read_gfs_field(run, "t_2m", step)
                    _, root = _save_layer_both(
                        d - 273.15, lons, lats, "contourf",
                        model, stamp, step, "t2m",
                        cmap="RdYlBu_r", levels=T_LEVELS_FILL, alpha=0.75,
                        draw_isolines=True, isoline_levels=T_LEVELS_ISO,
                        isoline_color="black", isoline_width=0.8,
                        isoline_fontsize=8, isoline_fmt="%d",
                        colorbar_label="Температура 2м, °C",
                    )
                    results.append(root)

                if "pmsl" in fields:
                    d, lats, lons = read_gfs_field(run, "pmsl", step)
                    _, root = _save_layer_both(
                        d / 100, lons, lats, "contour",
                        model, stamp, step, "pmsl",
                        levels=np.arange(960, 1040, 4),
                    )
                    results.append(root)

                if "u_10m" in fields and "v_10m" in fields:
                    u, lats, lons = read_gfs_field(run, "u_10m", step)
                    v, _, _ = read_gfs_field(run, "v_10m", step)
                    _, root = _save_layer_both(
                        (u, v), lons, lats, "quiver",
                        model, stamp, step, "wind",
                    )
                    results.append(root)

                if "tot_prec" in fields:
                    d, lats, lons = read_precip_per_step_gfs(run, step)
                    _, root = _save_layer_both(
                        d, lons, lats, "contourf",
                        model, stamp, step, "prec",
                        cmap="Blues", levels=np.arange(0, 20, 1),
                        alpha=0.75, colorbar_label="Осадки за 6 ч, мм",
                    )
                    results.append(root)

                if "clct" in fields:
                    d, lats, lons = read_gfs_field(run, "clct", step)
                    _, root = _save_layer_both(
                        d, lons, lats, "contourf",
                        model, stamp, step, "clct",
                        cmap="Greys", levels=np.arange(0, 100, 10),
                        alpha=0.6, colorbar_label="Облачность, %",
                    )
                    results.append(root)

    return results


# ============================================================
# МЕТАДАННЫЕ
# ============================================================
def get_meta():
    return {
        "bounds": [[LAT_MIN, LON_MIN], [LAT_MAX, LON_MAX]],
        "models": ["icon-eu", "gfs"],
        "steps": [6, 12, 18, 24],
        "fields": ["t_2m", "pmsl", "wind", "prec", "clct"],
        "moscow": [MOSCOW_LAT, MOSCOW_LON],
    }