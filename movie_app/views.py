from django.shortcuts import render, get_object_or_404, HttpResponseRedirect

from .forms import MovieForm
from .models import Movie, Director, Actor
from .models import Feedback
from django.views.generic import ListView, DetailView
from bs4 import BeautifulSoup
from django.http import JsonResponse
import requests
from django.utils.text import slugify
from datetime import datetime


def show_one_movie(request, slug_movie: str):
    movie = get_object_or_404(Movie, slug=slug_movie)

    form = MovieForm()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            feed = Feedback(
                review=form.cleaned_data['review'],
            )
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
        queryset = super().get_queryset()
        return queryset


class DirectorListView(ListView):
    model = Director
    template_name = 'movie_app/all_director.html'
    context_object_name = 'directors'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class DirectorDetailView(DetailView):
    model = Director
    template_name = 'movie_app/one_director.html'


class ActorListView(ListView):
    model = Actor
    template_name = 'movie_app/all_actor.html'
    context_object_name = 'actors'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class ActorDetailView(DetailView):
    model = Actor
    template_name = 'movie_app/one_actor.html'


def get_rate_movie(request):
    form = MovieForm()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return HttpResponseRedirect('/done_review')
    return render(request, 'movie_app/one_movie.html', context={'form': form})


def done_review(request):
    return render(request, 'movie_app/done_review.html')


def main_page(request):
    return render(request, 'movie_app/home_page.html')


def parse_movies(request):
    url = 'https://ticketon.kz/cinema'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return render(request, 'movie_app/error.html', {'error': 'Ошибка при получении данных с сайта'})

    movies = []

    for movie in soup.find_all('a', class_='list-item__link'):
        link = 'https://ticketon.kz' + movie.get('href')
        title_tag = movie.find('span', class_='list-item__event')
        if title_tag:
            title = title_tag.get_text(strip=True)
            movies.append({'title': title, 'url': link})

    for movie_data in movies:
        try:
            movie_response = requests.get(movie_data['url'])
            movie_response.raise_for_status()
            movie_soup = BeautifulSoup(movie_response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movie details for {movie_data['title']}: {e}")
            continue

        year = 'Не указан'
        director_name = 'Не указан'
        cast_names = []

        for p in movie_soup.find_all('p'):
            strong_tag = p.find('strong')
            if strong_tag:
                label = strong_tag.get_text(strip=True).lower()
                value = p.get_text(strip=True).replace(strong_tag.get_text(strip=True), '').strip(' :')

                if 'год выпуска' in label:
                    year = value
                elif 'режиссер' in label:
                    director_name = value
                elif 'главные роли' in label:
                    cast_names = value.split(', ')

        # Check for existing movie
        slug_title = slugify(title)
        existing_movie = Movie.objects.filter(slug=slug_title, year=int(year) if year.isdigit() else None).first()
        if existing_movie:
            print(f"Skipping duplicate movie entry: {title} ({year})")
            continue

        # Process director
        director_name_parts = director_name.split()
        if len(director_name_parts) >= 2:
            director, _ = Director.objects.get_or_create(
                first_name=director_name_parts[0],
                last_name=director_name_parts[1]
            )
        elif director_name_parts:
            director, _ = Director.objects.get_or_create(
                first_name=director_name_parts[0],
                last_name=""
            )
        else:
            print(f"Skipping director creation for movie {title} due to missing data.")
            continue

        # Process actors
        actors = []
        for actor_name in cast_names:
            actor_name_parts = actor_name.split(' ', 1)
            actor_first_name = actor_name_parts[0]
            actor_last_name = actor_name_parts[1] if len(actor_name_parts) > 1 else ""

            actor, _ = Actor.objects.get_or_create(
                first_name=actor_first_name,
                last_name=actor_last_name
            )
            actors.append(actor)

        # Save movie
        movie = Movie(
            name=title,
            year=int(year) if year.isdigit() else None,
            director=director,
            budget=1000000,
            rating=7,
            slug=slug_title
        )
        movie.save()
        movie.actor.set(actors)

    return render(request, 'movie_app/success.html', {'movies': movies})
