from classes_sqlalchemy import Course, Base
import aiohttp
import asyncio
from time import time
import pickle
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


with open('proxies2.txt') as f:
    proxies = f.read().splitlines()

# async def xd(course):
#     async with aiohttp.ClientSession() as session:
#         await course.load_base_info(session, proxy, False)


async def main(proxy_list, semester, db_session):
    tasks = []
    courses = []
    proxy_session_list = []
    for proxy in proxy_list:
        connector = aiohttp.TCPConnector(force_close=True, limit=300)
        aio_session = aiohttp.ClientSession(connector=connector)
        proxy_session_list.append([proxy, aio_session, 0, False])
    for nrc in nrcs:
        course = Course(nrc, semester)
        courses.append(course)
        task = course.load_main_page(proxy_session_list, True)
        tasks.append(task)
    await asyncio.gather(*tasks)
    for proxy, aio_session, num_failed, status in proxy_session_list:
        await aio_session.close()
    db_session.add_all(courses)
    return courses


with open('nrcs.txt') as f:
    nrcs = f.read().splitlines()

engine = create_engine('postgresql://nicobuzeta:Nibu2909@cursos-uc.postgres.database.azure.com:5432/cursos-uc',
                       echo=True, client_encoding='unicode')

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()

t1 = time()
res = asyncio.run(main(proxies, '2021-2', session))
t2 = time()



print(res)
print(len(res))
print(t2 - t1)

t1 = time()
session.commit()
t2 = time()
print(t2 - t1)