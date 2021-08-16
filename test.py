import pickle
from collections import defaultdict
import aiohttp
import asyncio
import time
import cchardet
from multiprocessing import Pool, Process, Queue

with open('proxies2.txt') as f:
    proxies = f.read().splitlines()
    print(proxies)

# proxies = [
#     '172.245.11.90:3128',
#     '192.186.139.165:3128',
#     '198.46.203.228:3128',
#     '23.95.47.222:3128',
#     '23.95.5.18:3128'
# ]

# proxies = [
#     '172.245.11.90:3128',
#     '192.186.139.165:3128',
#     '198.46.203.228:3128'
# ]

with open('classes.pickle', 'rb') as f:
    courses = pickle.load(f)


def run_main(given_courses, q):
    asyncio.run(main(given_courses))
    q.put(given_courses)

async def main(all_courses):
    tasks = []
    sessions = []
    chunk_size = (len(nrcs) // len(proxies)) + 1
    for c, i in enumerate(range(0, len(nrcs), chunk_size)):
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(force_close=True, limit=300)
        session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        sessions.append(session)
        # print(all_courses)
        courses_sublist = all_courses[i: i + chunk_size]
        for specific_course in courses_sublist:
            task = specific_course.parse_save_vacancies(session, proxies[c])
            tasks.append(task)
    completed_tasks = await asyncio.gather(*tasks)
    await asyncio.gather(*[session.close() for session in sessions])
    return completed_tasks

lol = defaultdict(int)
nrcs = []
for course in courses:
    lol[course.departamento] += 1
    # if course.departamento == 'Ingeniería':
    nrcs.append(course)


print(nrcs[0])
processes = []
cores = 7
step = (len(nrcs) // 7) + 1
queue = Queue()
for x in range(7):
    start = x * step
    end = step * (x + 1)
    sublist = nrcs[start:end]
    p = Process(target=run_main, args=(sublist, queue))
    processes.append(p)

for process in processes:
    process.start()

t1 = time.time()

results = []

[results.extend(queue.get()) for _ in range(cores)]

for process in processes:
    process.join()

print(time.time() - t1)
print(results[0])
print(lol)
print(len(results))


# print(results[0])