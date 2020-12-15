import requests
import bs4


r = requests.get('http://buscacursos.uc.cl/?cxml_semestre=2020-2&cxml_sigla=&cxml_nrc=&cxml_nombre=b&cxml_categoria=TODOS&cxml_area_fg=TODOS&cxml_formato_cur=TODOS&cxml_profesor=&cxml_campus=TODOS&cxml_unidad_academica=TODOS&cxml_horario_tipo_busqueda=si_tenga&cxml_horario_tipo_busqueda_actividad=TODOS#resultados')
page = bs4.BeautifulSoup(r.content, 'html5lib')
print(len(page.find_all('tbody')))
y = 0
for c, x in enumerate(page.find_all('table')):
    s = x.find_all(attrs={'class': 'resultadosRowPar'})
    if s:
        y += 1
        print(c)
        print('ids')
        l = 0
        l += len(x.find_all(attrs={'class': 'resultadosRowPar'}))
        l += len(x.find_all(attrs={'class': 'resultadosRowImpar'}))
        print(l)

print(y)

print(type(page.find_all(attrs={'class': 'resultadosRowPar'})))
print(len(page.find_all(attrs={'class': 'resultadosRowImpar'})))
print(type(page.find_all(attrs={'class': ['resultadosRowImpar', 'resultadosRowPar']})[0].find('td').text))