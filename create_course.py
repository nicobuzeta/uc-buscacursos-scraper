from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from classes_sqlalchemy import Course, Base
import asyncio
import aiohttp


async def test(course):
    async with aiohttp.ClientSession() as ses:
        await course.load_base_info(ses, ['104.227.191.159:3128'], True)
        await course.parse_save_vacancies(ses, ['104.227.191.159:3128'], True)

engine = create_engine('postgresql://nicobuzeta:Nibu2909@cursos-uc.postgres.database.azure.com:5432/cursos-uc', echo=True, client_encoding='unicode')

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


course = Course(26335, '2021-2')


asyncio.run(test(course))


session = Session()

session.merge(course)

session.commit()