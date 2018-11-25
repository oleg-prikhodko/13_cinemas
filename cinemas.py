import re
import sys
import urllib.parse

import requests
from bs4 import BeautifulSoup


class MovieNotFoundException(RuntimeError):
    def __init__(self):
        super().__init__("Could not find movie with that title")


def fetch_afisha_page(url="https://www.afisha.ru/msk/schedule_cinema/"):
    response = requests.get(url)
    html = response.text
    return html


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    movie_titles = soup.find_all("h3", {"class": "card__title"})
    return [title.string.strip() for title in movie_titles]


def fetch_movie_info(movie_title):
    url = "https://www.kinopoisk.ru/index.php"
    params = {"kp_query": movie_title}
    response = requests.get(url, params=params)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    non_breaking_space = "\u00A0"
    page_title = soup.title.string.strip()
    most_wanted = soup.select_one(".most_wanted")

    if most_wanted is not None:
        link = most_wanted.select_one("div.info > p > a")
        title = link.string.strip()
        if title not in movie_title:
            raise MovieNotFoundException()
        rating = most_wanted.select_one(".rating")
        if rating is None:
            return "—", "—"
        rating = rating["title"].replace(non_breaking_space, "")
        match = re.search(r"(\d\.\d*) \((\d*)\)", rating)
        rating_value = match.group(1)
        rating_count = match.group(2)

        return rating_value, rating_count
    elif re.sub(r"«|»", "", movie_title) in page_title:
        rating_value = soup.find("meta", attrs={"itemprop": "ratingValue"})[
            "content"
        ]
        rating_count = soup.find("meta", attrs={"itemprop": "ratingCount"})[
            "content"
        ]
        return rating_value, rating_count

    else:
        raise MovieNotFoundException()


def sort_movies_by_rating(movies):
    default_rating = 0
    rating_value_index = 1
    return sorted(
        movies,
        key=lambda movie: float(movie[rating_value_index])
        if re.search(r"\d\.\d*", movie[rating_value_index]) is not None
        else default_rating,
        reverse=True,
    )


def output_movies_to_console(movies, max_movies=10):
    movies = movies[:10]
    for movie in movies:
        print("{} | {} | {}".format(*movie))


if __name__ == "__main__":
    try:
        html = fetch_afisha_page()
        titles = parse_afisha_list(html)
        movies = [(title, *fetch_movie_info(title)) for title in titles]
    except (requests.RequestException, MovieNotFoundException) as err:
        sys.exit(err)
    movies = sort_movies_by_rating(movies)
    output_movies_to_console(movies)
