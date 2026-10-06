# -*- coding: utf-8 -*-
"""Генерация карт АТ/PMSL с изогипсами, изотермами, изотахами и городами."""

import os
from synoptic_maps.storage import get_archive_dir
import time
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from synoptic_maps.config import AT_LEVELS, REGIONS, CITIES


OUTPUT_DIR = "static/synoptic_maps"
ARCHIVE_DIR = get_archive_dir()

ARCHIVE_RETENTION_DAYS = 3
DOWNLOAD_TIMEOUT = 180
DOWNLOAD_RETRIES = 2
DOWNLOAD_RETRY_DELAY = 5


def get_latest_gfs_run():
    now = datetime.now(timezone.utc) - timedelta(hours=5)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)



# Патч сессии Herbie — увеличенный timeout (v3)
def _make_herbie(run, step_h, priority=None, model="gfs", **kwargs):
    """Создаёт Herbie с увеличенным timeout (180 сек)."""
    import requests
    from herbie import Herbie

    if priority is None:
        priority = ["nomads", "aws"]

    H = Herbie(
            run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product="pgrb2.0p25",
        fxx=step_h,
        priority=priority,
        verbose=False,
    )
    # Патчим сессию: увеличиваем timeout
    try:
        if hasattr(H, "session") and H.session is not None:
            original = H.session.get
            H.session.get = lambda url, **kw: original(
                url, **{**kw, "timeout": 180}
            )
    except Exception:
        pass
    return H

def read_grib_field(run, level, step_h, region_bbox):
    """
    Читает HGT, TMP, UGRD, VGRD для изобарического уровня.
    Для level="pmsl" — читает PRMSL и TMP:2 m.

    Возвращает dict:
        lons, lats,
        hgt (2D) — изогипсы (м) или изобары (гПа для PMSL),
        tmp (2D) — температура (°C) или None,
        wspd (2D) — скорость ветра (м/с) или None,
    """
    from herbie import Herbie

    is_pmsl = (level == "pmsl")

    H = Herbie(
            run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product="pgrb2.0p25",
        fxx=step_h,
        priority=["nomads", "aws"],
        verbose=False,
    )

    if is_pmsl:
        search = "PRMSL:mean sea level|TMP:2 m|UGRD:10 m|VGRD:10 m"
    else:
        search = (f"HGT:{level} mb|TMP:{level} mb|"
                  f"UGRD:{level} mb|VGRD:{level} mb")

    ds = None
    last_err = None
    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            ds = H.xarray(
                search,
                remove_grib=False,
            )
            break
        except Exception as e:
            last_err = e
            print(f"[synoptic_maps] Попытка {attempt}/{DOWNLOAD_RETRIES} "
                  f"не удалась: {e}", flush=True)
            if attempt < DOWNLOAD_RETRIES:
                time.sleep(DOWNLOAD_RETRY_DELAY)

    if ds is None:
        raise RuntimeError(
            f"Скачивание не удалось после {DOWNLOAD_RETRIES} попыток: {last_err}"
        )

    if isinstance(ds, list):
        ds = xr.merge(ds, compat="override")

    # --- Координаты ---
    lons = ds.longitude.values
    if lons.max() > 180:
        lons = np.where(lons > 180, lons - 360, lons)
        order = np.argsort(lons)
        lons = lons[order]
        ds = ds.isel(longitude=order)

    lats = ds.latitude.values
    if lats[0] > lats[-1]:
        lats = lats[::-1]
        ds = ds.isel(latitude=slice(None, None, -1))

    lon_min, lon_max, lat_min, lat_max = region_bbox
    mask_lon = (lons >= lon_min) & (lons <= lon_max)
    mask_lat = (lats >= lat_min) & (lats <= lat_max)
    lons_c = lons[mask_lon]
    lats_c = lats[mask_lat]

    def _get(*candidates):
        for name in candidates:
            if name in ds.data_vars:
                return ds[name].values[np.ix_(mask_lat, mask_lon)]
        for name in ds.data_vars:
            for c in candidates:
                if c.lower() in name.lower():
                    return ds[name].values[np.ix_(mask_lat, mask_lon)]
        return None

    if is_pmsl:
        hgt = _get("prmsl", "msl", "mslp")
        if hgt is not None:
            hgt = hgt / 100.0  # Pa → гПа
        tmp = _get("t2m", "t")
        if tmp is not None:
            if float(np.nanmean(tmp)) > 100:
                tmp = tmp - 273.15
        u = _get("u10", "u")
        v = _get("v10", "v")
    else:
        hgt = _get("gh", "hgt")
        tmp = _get("t", "tmp")
        if tmp is not None:
            if float(np.nanmean(tmp)) > 100:
                tmp = tmp - 273.15
        u = _get("u", "ugrd")
        v = _get("v", "vgrd")

    if hgt is None:
        hgt = ds[list(ds.data_vars)[0]].values[np.ix_(mask_lat, mask_lon)]

    wspd = None
    if u is not None and v is not None:
        wspd = np.hypot(u, v)

    return {
        "lons": lons_c,
        "lats": lats_c,
        "hgt": hgt,
        "tmp": tmp,
        "wspd": wspd,
    }


