from pprint import pprint
import urllib.parse

import requests
from bs4 import BeautifulSoup


def fetch_afisha_page(url="https://www.afisha.ru/msk/schedule_cinema/"):
    response = requests.get(url)
    html = response.text
    return html


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    movie_titles = soup.find_all('h3', {"class": "card__title"})
    return [title.string.strip() for title in movie_titles]


def fetch_movie_info(movie_title):
    url = "https://www.kinopoisk.ru/index.php"
    # params = {"kp_query": urllib.parse.quote_plus(movie_title)}
    params = {"kp_query": movie_title}
    response = requests.get(url, params=params)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    try:
        most_wanted = soup.select_one(".most_wanted")
        link = most_wanted.select_one('div.info > p > a')
        title = link.string.strip()
        rating = most_wanted.select_one('div.right > div.rating')["title"]
        if title == movie_title:
            return rating
        else:
            return None
    except Exception:
        return None



def output_movies_to_console(movies):
    pprint(movies)


if __name__ == '__main__':
    html = fetch_afisha_page()
    titles = parse_afisha_list(html)
    movies = [(title, fetch_movie_info(title)) for title in titles]
    output_movies_to_console(movies)
