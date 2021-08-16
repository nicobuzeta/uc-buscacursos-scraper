from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import enum
import datetime

Base = declarative_base()


import aiohttp
import asyncio
import bs4
import copy
import datetime
from collections import defaultdict

from functions import fetch_parse_html


class Course(Base):
    __table_args__ = {"schema": "2021-2"}
    __tablename__ = 'courses'
    base_url = 'http://buscacursos.uc.cl/'

    base_url_vacancies = 'https://buscacursos.uc.cl/informacionVacReserva.ajax.php'

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

    base_parameters_vacancies = {
        'nrc': '',
        'termcode': ''
    }

    nrc = Column(Integer, primary_key=True)
    semester = Column(String)
    departamento = Column(String)
    sigla = Column(String)
    permite_retiro = Column(String)
    dicta_ingles = Column(String)
    section = Column(Integer)
    need_special_approval = Column(String)
    area_fg = Column(String)
    formato_curso = Column(String)
    categoria = Column(String)
    nombre = Column(String)
    profesor = Column(String)
    campus = Column(String)
    credits = Column(Integer)

    schedules = relationship('Schedule', backref='course', cascade='all, delete')

    vacancy_checks = relationship('VacancyCheck', backref='course', cascade='all, delete')

    def __init__(self, nrc, semester):
        self.parameters = copy.deepcopy(self.base_parameters)

        self.parameters['cxml_semestre'] = semester
        self.parameters['cxml_nrc'] = nrc

        self.nrc = int(nrc)  # INT
        self.semester = semester
        # self.departamento = None  # INT
        # self.sigla = None  # STR
        # self.permite_retiro = None  # STR
        # self.dicta_ingles = None  # INT
        # self.section = None  # INT
        # self.need_special_approval = None  # INT
        # self.area_fg = None  # INT
        # self.formato_curso = None  # INT
        # self.categoria = None  # INT
        # self.nombre = None  # INT
        # self.professor = None  # INT
        # self.campus = None  # INT
        # self.credits = None  # INT

    async def load_base_info(self, proxy_session_list, use_proxy):
        page = await fetch_parse_html(self.base_url, self.parameters, proxy_session_list, use_proxy)
        table = page.find(attrs={'class': ['resultadosRowPar']})
        for _ in range(10):
            if table is None:
                page = await fetch_parse_html(self.base_url, self.parameters, proxy_session_list, use_proxy)
                table = page.find(attrs={'class': ['resultadosRowPar']})
            else:
                break
        rows = table.find_all('td', recursive=False)
        direct_rows = rows[1:14]
        time_table = rows[16].find('table')
        self.departamento = table.parent.find('tr').text.strip()
        self.sigla = direct_rows[0].text.strip()
        self.permite_retiro = direct_rows[1].text.strip()
        self.dicta_ingles = direct_rows[2].text.strip()
        self.section = int(direct_rows[3].text.strip())
        self.need_special_approval = direct_rows[4].text.strip()
        self.area_fg = direct_rows[5].text.strip()
        self.formato_curso = direct_rows[6].text.strip()
        self.categoria = direct_rows[7].text.strip()
        self.nombre = direct_rows[8].text.strip()
        self.profesor = direct_rows[9].text.strip()
        self.campus = direct_rows[10].text.strip()
        self.credits = int(direct_rows[11].text.strip())

        self.parse_schedule(time_table)
        print(f'adding Course {self.nrc}')

    def parse_schedule(self, table):
        rows = table.find_all('tr')
        for row in rows:
            row = row.find_all('td')
            type_class = row[1].text.strip()
            if type_class == '':
                type_class = None
            days, hours = row[0].text.split(':')
            days = days.split('-')
            hours = hours.split(',')
            for day in days:
                for hour in hours:
                    day = day.strip()
                    hour = hour.strip()
                    if day == '' or hour == '':
                        continue
                    schedule = Schedule(day=day, modulo=hour, class_type=type_class)
                    self.schedules.append(schedule)

    async def parse_save_vacancies(self, vacancy_check_id, vacancy_checks, vacancies, proxy_session_list, use_proxy):
        try:
            self.vacancy_parameters = copy.deepcopy(self.base_parameters_vacancies)
            self.vacancy_parameters['nrc'] = str(self.nrc)
            self.vacancy_parameters['termcode'] = self.semester
            page = await fetch_parse_html(self.base_url_vacancies, self.vacancy_parameters, proxy_session_list,
                                          use_proxy)
            if page is None:
                return None
            table = page.find('table')
            rows = table.find_all(attrs={'class': ['resultadosRowImpar', 'resultadosRowPar']})[1:-1]
            current_check = VacancyCheck(id=vacancy_check_id, nrc=self.nrc, time=datetime.datetime.now())
            vacancies_vector = defaultdict(lambda: copy.deepcopy([0, 0, 0]))
            for row in rows:
                row = row.find_all('td')
                escuela = row[0].text.strip()
                level = row[1].text.strip()
                program = row[2].text.strip()
                concentration = row[3].text.strip()
                slots = {
                    'Ofrecidas': int(row[6].text.strip()),
                    'Ocupadas': int(row[7].text.strip()),
                    'Disponibles': int(row[8].text.strip())
                }
                vacancies_vector[(escuela, level, program, concentration)][0] += slots['Ofrecidas']
                vacancies_vector[(escuela, level, program, concentration)][1] += slots['Ocupadas']
                vacancies_vector[(escuela, level, program, concentration)][2] += slots['Disponibles']
                # vacancy_information = Vacancy(vacancy_type=escuela, vacancy_level=level, vacancy_program=program,
                #                               vacancy_concentration=concentration, offered=slots['Ofrecidas'],
                #                               occupied=slots['Ocupadas'], available=slots['Disponibles'])
                # current_check.vacancies.append(vacancy_information)
            for (escuela, level, program, concentration), all_vacancies in vacancies_vector.items():
                vacancy_information = Vacancy(vacancy_check_id=current_check.id, vacancy_type=escuela,
                                              vacancy_level=level, vacancy_program=program,
                                              vacancy_concentration=concentration, offered=all_vacancies[0],
                                              occupied=all_vacancies[1], available=all_vacancies[2])
                vacancies.append(vacancy_information)
            vacancy_checks.append(current_check)
            # print('done')
        except Exception as e:
            pass
            # print(e)

    def __repr__(self):
        return str({'Nrc': self.nrc, 'departamento': self.departamento, 'Sigla': self.sigla,
                    'Permite Retiro': self.permite_retiro,
                    'Se Dicta en Ingles?': self.dicta_ingles, 'Section': self.section,
                    'Requiere Aprobacion Especial': self.need_special_approval, 'Area de FG': self.area_fg,
                    'Formato Curso': self.formato_curso, 'Categoria': self.categoria, 'Nombre': self.nombre,
                    'Profesor': self.profesor, 'Campus': self.campus, 'Creditos': self.credits})