def _fmt_valid_time(run, step_h):
    return (run + timedelta(hours=step_h)).strftime("%d.%m.%Y %H:%M UTC")



def read_ot_field(run, step_h, region_bbox):
    """Читает HGT 500/1000, TMP 850, UGRD/VGRD 700 и вычисляет ОТ."""
    from herbie import Herbie

    H = _make_herbie(run, step_h, priority=["aws", "nomads"])

    search = (
        "HGT:500 mb|HGT:1000 mb|"
        "TMP:850 mb|UGRD:700 mb|VGRD:700 mb"
    )

    ds = H.xarray(search, remove_grib=False)
    if isinstance(ds, list):
        ds = xr.merge(ds, compat="override")

    # Координаты
    lons = ds.longitude.values
    if lons.max() > 180:
        lons = np.where(lons > 180, lons - 360, lons)
        order = np.argsort(lons)
        lons = lons[order]
        ds = ds.isel(longitude=order)

    lats = ds.latitude.values
    if lats[0] > lats[-1]:
        lats = lats[::-1]
        ds = ds.isel(latitude=slice(None, None, -1))

    # Обрезка по региону
    lon_min, lon_max, lat_min, lat_max = region_bbox
    mask_lon = (lons >= lon_min) & (lons <= lon_max)
    mask_lat = (lats >= lat_min) & (lats <= lat_max)
    lons_c = lons[mask_lon]
    lats_c = lats[mask_lat]

    def _at_level(var_candidates, lvl):
        """Возвращает 2D-массив для указанного уровня."""
        # Вариант 1: переменная с координатой isobaricInhPa
        for name in ds.data_vars:
            for c in var_candidates:
                if c.lower() in name.lower():
                    d = ds[name]
                    if "isobaricInhPa" in d.dims:
                        try:
                            sub = d.sel(isobaricInhPa=lvl)
                            return sub.values[np.ix_(mask_lat, mask_lon)]
                        except (KeyError, ValueError):
                            continue
        # Вариант 2: переменная — 2D-массив без уровня
        for name in ds.data_vars:
            for c in var_candidates:
                if c.lower() in name.lower():
                    d = ds[name]
                    if (len(d.dims) == 2
                            and "latitude" in d.dims
                            and "longitude" in d.dims):
                        return d.values[np.ix_(mask_lat, mask_lon)]
        return None

    h500 = _at_level(["gh", "hgt"], 500)
    h1000 = _at_level(["gh", "hgt"], 1000)

    if h500 is None or h1000 is None:
        raise RuntimeError(
            f"Не удалось извлечь HGT: h500={h500 is not None}, "
            f"h1000={h1000 is not None}. Переменные: {list(ds.data_vars)}"
        )

    # ОТ в гпдам
    ot = (h500 - h1000) / 10.0

    # Температура и ветер
    tmp = _at_level(["t", "tmp"], 850)
    if tmp is not None:
        if float(np.nanmean(tmp)) > 100:
            tmp = tmp - 273.15

    u = _at_level(["u", "ugrd"], 700)
    v = _at_level(["v", "vgrd"], 700)
    wspd = None
    if u is not None and v is not None:
        wspd = np.hypot(u, v)

    return {
        "lons": lons_c,
        "lats": lats_c,
        "hgt": ot,
        "tmp": tmp,
        "wspd": wspd,
    }



