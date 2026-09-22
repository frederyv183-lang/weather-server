# -*- coding: utf-8 -*-
"""
Планировщик фонового обновления карт.

Запуск (отдельный процесс):
    python scheduler.py

Cron-эквивалент:
    sched.add_job(job, "cron", hour="*/3", minute=20)
    sched.add_job(cleanup, "cron", hour=3, minute=0)
"""

import os
import shutil
from datetime import datetime, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler

from maps_generator import generate_all_layers, ARCHIVE_DIR


# Хранить архив 90 дней
ARCHIVE_RETENTION_DAYS = 90


def job():
    """Генерирует все карты: ICON-EU + GFS, все шаги, все поля."""
    print("[scheduler] Запуск генерации карт...", flush=True)
    try:
        files = generate_all_layers(
            models=["icon-eu", "gfs"],
            steps=[6, 12, 18, 24],
            fields=["t_2m", "pmsl", "u_10m", "v_10m", "tot_prec", "clct"],
        )
        print(f"[scheduler] Готово, файлов: {len(files)}", flush=True)
    except Exception as e:
        print(f"[scheduler] Ошибка генерации: {e}", flush=True)


def cleanup_archive():
    """
    Удаляет архивы старше ARCHIVE_RETENTION_DAYS дней.
    Структура: static/maps/archive/YYYY/MM/DD/
    """
    print("[scheduler] Очистка архива...", flush=True)

    if not os.path.isdir(ARCHIVE_DIR):
        print("[scheduler] Архив пуст", flush=True)
        return

    cutoff = datetime.now() - timedelta(days=ARCHIVE_RETENTION_DAYS)
    removed_days = 0
    removed_dirs = 0

    for year in os.listdir(ARCHIVE_DIR):
        year_path = os.path.join(ARCHIVE_DIR, year)
        if not os.path.isdir(year_path) or not year.isdigit():
            continue

        for month in os.listdir(year_path):
            month_path = os.path.join(year_path, month)
            if not os.path.isdir(month_path) or not month.isdigit():
                continue

            for day in os.listdir(month_path):
                day_path = os.path.join(month_path, day)
                if not os.path.isdir(day_path) or not day.isdigit():
                    continue

                try:
                    d = datetime(int(year), int(month), int(day))
                except ValueError:
                    continue

                if d < cutoff:
                    try:
                        shutil.rmtree(day_path)
                        removed_days += 1
                        print(f"[scheduler]   Удалён: {year}/{month}/{day}",
                              flush=True)
                    except Exception as e:
                        print(f"[scheduler]   Ошибка удаления "
                              f"{year}/{month}/{day}: {e}", flush=True)

            # Удаляем пустые месяцы
            try:
                if not os.listdir(month_path):
                    os.rmdir(month_path)
                    removed_dirs += 1
            except OSError:
                pass

        # Удаляем пустые годы
        try:
            if not os.listdir(year_path):
                os.rmdir(year_path)
                removed_dirs += 1
        except OSError:
            pass

    print(f"[scheduler] Очистка завершена: "
          f"{removed_days} дней, {removed_dirs} пустых папок", flush=True)


if __name__ == "__main__":
    sched = BlockingScheduler(timezone="UTC")

    # Обновление карт каждые 3 часа
    sched.add_job(job, "cron", hour="*/3", minute=20)

    # Очистка архива раз в сутки в 03:00 UTC
    sched.add_job(cleanup_archive, "cron", hour=3, minute=0)

    print(f"[scheduler] Старт. Обновление каждые 3 часа, "
          f"очистка архива раз в сутки (хранить {ARCHIVE_RETENTION_DAYS} дней).",
          flush=True)

    # Первый запуск сразу
    job()

    sched.start()