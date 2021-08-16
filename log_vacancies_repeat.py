from classes_sqlalchemy import Course, Base, VacancyCheck
import aiohttp
import asyncio
from time import time
import pickle
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc
from sqlalchemy.sql.expression import func
import more_itertools
from multiprocessing import Process
from datetime import datetime, timedelta
import cchardet
from time import sleep
import pause
import test_time

with open('proxies.txt') as f:
    proxies = f.read().splitlines()

# async def xd(course):
#     async with aiohttp.ClientSession() as session:
#         await course.load_base_info(session, proxy, False)


def run_main(proxy_list, first_id, course_nrcs):
    asyncio.run(main(proxy_list, first_id, course_nrcs))


async def main(proxy_list, first_id, course_nrcs):
    engine.dispose()

    Session = sessionmaker(bind=engine)
    db_session = Session()

    vacancy_checks = []
    vacancies = []
    tasks = []
    proxy_session_list = []
    for proxy in proxy_list:
        timeout = aiohttp.ClientTimeout(total=25)
        connector = aiohttp.TCPConnector(force_close=True, limit=50)
        aio_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        proxy_session_list.append([proxy, aio_session, 0, False])

    courses = db_session.query(Course).filter(Course.nrc >= course_nrcs[0][1]).\
        filter(Course.nrc <= course_nrcs[-1][1]).order_by(asc(Course.nrc))
    for pos, course in enumerate(courses):
        vacancy_check_id = first_id + course_nrcs[pos][0]
        task = course.parse_save_vacancies(vacancy_check_id, vacancy_checks, vacancies, proxy_session_list, True)
        tasks.append(task)
    await asyncio.gather(*tasks)
    db_session.bulk_save_objects(vacancy_checks)
    db_session.bulk_save_objects(vacancies)
    for proxy, aio_session, num_failed, status in proxy_session_list:
        await aio_session.close()
    db_session.commit()
    db_session.close()

engine = create_engine('postgresql://nicobuzeta:Nibu2909@cursos-uc.postgres.database.azure.com:5432/cursos-uc',
                       client_encoding='unicode')

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


pauses = {
    timedelta(hours=1): 400,
    timedelta(minutes=10): 300,
    timedelta(minutes=7): 250,
    timedelta(minutes=5): 200,
    timedelta(minutes=3): 100
}


times = test_time.times()


# pause.until(dt1)

interval = 450

t1 = time()
n_run = 0
while True:

    lowest_delta = timedelta(days=10000)

    for specific_time in times:
        delta = abs(specific_time - datetime.now())
        if delta < lowest_delta:
            lowest_delta = delta
    interval = 'inf'

    for pause, pause_interval in pauses.items():
        if lowest_delta < pause:
            interval = pause_interval

    if interval == 'inf':
        raise Exception

    print(interval)

    t2 = time()
    try:
        Session = sessionmaker(bind=engine)

        session = Session()

        nrcs = [(c, x) for c, (x,) in enumerate(session.query(Course.nrc).order_by(asc(Course.nrc)))]

        n_processes = 8
        split_nrcs = more_itertools.divide(n_processes, nrcs)
        last_vacancy_check = session.query(func.max(VacancyCheck.id)).scalar()
        if last_vacancy_check is None:
            last_vacancy_check = 0
        starting_id = last_vacancy_check + 1

        sleep_time = interval - (time() - t1)
        if sleep_time < 0:
            sleep_time = 0
        sleep(sleep_time)
        t1 = time()
        print(f'Running {n_run}')
        if n_processes == 1:
            asyncio.run(main(proxies, starting_id, list(split_nrcs[0])))
        else:
            processes = []
            for x in range(n_processes):
                p = Process(target=run_main, args=(proxies, starting_id, list(split_nrcs[x])))
                processes.append(p)

            for process in processes:
                process.start()

            for process in processes:
                process.join()
        print(f'Done {n_run}')
        n_run += 1
        session.close()
    except Exception as e:
        print(e)
    print(time() - t1)

