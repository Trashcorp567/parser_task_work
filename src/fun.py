import json
from abc import ABC, abstractmethod
import requests
import os


class VacancyAPI(ABC):
    @abstractmethod
    def get_vacancies(self):
        pass


class VacancySaver(ABC):
    @abstractmethod
    def save_vacancy(self):
        pass

    @abstractmethod
    def update_vacancy(self):
        pass

    @abstractmethod
    def delete_vacancy(self):
        pass

    @abstractmethod
    def get_vacancy(self):
        pass


class HeadHunterAPI(VacancyAPI):
    @staticmethod
    def get_vacancies():
        response = requests.get('https://api.hh.ru/vacancies')
        if response.status_code == 200:
            vacancies = response.json()
            return vacancies
        else:
            print(response.status_code)


class JSONVacansy(VacancySaver, HeadHunterAPI):
    @staticmethod
    def save_vacancy():
        with open('vacancies.json', 'w') as file:
            json.dump(HeadHunterAPI.get_vacancies(), file, indent=4)

    @staticmethod
    def update_vacancy():
        JSONVacansy.delete_vacancy()
        JSONVacansy.save_vacancy()

    @staticmethod
    def delete_vacancy():
        os.remove('vacancies.json')

    @staticmethod
    def get_vacancy():
        with open('vacancies.json', 'r') as file:
            return file.read()


vacancy_data = JSONVacansy.get_vacancy()
vacancy_json = json.loads(vacancy_data)
test_inp = str(input())
for vacancy in vacancy_json['items']:
    if test_inp in vacancy['name']:
        print(vacancy['name'])
    else:
        print(f'Нет такого запроса {test_inp}')
for vacancy in vacancy_json['items']:
    print('Название:', vacancy['name'])
    #print('URL:', vacancy["employer"]['name'])
    #print(f"Сумма: {vacancy['salary']['from']} - {vacancy['salary']['to']}")
    #print("")

# Нужно додумать как получать фильтрованные данные, дописать класс и методы
# для хранения информация именно тех проф которые подходят пользователю
# Функции для сортировки вакансий(по названию по зп по требованиям(возможно)
# Создать класс для работы с вакансиями.
# В этом классе самостоятельно определить атрибуты, такие как название вакансии, ссылка на вакансию, зарплата,
# краткое описание или требования и т.п. (не менее четырех) Класс должен поддерживать методы сравнения вакансий
# между собой по зарплате и валидировать данные,
# которыми инициализируются его атрибуты.
# Определить абстрактный класс, который обязывает реализовать методы для добавления
# Пока сделал только для одного hh
# получить вакансии в отсортированном виде, получить вакансии,
# в описании которых есть определенные ключевые слова, например "postgres"(????) и т.п.
# Понять что я делаю
# Дописать readme