def draw_ot_map(field, step_h, run, output_path, region_bbox,
                show_isohypse=True, show_isotherm=True, show_isotach=True):
    """Рисует карту ОТ 500/1000 с изолиниями, изотермами, изотахами, городами."""
    from synoptic_maps.config import OT, CITIES

    lons, lats = field["lons"], field["lats"]

    if region_bbox == (-180, 180, -90, 90) or (region_bbox[1] - region_bbox[0] > 180):
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(16, 11), dpi=110)
    ax = plt.axes(projection=proj)
    if isinstance(proj, ccrs.Robinson):
        ax.set_global()
    else:
        ax.set_extent(region_bbox, crs=ccrs.PlateCarree())

    ax.set_facecolor("#f7f7f2")

    # === Изолинии ОТ с заливкой ===
    if show_isohypse:
        lo, hi = OT["range"]
        step = OT["step"]
        levels_ot = np.arange(lo, hi + step, step)

        cf = ax.contourf(
            lons, lats, field["hgt"], levels=levels_ot,
            cmap="RdYlBu_r", alpha=0.35,
            transform=ccrs.PlateCarree(), extend="both", zorder=2,
        )
        cbar = fig.colorbar(cf, ax=ax, orientation="horizontal",
                            pad=0.04, shrink=0.55)
        cbar.set_label("ОТ 500/1000, гпдам", fontsize=10)

        cs_ot = ax.contour(
            lons, lats, field["hgt"], levels=levels_ot,
            colors="black", linewidths=1.2,
            transform=ccrs.PlateCarree(), zorder=4,
        )
        ax.clabel(cs_ot, inline=True, fontsize=8, fmt="%d")

    # === Изотермы 850 гПа ===
    if show_isotherm and field["tmp"] is not None:
        t_lo, t_hi, t_step = OT["t_levels"]
        cs_t = ax.contour(
            lons, lats, field["tmp"],
            levels=np.arange(t_lo, t_hi + t_step, t_step),
            colors="#cc0000", linewidths=0.7,
            linestyles="dashed",
            transform=ccrs.PlateCarree(), zorder=5,
        )
        ax.clabel(cs_t, inline=True, fontsize=7, fmt="%d",
                  colors="#cc0000")

    # === Изотахи 700 гПа ===
    if show_isotach and field["wspd"] is not None:
        cs_w = ax.contour(
            lons, lats, field["wspd"],
            levels=[10, 20, 30, 40, 50],
            colors="#0066cc", linewidths=0.8,
            linestyles="dotted",
            transform=ccrs.PlateCarree(), zorder=6,
        )
        ax.clabel(cs_w, inline=True, fontsize=7, fmt="%d",
                  colors="#0066cc")

    # === География ===
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6,
                   edgecolor="#333333", zorder=7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4,
                   edgecolor="#888888", linestyle=":",
                   alpha=0.7, zorder=7)

    # === Города ===
    lon_min, lon_max, lat_min, lat_max = region_bbox
    for name, lat, lon in CITIES:
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            continue
        is_moscow = (name == "Москва")
        is_capital = name in ("Москва", "Санкт-Петербург", "Киев",
                              "Минск", "Лондон", "Париж", "Берлин",
                              "Варшава")
        size = 5 if is_moscow else (3.5 if is_capital else 2.5)
        color = "#cc0000" if is_moscow else "#111111"
        fs = 9 if is_moscow else (7 if is_capital else 6)
        ax.plot(lon, lat, marker="o", markersize=size,
                markerfacecolor=color, markeredgecolor="white",
                markeredgewidth=0.7,
                transform=ccrs.PlateCarree(), zorder=8)
        ax.text(lon + 0.25, lat + 0.15, name,
                transform=ccrs.PlateCarree(),
                fontsize=fs,
                fontweight="bold" if is_moscow else "normal",
                color=color, ha="left", va="bottom", zorder=9,
                path_effects=[pe.withStroke(linewidth=1.8,
                                            foreground="white")])

    # === Заголовок ===
    title = f"ОТ 500/1000 · +{step_h} ч · GFS"
    ax.set_title(title, fontsize=16, pad=12, fontweight="bold")

    # === Таймкод ===
    valid_str = _fmt_valid_time(run, step_h)
    run_str = run.strftime("%d.%m.%Y %H:%M UTC")
    ax.text(
        0.99, 0.01,
        f"Прогноз на: {valid_str}\nЗапуск: {run_str}",
        transform=ax.transAxes,
        fontsize=10, fontfamily="monospace",
        ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.4",
                  facecolor="white", edgecolor="#333333", alpha=0.9),
        zorder=10,
    )

    plt.savefig(output_path, bbox_inches="tight", dpi=110,
                facecolor="white")
    plt.close(fig)


