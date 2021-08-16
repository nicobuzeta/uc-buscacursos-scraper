import bs4
import copy
import random
import aiohttp


async def fetch_html(session, url, params, proxy, use_proxy):
    if use_proxy:
        page = await session.get(url, params=params, proxy=f'{proxy}')
    else:
        page = await session.get(url, params=params)
    return page


async def fetch_parse_html(url, params, proxy_session_list, use_proxy=True):
    s = ''
    while True:
        # for proxy, aio_session in random.sample(proxy_session_list, len(proxy_session_list)):
        for proxy_num in random.sample(list(range(len(proxy_session_list))), len(proxy_session_list)):
            proxy = proxy_session_list[proxy_num][0]
            aio_session = proxy_session_list[proxy_num][1]
            try:
                res = await fetch_html(aio_session, url, params, proxy, use_proxy)
                html_res = await res.read()
                page = bs4.BeautifulSoup(html_res, 'lxml', from_encoding='utf-8')
                return page

            except Exception as e:
                # proxy_session_list[proxy_num][2] += 1
                # if proxy_session_list[proxy_num][2] >= 6 and not proxy_session_list[proxy_num][3]:
                #     proxy_session_list[proxy_num][2] = True
                #     await proxy_session_list[proxy_num][1].close()
                #     timeout = aiohttp.ClientTimeout(total=10)
                #     connector = aiohttp.TCPConnector(force_close=True, limit=300)
                #     aio_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
                #     proxy_session_list[proxy_num][3] = False
                #     proxy_session_list[proxy_num][2] = 0
                #     proxy_session_list[proxy_num][1] = aio_session
                s = e
        print(repr(s))
        return None

