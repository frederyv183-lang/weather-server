# -*- coding: utf-8 -*-
"""
Генерация глобальных карт абсолютной топографии (АТ) через NOAA GFS.

Использует herbie-data для скачивания GRIB-файлов GFS и Cartopy
для отрисовки изогипс на карте Robinson.
"""

import os
import traceback
from datetime import datetime, timedelta, timezone

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from synoptic_maps.config import AT_LEVELS, REGIONS


OUTPUT_DIR = "static/synoptic_maps"
ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "archive")


def get_latest_gfs_run():
    """Ближайший доступный прогон GFS (задержка ~5 часов)."""
    now = datetime.now(timezone.utc) - timedelta(hours=5)
    hour = (now.hour // 6) * 6
    return now.replace(hour=hour, minute=0, second=0, microsecond=0)


def read_gh_field(run, level_hpa, step_h, region_bbox):
    """
    Читает поле HGT (geopotential height) из GFS GRIB.
    Возвращает (lons, lats, gh_2d).
    """
    from herbie import Herbie

    H = Herbie(
        run.strftime("%Y-%m-%d %H:%M"),
        model="gfs",
        product="pgrb2.0p25",
        fxx=step_h,
    )

    # Скачиваем только HGT на нужном уровне (маленький сабсет)
    ds = H.xarray(f"HGT:{level_hpa} mb")
    if isinstance(ds, list):
        ds = ds[0]

    var = list(ds.data_vars)[0]
    lats = ds.latitude.values
    lons = ds.longitude.values

    # Приводим долготы к -180..180
    if lons.max() > 180:
        lons = np.where(lons > 180, lons - 360, lons)
        order = np.argsort(lons)
        lons = lons[order]
        ds = ds.isel(longitude=order)

    if lats[0] > lats[-1]:
        lats = lats[::-1]
        ds = ds.isel(latitude=slice(None, None, -1))

    lon_min, lon_max, lat_min, lat_max = region_bbox
    mask_lon = (lons >= lon_min) & (lons <= lon_max)
    mask_lat = (lats >= lat_min) & (lats <= lat_max)

    lons_c = lons[mask_lon]
    lats_c = lats[mask_lat]
    gh_2d = ds[var].values[np.ix_(mask_lat, mask_lon)]

    return lons_c, lats_c, gh_2d


def draw_at_map(lons, lats, gh_2d, level_hpa, step_h, run,
                output_path, region_bbox):
    """Рисует карту АТ и сохраняет в output_path."""
    level_info = AT_LEVELS[level_hpa]
    gh_min, gh_max = level_info["range"]
    step = level_info["step"]

    # Определяем проекцию по региону
    if region_bbox == (-180, 180, -90, 90):
        proj = ccrs.Robinson()
    elif region_bbox[1] - region_bbox[0] > 180:
        proj = ccrs.Robinson()
    else:
        proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(16, 10), dpi=100)
    ax = plt.axes(projection=proj)

    if isinstance(proj, ccrs.Robinson):
        ax.set_global()
    else:
        ax.set_extent(region_bbox, crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.COASTLINE, linewidth=0.5,
                   edgecolor="#555555", zorder=3)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3,
                   edgecolor="#888888", linestyle="--",
                   alpha=0.5, zorder=3)
    ax.add_feature(cfeature.LAND, facecolor="#f5f5dc", alpha=0.3, zorder=1)

    levels = np.arange(gh_min, gh_max + step, step)
    cs = ax.contour(lons, lats, gh_2d, levels=levels,
                    colors="black", linewidths=1.2,
                    transform=ccrs.PlateCarree(), zorder=4)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%d")

    run_str = run.strftime("%d.%m.%Y %H:%M UTC")
    title = f"АТ-{level_hpa} гПа · +{step_h} ч · GFS · {run_str}"
    ax.set_title(title, fontsize=14, pad=10, fontweight="bold")

    plt.savefig(output_path, bbox_inches="tight", dpi=100,
                facecolor="white")
    plt.close(fig)


def generate_at_maps(levels=(500,), steps=(0, 24),
                     regions=("nh",)):
    """Генерирует карты для всех комбинаций level × step × region."""
    run = get_latest_gfs_run()
    stamp = run.strftime("%Y%m%d%H")
    year, month, day = stamp[:4], stamp[4:6], stamp[6:8]

    out_dir = os.path.join(ARCHIVE_DIR, year, month, day)
    os.makedirs(out_dir, exist_ok=True)

    results = []
    for region_key in regions:
        bbox = REGIONS[region_key]["bbox"]
        for level in levels:
            for step in steps:
                try:
                    lons, lats, gh = read_gh_field(run, level, step, bbox)
                    fname = (f"gfs_{stamp}_{step:03d}"
                             f"_at{level}_{region_key}.png")
                    out_path = os.path.join(out_dir, fname)
                    draw_at_map(lons, lats, gh, level, step, run,
                                out_path, bbox)
                    results.append(out_path)
                    print(f"[synoptic_maps] ✓ {out_path}", flush=True)
                except Exception as e:
                    print(f"[synoptic_maps] ✗ level={level} "
                          f"step={step} region={region_key}: {e}",
                          flush=True)
                    traceback.print_exc()

    return results
