import bs4
import copy
import random


async def fetch_html(session, url, params, proxy, use_proxy):
    if use_proxy:
        page = await session.get(url, params=params, proxy=f'http://{proxy}')
    else:
        page = await session.get(url, params=params)
    return page


async def fetch_parse_html(url, params, proxy_session_list, use_proxy=True):
    s = ''
    while True:
        for proxy, aio_session in random.sample(proxy_session_list, len(proxy_session_list)):
            try:
                res = await fetch_html(aio_session, url, params, proxy, use_proxy)
                html_res = await res.read()
                page = bs4.BeautifulSoup(html_res, 'lxml', from_encoding='utf-8')
                return page
            except Exception as e:
                s = e

        print('fetch_parse_html')
        print(s)
