import requests
from bs4 import BeautifulSoup

# class FilmParser:
#
#     def __init__(self, base_url='https://ticketon.kz/almaty/cinema'):
#         self.base_url = base_url
#
#     def find_category(self, name_category):
#         url = f'{self.base_url}/{name_category}'
#         return url
#
#     def find_data_pages(self, number, url):
#         urls = []
#         for i in range(1, number + 1):
#             url_page = f'{url}/page/{i}'
#             urls.append(url_page)
#         return urls
#
#     def find_full_data(self, number_of_pages, url):
#         films = []
#         pages = self.find_data_pages(number_of_pages, url)
#         for page_url in pages:
#             response = requests.get(page_url)
#             data = BeautifulSoup(response.text, 'lxml')
#             for film_data in data.find_all('div', class_='shortpost'):
#                 link = film_data.div.a['href']
#                 name = film_data.div.a.img['alt']
#                 films.append({'name': name, 'link': link})
#         return films
#
#
# film = FilmParser()
# print(film.find_full_data(5, film.find_category('anime')))

url = 'https://ticketon.kz/almaty/cinema'
page = requests.get(url)
filtered_films = []
all_films = []
soup = BeautifulSoup(page.text, "html.parser")
print(soup)