def draw_map(field, level, step_h, run, output_path, region_bbox,
             show_isohypse=True, show_isotherm=True, show_isotach=True):
    """Рисует карту АТ/PMSL с изогипсами, изотермами, изотахами, городами."""
    lons, lats = field["lons"], field["lats"]
    level_info = AT_LEVELS[level]
    is_pmsl = level_info.get("is_pmsl", False)

    # Проекция
    if region_bbox == (-180, 180, -90, 90) or (region_bbox[1] - region_bbox[0] > 180):
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(16, 11), dpi=110)
    ax = plt.axes(projection=proj)
    if isinstance(proj, ccrs.Robinson):
        ax.set_global()
    else:
        ax.set_extent(region_bbox, crs=ccrs.PlateCarree())

    # Фон — светлый
    ax.set_facecolor("#f7f7f2")

    # === Изогипсы (HGT) или изобары (PMSL) ===
    if show_isohypse:
        lo, hi = level_info["range"]
        step = level_info["step"]
        levels_h = np.arange(lo, hi + step, step)
        cs_h = ax.contour(
            lons, lats, field["hgt"], levels=levels_h,
            colors="black", linewidths=1.3,
            transform=ccrs.PlateCarree(), zorder=4,
        )
        ax.clabel(cs_h, inline=True, fontsize=9, fmt="%d")

    # === Изотермы ===
    if show_isotherm and field["tmp"] is not None and level_info.get("t_levels"):
        t_lo, t_hi, t_step = level_info["t_levels"]
        cs_t = ax.contour(
            lons, lats, field["tmp"],
            levels=np.arange(t_lo, t_hi + t_step, t_step),
            colors="#cc0000", linewidths=0.8,
            linestyles="dashed",
            transform=ccrs.PlateCarree(), zorder=5,
        )
        ax.clabel(cs_t, inline=True, fontsize=8, fmt="%d",
                  colors="#cc0000")

    # === Изотахи (скорость ветра) ===
    if show_isotach and field["wspd"] is not None:
        # Пороги изотах — динамические, зависят от уровня
        if is_pmsl:
            isotach_levels = [5, 10, 15, 20]
        else:
            isotach_levels = [10, 20, 30, 40, 50]
        cs_w = ax.contour(
            lons, lats, field["wspd"], levels=isotach_levels,
            colors="#0066cc", linewidths=0.8,
            linestyles="dotted",
            transform=ccrs.PlateCarree(), zorder=6,
        )
        ax.clabel(cs_w, inline=True, fontsize=7, fmt="%d",
                  colors="#0066cc")

    # === География ===
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6,
                   edgecolor="#333333", zorder=7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.4,
                   edgecolor="#888888", linestyle=":",
                   alpha=0.7, zorder=7)
    ax.add_feature(cfeature.LAND, facecolor="#f0efe5",
                   alpha=0.6, zorder=1)

    # === Города ===
    lon_min, lon_max, lat_min, lat_max = region_bbox
    for name, lat, lon in CITIES:
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            continue
        is_moscow = (name == "Москва")
        is_capital = name in ("Москва", "Санкт-Петербург", "Киев",
                              "Минск", "Лондон", "Париж", "Берлин",
                              "Варшава")
        size = 5 if is_moscow else (3.5 if is_capital else 2.5)
        color = "#cc0000" if is_moscow else "#111111"
        fs = 9 if is_moscow else (7 if is_capital else 6)

        ax.plot(lon, lat, marker="o", markersize=size,
                markerfacecolor=color, markeredgecolor="white",
                markeredgewidth=0.7,
                transform=ccrs.PlateCarree(), zorder=8)
        ax.text(lon + 0.25, lat + 0.15, name,
                transform=ccrs.PlateCarree(),
                fontsize=fs,
                fontweight="bold" if is_moscow else "normal",
                color=color, ha="left", va="bottom", zorder=9,
                path_effects=[pe.withStroke(linewidth=1.8,
                                            foreground="white")])

    # === Заголовок ===
    level_name = level_info["name"]
    title = f"{level_name} · +{step_h} ч · GFS"
    ax.set_title(title, fontsize=16, pad=12, fontweight="bold")

    # === Таймкод ===
    valid_str = _fmt_valid_time(run, step_h)
    run_str = run.strftime("%d.%m.%Y %H:%M UTC")
    ax.text(
        0.99, 0.01,
        f"Прогноз на: {valid_str}\nЗапуск: {run_str}",
        transform=ax.transAxes,
        fontsize=10,
        fontfamily="monospace",
        ha="right", va="bottom",
        bbox=dict(boxstyle="round,pad=0.4",
                  facecolor="white", edgecolor="#333333", alpha=0.9),
        zorder=10,
    )

    plt.savefig(output_path, bbox_inches="tight", dpi=110,
                facecolor="white")
    plt.close(fig)


