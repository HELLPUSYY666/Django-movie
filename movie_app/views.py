from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from .forms import MovieForm
from .models import Movie, Director, Actor, Feedback
from django.views.generic import ListView, DetailView
from bs4 import BeautifulSoup
import requests
from django.utils.text import slugify
import redis
from django.core.cache import cache


def show_one_movie(request, pk: int):
    movie = get_object_or_404(Movie, pk=pk)
    form = MovieForm()

    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            feed = Feedback(review=form.cleaned_data['review'], movie=movie)
            feed.save()
            return HttpResponseRedirect('/done_review')

    return render(request, 'movie_app/one_movie.html', {
        'movie': movie,
        'form': form
    })


class MovieListView(ListView):
    model = Movie
    template_name = 'movie_app/all_movie.html'
    context_object_name = 'movies'

    def get_queryset(self):
        movies = cache.get('all_movies')
        if movies:
            print('Hit the cache')
        else:
            movies = Movie.objects.all()
            if movies.exists():
                cache.set('all_movies', movies, timeout=60 * 15)
                print('Hit the db')
            else:
                return HttpResponse('No movies found')
        return movies


class DirectorListView(ListView):
    model = Director
    template_name = 'movie_app/all_director.html'
    context_object_name = 'directors'

    def get_queryset(self):
        directors = cache.get('all_directors')
        if directors:
            print('Hit the cache')
        else:
            directors = Director.objects.all()
            if directors.exists():
                cache.set('all_directors', directors, timeout=60 * 15)
                print('Hit the db')
            else:
                return HttpResponse('No directors found')
        return directors


class DirectorDetailView(DetailView):
    model = Director
    template_name = 'movie_app/one_director.html'


class ActorListView(ListView):
    model = Actor
    template_name = 'movie_app/all_actor.html'
    context_object_name = 'actors'

    def get_queryset(self):
        actors = cache.get('all_actors')
        if actors:
            print('Hit the cache')
        else:
            actors = Actor.objects.all()
            if actors.exists():
                cache.set('all_actors', actors, timeout=60 * 15)
                print('Hit the db')
            else:
                return HttpResponse('No actors found')
        return actors


class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movie_app/one_actor.html'


def done_review(request):
    return render(request, 'movie_app/done_review.html')


def main_page(request):
    return render(request, 'movie_app/home_page.html')


def parse_movies(request):
    if request.method == 'POST':
        url = 'https://ticketon.kz/cinema'
        print(f"Получаем данные с URL: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            print("Данные успешно получены.")
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении данных с {url}: {e}")
            return render(request, 'movie_app/error.html', {'error': str(e)})

        movies = []

        for movie in soup.find_all('a', class_='list-item__link'):
            link = 'https://ticketon.kz' + movie.get('href')
            title_tag = movie.find('span', class_='list-item__event')
            if title_tag:
                title = title_tag.get_text(strip=True)
                movies.append({'title': title, 'url': link})
                print(f"Найден фильм: {title}")

        if not movies:
            return render(request, 'movie_app/success.html', {'message': 'Фильмы не найдены.'})

        for movie_data in movies:
            try:
                print(f"Получаем детали для фильма: {movie_data['title']}")
                movie_response = requests.get(movie_data['url'])
                movie_response.raise_for_status()
                movie_soup = BeautifulSoup(movie_response.content, 'html.parser')
            except requests.exceptions.RequestException as e:
                print(f"Ошибка при получении деталей фильма {movie_data['title']}: {e}")
                continue

            year = None
            director_name = 'Не указан'
            cast_names = []

            for p in movie_soup.find_all('p'):
                strong_tag = p.find('strong')
                if strong_tag:
                    label = strong_tag.get_text(strip=True).lower()
                    value = p.get_text(strip=True).replace(strong_tag.get_text(strip=True), '').strip(' :')

                    if 'год выпуска' in label:
                        if value != 'Не указан':
                            year = int(value)
                    elif 'режиссер' in label:
                        director_name = value
                    elif 'главные актёры:' in label:
                        cast_names = value.split(', ')

            first_name, last_name = director_name.split(' ', 1) if ' ' in director_name else (director_name, '')
            director, created = Director.objects.get_or_create(first_name=first_name, last_name=last_name)

            movie, created = Movie.objects.get_or_create(
                name=movie_data['title'],
                year=year,
                director=director,
                slug=slugify(movie_data['title'])
            )

            if not created:
                print(f"Фильм '{movie_data['title']}' уже существует в базе данных.")
                continue

            for actor_name in cast_names:
                first_name, last_name = actor_name.split(' ', 1) if ' ' in actor_name else (actor_name, '')
                actor, _ = Actor.objects.get_or_create(first_name=first_name, last_name=last_name)
                movie.actor.add(actor)

        return render(request, 'movie_app/success.html', {'movies': movies})

    return render(request, 'movie_app/home_page.html')


redis_client = redis.Redis(host='localhost', port=6379, db=0)

redis_client.close()
