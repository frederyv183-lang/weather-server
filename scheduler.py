# -*- coding: utf-8 -*-

"""

   .



    Flask (. server.py).

    (BackgroundScheduler),   .



   ( ):

    python scheduler.py



Cron-:

    sched.add_job(job, "cron", hour="*/3", minute=20)

    sched.add_job(cleanup, "cron", hour=3, minute=0)

"""



import os

import shutil

from datetime import datetime, timedelta



from apscheduler.schedulers.background import BackgroundScheduler

from apscheduler.schedulers.blocking import BlockingScheduler



from maps_generator import generate_all_layers, ARCHIVE_DIR





#   90 

ARCHIVE_RETENTION_DAYS = 90



#   

_scheduler = None





def job_synoptic_maps():

    """   +  ."""

    print("[scheduler]    ...", flush=True)

    try:

        from synoptic_maps.generator import (

            generate_maps, cleanup_old_archive,

        )

        files = generate_maps(

            levels=(500, 850),

            steps=(0, 12, 24),

            regions=("etr",),

            include_ot=True,

        )

        removed = cleanup_old_archive()

        print(f"[scheduler] : {len(files)}  , "

              f" : {removed}", flush=True)

    except Exception as e:

        print(f"[scheduler]   : {e}", flush=True)





def job():

    """ :  Render  ,   ."""

    # [PATCH scheduler.render_check]
    import os as _os3
    _render_env3 = (_os3.environ.get("RENDER") or "").strip().lower()
    _is_render3 = _render_env3 in ("true", "1", "yes", "on")
    print("[scheduler] Запуск генерации карт...", flush=True)
    try:
        if _is_render3:

            files = generate_all_layers(

                models=["gfs"],

                steps=[12],

                fields=["t_2m", "pmsl"],

            )

        else:

            files = generate_all_layers(

                models=["icon-eu", "gfs"],

                steps=[6, 12, 18, 24],

                fields=["t_2m", "pmsl", "u_10m", "v_10m", "tot_prec", "clct"],

            )

        print(f"[scheduler] , : {len(files)}", flush=True)

    except Exception as e:

        print(f"[scheduler]  : {e}", flush=True)





def cleanup_archive():

    """

       ARCHIVE_RETENTION_DAYS .

    : static/maps/archive/YYYY/MM/DD/

    """

    print("[scheduler]  ...", flush=True)



    if not os.path.isdir(ARCHIVE_DIR):

        print("[scheduler]  ", flush=True)

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

                        print(f"[scheduler]   : {year}/{month}/{day}",

                              flush=True)

                    except Exception as e:

                        print(f"[scheduler]     "

                              f"{year}/{month}/{day}: {e}", flush=True)



            try:

                if not os.listdir(month_path):

                    os.rmdir(month_path)

                    removed_dirs += 1

            except OSError:

                pass



        try:

            if not os.listdir(year_path):

                os.rmdir(year_path)

                removed_dirs += 1

        except OSError:

            pass



    print(f"[scheduler]  : "

          f"{removed_days} , {removed_dirs}  ", flush=True)





def init_scheduler(app=None):

    """

      .



      server.py   .

          debug=True (Flask reloader).

    """

    global _scheduler

    if _scheduler is not None:

        print("[scheduler]  ,   ",

              flush=True)

        return _scheduler



    #      Flask reloader

    if app is not None and app.debug:

        # WERKZEUG_RUN_MAIN == "true"     reloader

        if os.environ.get("WERKZEUG_RUN_MAIN") != "true":

            print("[scheduler]   reloader-", flush=True)

            return None



    _scheduler = BackgroundScheduler(timezone="UTC")



    #    3  ( :20)

    import os as _os

    if _os.environ.get("RENDER") != "true":

        _scheduler.add_job(

            job,

            "cron",

            hour="*/3",

            minute=20,

            id="update_maps",

            replace_existing=True,

        )



    #     6  ( :40)

    _scheduler.add_job(

        job_synoptic_maps,

        "cron",

        hour="*/6",

        minute=40,

        id="synoptic_maps",

        replace_existing=True,

    )



    #       03:00 UTC

    _scheduler.add_job(

        cleanup_archive,

        "cron",

        hour=3,

        minute=0,

        id="cleanup_archive",

        replace_existing=True,

    )



    _scheduler.start()



    print(

        f"[scheduler]   .   3 , "

        f"     ( {ARCHIVE_RETENTION_DAYS} ).",

        flush=True,

    )



    #    ( ,     Flask)

    # [PATCH scheduler.render_check]
    import os as _os2
    _render_env2 = (_os2.environ.get("RENDER") or "").strip().lower()
    _is_render2 = _render_env2 in ("true", "1", "yes", "on")
    if not _is_render2:

        try:

            import threading

            threading.Thread(target=job, daemon=True).start()

            print("[scheduler]     ", flush=True)

        except Exception as e:

            print(f"[scheduler]   : {e}", flush=True)



    return _scheduler





# ============================================================

#   (python scheduler.py)

# ============================================================

if __name__ == "__main__":

    sched = BlockingScheduler(timezone="UTC")



    sched.add_job(job, "cron", hour="*/3", minute=20)

    sched.add_job(cleanup_archive, "cron", hour=3, minute=0)



    print(

        f"[scheduler]  .   3 , "

        f"     ( {ARCHIVE_RETENTION_DAYS} ).",

        flush=True,

    )



    #   

    job()



    sched.start()