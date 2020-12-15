import requests
import bs4
from string import ascii_lowercase



def check_overflow(page_to_check):
    res = page_to_check.find_all(attrs={'class': 'bordeBonito'})
    if len(res) == 1:
        if '750' in res[0].text:
            return True
        elif 'no produjo resultados' in res[0].text:
            return False
        else:
            raise Exception('Wrong class result len == 1\n'
                            f'{res}')
    elif len(res) > 1:
        raise Exception('Wrong class result len > 1\n'
                        f'{res}')
    return False

def get_ids(page_to_check):
    ids = []
    for x in page_to_check.find_all(attrs={'class': ['resultadosRowImpar', 'resultadosRowPar']}):
        ids.append(str(x.find('td').text))
    return ids

base_url = 'http://buscacursos.uc.cl/'

proxies = [
    '142.147.108.43:3128',
    '167.160.78.243:3128',
    '172.96.95.213:3128',
    '216.180.106.248:3128',
    '216.41.233.253:3128'
]

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
custom_parameters = base_parameters

custom_parameters['cxml_semestre'] = '2020-2'

alphabet = list(ascii_lowercase)
current_letter_index = [0]
custom_parameters['cxml_nombre'] = alphabet[current_letter_index[0]]

proxy_counter = 0

all_ids = []

while current_letter_index != (len(alphabet) - 1):
    letter = ''.join([alphabet[x] for x in current_letter_index])
    print(letter)
    custom_parameters['cxml_nombre'] = letter
    r = requests.get(base_url, params=base_parameters, proxies={'http': f'http://{proxies[proxy_counter]}'})
    page = bs4.BeautifulSoup(r.content, 'html5lib')
    if check_overflow(page):
        current_letter_index += [0]
        continue
    else:
        all_ids.extend(get_ids(page))
    level_al = len(current_letter_index)
    if current_letter_index[-1] == (len(alphabet) - 1) and level_al != 1:
        current_letter_index = current_letter_index[:-1]
        current_letter_index[-1] += 1
    else:
        current_letter_index[-1] += 1
    if current_letter_index[-1] > (len(alphabet) - 1) and level_al == 1:
        break
    proxy_counter += 1
    if proxy_counter > (len(proxies) - 1):
        proxy_counter = 0





print(all_ids)

