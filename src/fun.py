import json
from abc import ABC, abstractmethod
import requests
import os


class VacancyAPI(ABC):
    """
    Абстрактный класс обязывающий реализовать метод API запросов
    """
    @abstractmethod
    def get_vacancies(self):
        pass


class VacancySaver(ABC):
    """
    Абстрактный класс обязывающий реализовать методы записи json
    """
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
    """
    Класс для работы с API запросами сайта HeadHunter
    """

    @classmethod
    def get_data(cls, per_page=50, page=1, text=None):
        """
        Метод для фильтрации полученных данных
        """
        all_vacancies = []
        headers = {
            'User-Agent': 'Homework'
        }
        params = {
            "text": text,
            "page": page,
            "per_page": per_page
        }
        response = requests.get('https://api.hh.ru/vacancies', headers=headers, params=params)
        if response.status_code == 200:
            vacancies = response.json()
            all_vacancies.extend(vacancies.get('items', []))
        else:
            print(response.status_code)

        return {'items': all_vacancies}


class SuperJobAPI(VacancyAPI):
    """
    Класс для работы с API запросами сайта SuperJob
    """
    api_key = "v3.r.137657357.791fa7b6a4bbec4e3bb7bdd5dbf4214e9ceaace3.493002b668a537f2ec0eead1216ef5959c90e56a"
    base_url = "https://api.superjob.ru/2.0"

    @staticmethod
    def get_data(page=0, count=20, keyword=None):
        """
        Метод для фильтрации полученных данных
        Параметры запроса меняются в самом блоке интеракция с пользователем
        """
        url = f"{SuperJobAPI.base_url}/vacancies/"
        headers = {
            "X-Api-App-Id": SuperJobAPI.api_key
        }
        params = {
            "keyword": keyword,
            "page": page,
            "count": count
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if response.status_code == 200:
            vacancies = data.get("objects", [])
            return vacancies
        else:
            print(data)

        return []


class Vacancy:

    def __init__(self, name, link, salary, description, currency):
        """
        Инициализация класса по атрибутам полученным с помощьб метода from_json
        """
        self.name = name
        self.link = link
        self.salary = salary
        self.description = description
        self.currency = currency

    @classmethod
    def from_json(cls, data):
        """
        Метод для получения атрибутов из json файла для работы с HH и SJ
        """
        vacancies = []
        try:
            for vacancy_data in data["items"]:
                name = vacancy_data.get('name')
                link = vacancy_data.get('alternate_url')
                if vacancy_data['salary'] != 0:

                    try:
                        salary = vacancy_data['salary'].get('from')
                        currency = vacancy_data['salary'].get('currency')

                    except:
                        salary = "Информация об оплате отсутствует"
                        currency = ""

                else:
                    salary = "Информация об оплате отсутствует"
                    currency = ""

                description = vacancy_data['snippet'].get('responsibility')
                vacancy = cls(name, link, salary, description, currency)
                vacancies.append(vacancy)
                return vacancies

        except:
            for vacancy_data in data:
                name = vacancy_data["profession"]
                link = vacancy_data['link']
                if vacancy_data['payment_from'] == 0:
                    salary == ""
                    currency = ""
                else:
                    currency = vacancy_data["currency"]
                    salary = vacancy_data['payment_from']
                description = vacancy_data["work"]
                vacancy = cls(name, link, salary, description, currency)
                vacancies.append(vacancy)
            return vacancies

    def __str__(self):
        return f"{self.name} ({self.salary})\n{self.description}\nLink: {self.link}"

    def __repr__(self):
        return f"Vacancy('{self.name}', '{self.link}', {self.salary}, '{self.description}')"

    def __lt__(self, other):
        return self.salary < other.salary

    def __le__(self, other):
        return self.salary <= other.salary

    def __eq__(self, other):
        return self.salary == other.salary

    def __ne__(self, other):
        return self.salary != other.salary

    def __gt__(self, other):
        return self.salary > other.salary

    def __ge__(self, other):
        return self.salary >= other.salary


class JSONVacancy(VacancySaver, HeadHunterAPI, SuperJobAPI):
    """
    Методы редактирования полученных данных в JSON файл
    При желании можно оъеденить, чтобы данные сохранялись в один файл
    """
    @classmethod
    def save_vacancy(cls, vacancies):
        with open('vacancies.json', 'w', encoding='utf-8') as file:
            json.dump(vacancies, file, indent=4, ensure_ascii=False)

    @classmethod
    def update_vacancy(cls):
        JSONVacancy.delete_vacancy()
        JSONVacancy.save_vacancy()

    @classmethod
    def delete_vacancy(cls):
        os.remove('vacancies.json')

    @classmethod
    def get_vacancy(cls):
        with open('vacancies.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            vacancies = Vacancy.from_json(json_data)
            return vacancies

    @classmethod
    def save_vacancy_for_sj(cls, vacancies):
        with open('vacancies_sj.json', 'w', encoding='utf-8') as file:
            json.dump(vacancies, file, indent=4, ensure_ascii=False)

    @classmethod
    def delete_vacancy_for_sj(cls):
        os.remove('vacancies_sj.json')

    @classmethod
    def get_vacancy_sj(cls):
        with open('vacancies_sj.json', 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            vacancies = Vacancy.from_json(json_data)
            return vacancies


def interact():
    """
    Функция работы с пользователем
    """
    # Взаимодействие с пользователем через консоль
    print("Поиск вакансий:")
    # Выбор платформы
    platform_choice = input("Выбирете платформу для поиска(HH или SJ): ").upper()
    if platform_choice == "HH":
        text = input("Введите текст поискового запроса: ")
        # Получение вакансий с использованием введенных пользователем данных
        hh_api = HeadHunterAPI.get_data(text=text)
        # Проверка наличия вакансий
        if hh_api and 'items' in hh_api:
            filtered_vacancies = [item for item in hh_api['items'] if text.lower() in item['name'].lower()]
            if filtered_vacancies:
                JSONVacancy.save_vacancy(filtered_vacancies)

                print(f"Найдено {len(filtered_vacancies)} вакансий:\n")

                for vac in filtered_vacancies:
                    vacancy = Vacancy.from_json({"items": [vac]})
                    for vacancy_item in vacancy:
                        print(f"{vacancy_item.name} -  {vacancy_item.salary} {vacancy_item.currency}")
                        print(f"Ссылка на вакансию: {vacancy_item.link}\n")
            else:
                print("Вакансии по заданному запросу не найдены.")

    elif platform_choice == "SJ":
        user_choice = input("Введите наименование вакансии: ")
        count = int(input("Введите количество вакансий для просмотра: "))
        # Получение вакансий с использованием введенных пользователем данных
        super_job_api = SuperJobAPI.get_data(page=0, count=count, keyword=user_choice)
        if super_job_api:
            JSONVacancy.save_vacancy_for_sj(super_job_api)
            # Инициализациия атрибутами класс Vacancy и присвоение их объекту
            vacancies = Vacancy.from_json(super_job_api)
            print(f"Найдено {len(vacancies)} вакансий:\n")
            if vacancies:
                for vac in vacancies:
                    # Выводимые параметры можно изменить другими атрибутами класса
                    print(f"Название: {vac.name}")
                    print(f"Оплата: от {vac.salary} {vac.currency}")
                    print(f"Ссылка на вакансию: {vac.link}\n")

    else:
        # Сообщает о неправильном выборе платформы и удаляет словари, если они есть
        JSONVacancy.delete_vacancy()
        JSONVacancy.delete_vacancy_for_sj()
        print("Платформа не найдена")