class WeekDays(enum.Enum):
    Monday = 1
    L = 1

    Tuesday = 2
    M = 2

    Wednesday = 3
    W = 3

    Thursday = 4
    J = 4

    Friday = 5
    V = 5

    Saturday = 6
    S = 6

    Sunday = 7
    D = 7


class ClassTypes(enum.Enum):
    Clase = 1
    CLAS = 1

    Taller = 2
    TAL = 2

    Ayudantia = 3
    AYU = 3

    TER = 4

    LAB = 5

    PRA = 6

    TES = 7

    LIB = 8

    SUP = 9


class Schedule(Base):
    __table_args__ = {"schema": "2021-2"}
    __tablename__ = 'schedules'

    nrc = Column(Integer, ForeignKey('2021-2.courses.nrc'), primary_key=True)
    day = Column(Enum(WeekDays), primary_key=True)
    modulo = Column(String, primary_key=True)
    class_type = Column(Enum(ClassTypes), primary_key=True)



class VacancyCheck(Base):
    __table_args__ = {"schema": "2021-2"}
    __tablename__ = 'vacancy_checks'

    id = Column(Integer, primary_key=True)
    nrc = Column(Integer, ForeignKey('2021-2.courses.nrc'))
    time = Column(DateTime)
    vacancies = relationship('Vacancy', backref='vacancy_checks', cascade='all, delete')


class Vacancy(Base):
    __table_args__ = {"schema": "2021-2"}
    __tablename__ = 'vacancies'

    vacancy_check_id = Column(Integer, ForeignKey('2021-2.vacancy_checks.id'), primary_key=True)
    vacancy_type = Column(String, primary_key=True)
    vacancy_level = Column(String, primary_key=True)
    vacancy_program = Column(String, primary_key=True)
    vacancy_concentration = Column(String, primary_key=True)
    offered = Column(Integer)
    occupied = Column(Integer)
    available = Column(Integer)