def _overlay_suffix(show_iso, show_iso_t, show_iso_w):
    parts = []
    if show_iso:
        parts.append("h")
    if show_iso_t:
        parts.append("t")
    if show_iso_w:
        parts.append("w")
    return ("_" + "".join(parts)) if parts else "_none"


def generate_maps(levels=None, steps=None, regions=None,
                  show_isohypse=True, show_isotherm=True,
                  show_isotach=True, include_ot=False):
    """Генерирует карты для всех комбинаций level × step × region."""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    if levels is None:
        levels = list(AT_LEVELS.keys())
    if steps is None:
        steps = [0, 12, 24, 48]
    if regions is None:
        regions = ["nh"]

    run = get_latest_gfs_run()
    stamp = run.strftime("%Y%m%d%H")
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]
    out_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    os.makedirs(out_dir, exist_ok=True)

    suffix = _overlay_suffix(show_isohypse, show_isotherm, show_isotach)
    results = []

    for region_key in regions:
        bbox = REGIONS[region_key]["bbox"]
        for level in levels:
            for step in steps:
                try:
                    field = read_grib_field(run, level, step, bbox)
                    fname = (f"gfs_{stamp}_{step:03d}"
                             f"_at{level}_{region_key}{suffix}.png")
                    out_path = os.path.join(out_dir, fname)
                    draw_map(
                        field, level, step, run, out_path, bbox,
                        show_isohypse=show_isohypse,
                        show_isotherm=show_isotherm,
                        show_isotach=show_isotach,
                    )
                    results.append(out_path)
                    print(f"[synoptic_maps] ✓ {out_path}", flush=True)
                except Exception as e:
                    print(f"[synoptic_maps] ✗ level={level} "
                          f"step={step} region={region_key}: {e}",
                          flush=True)
                    traceback.print_exc()


    # --- Относительная топография (ОТ 500/1000) ---
    if include_ot:
        for region_key in regions:
            bbox = REGIONS[region_key]["bbox"]
            for step in steps:
                try:
                    field = read_ot_field(run, step, bbox)
                    fname = (f"gfs_{stamp}_{step:03d}"
                             f"_ot_500_1000_{region_key}{suffix}.png")
                    out_path = os.path.join(out_dir, fname)
                    draw_ot_map(
                        field, step, run, out_path, bbox,
                        show_isohypse=show_isohypse,
                        show_isotherm=show_isotherm,
                        show_isotach=show_isotach,
                    )
                    results.append(out_path)
                    print(f"[synoptic_maps] ✓ ОТ {out_path}",
                          flush=True)
                except Exception as e:
                    print(f"[synoptic_maps] ✗ ОТ step={step} "
                          f"region={region_key}: {e}", flush=True)
                    traceback.print_exc()

    return results


def cleanup_old_archive():

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    import shutil
    if not os.path.isdir(ARCHIVE_DIR):
        return 0
    cutoff = datetime.now() - timedelta(days=ARCHIVE_RETENTION_DAYS)
    removed = 0
    for year in os.listdir(ARCHIVE_DIR):
        ypath = os.path.join(ARCHIVE_DIR, year)
        if not (os.path.isdir(ypath) and year.isdigit()):
            continue
        for month in os.listdir(ypath):
            mpath = os.path.join(ypath, month)
            if not (os.path.isdir(mpath) and month.isdigit()):
                continue
            for day in os.listdir(mpath):
                dpath = os.path.join(mpath, day)
                if not (os.path.isdir(dpath) and day.isdigit()):
                    continue
                try:
                    d = datetime(int(year), int(month), int(day))
                except ValueError:
                    continue
                if d < cutoff:
                    try:
                        shutil.rmtree(dpath)
                        removed += 1
                    except Exception:
                        pass
    return removed
