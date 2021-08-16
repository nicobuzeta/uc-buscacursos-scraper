import bs4
from functions import fetch_html
import aiohttp
import asyncio
import time

async def check_existence_nrc(search, session, url, base_params, proxy):
    params = base_params
    params['cxml_nrc'] = search
    params['cxml_semestre'] = semester
    for _ in range(10):
        try:
            res = await fetch_html(session, url, params, proxy, False)
            html_res = await res.read()
            break
        except Exception as e:
            print(e)
    page = bs4.BeautifulSoup(html_res, 'lxml')
    if len(page.find_all('table')) == 7:
        print(f'Done {search}')
        return search


async def main_nrc(url, base_params, use_proxies):
    tasks = []
    sessions = []
    responses = []
    counter = 0
    connector = aiohttp.TCPConnector(force_close=True, limit=300)
    session = aiohttp.ClientSession(connector=connector)
    sessions.append(session)
    for c, nrc in enumerate(range(10000, 29000)):
    # for c, nrc in enumerate(range(10000, 11000)):
        proxy_use = c % len(proxies)
        proxy_use = use_proxies[proxy_use]

        task = check_existence_nrc(str(nrc), session, url, base_params, proxy_use)
        tasks.append(task)
        if counter == 1000:
            print(f'Running {nrc}')
            response = await asyncio.gather(*tasks)
            tasks = []
            responses.extend(response)
            counter = 0
            connector = aiohttp.TCPConnector(force_close=True, limit=300)
            session = aiohttp.ClientSession(connector=connector)
            sessions.append(session)
        counter += 1
    response = await asyncio.gather(*tasks)
    responses.extend(response)
    await asyncio.gather(*[session.close() for session in sessions])
    return list(filter(None, responses))


with open('proxies2.txt') as f:
    proxies = f.read().splitlines()

base_url = 'http://buscacursos.uc.cl/'

base_parameters = {
    'cxml_semestre': '',
    'cxml_sigla': '',
    'cxml_nrc': '',
    'cxml_nombre': '',
    'cxml_categoria': 'TODOS',
    'cxml_area_fg': 'TODOS',
    'cxml_formato_cur': 'TODOS',
    'cxml_profesor': '',
    'cxml_campus': 'TODOS',
    'cxml_unidad_academica': 'TODOS',
    'cxml_horario_tipo_busqueda': 'si_tenga',
    'cxml_horario_tipo_busqueda_actividad': 'TODOS'
}

semester = '2021-2'

top = 50000

t1 = time.time()
res = asyncio.run(main_nrc(base_url, base_parameters, proxies))
t2 = time.time()

print(res)
print(len(res))
print(t2 - t1)

with open('nrcs.txt', 'w') as f:
    for nrc in res:
        f.write(nrc + '\n')