import random
from django.contrib import admin
from .models import Movie, Director, Actor, DressingRoom
from django.db.models import QuerySet

admin.site.register(Director)
admin.site.register(Actor)
# admin.site.register(DressingRoom)


@admin.register(DressingRoom)
class DressingRoomAdmin(admin.ModelAdmin):
    list_display = ('floor', 'number', 'actor')


class RatingFilter(admin.SimpleListFilter):
    title = 'Фильтр по рейтенгу'
    parameter_name = 'rating'

    def lookups(self, request, model_admin):
        return [
            ('<4', 'Низкий'),
            ('<6', 'Средний'),
            ('<8', 'Высокий'),
            ('<=10', 'Крутяк')
        ]

    def queryset(self, request, queryset):
        if self.value() == '<4':
            return queryset.filter(rating__lt=4)
        if self.value() == '<6':
            return queryset.filter(rating__gt=4).filter(rating__lt=6)
        if self.value() == '<9':
            return queryset.filter(rating__gt=6).filter(rating__lt=8)
        if self.value() == '<11':
            return queryset.filter(rating__gt=8).filter(rating__lte=10)
        return queryset


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'year', 'budget', 'rating_status', 'director',)
    list_editable = ('rating', 'year', 'budget', 'director')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 5
    search_fields = (['name'])
    filter_horizontal = ['actor']
    list_filter = ['name', RatingFilter]

    @admin.display(ordering='-rating', description='Личное мнение')
    def rating_status(self, movie):
        if movie.rating is None:
            return 'Рейтинг не указан'
        elif movie.rating < 2:
            return 'Говно не смотрите'
        elif movie.rating < 5:
            return 'Прикольно на разок'
        elif movie.rating < 8:
            return 'Один из крутых'
        elif movie.name == 'Fight Club':
            return 'ШЕДЕВР'
        else:
            return 'Просто ахуенно'

    actions = ['set_shit', 'set_good', 'set_perfect']

    @admin.action(description='Сменить рейтинг на < 2')
    def set_shit(self, request, qs: QuerySet):
        count_updated = qs.count()
        qs.update(rating=random.randint(0, 1))
        self.message_user(request, f'Было обновлено {count_updated} записей')

    @admin.action(description='Сменить рейтинг на < 5')
    def set_good(self, request, qs: QuerySet):
        count_updated = qs.count()
        qs.update(rating=random.randint(2, 4))
        self.message_user(request, f'Было обновлено {count_updated} записей')

    @admin.action(description='Сменить рейтинг на < 8')
    def set_perfect(self, request, qs: QuerySet):
        count_updated = qs.count()
        qs.update(rating=random.randint(5, 7))
        self.message_user(request, f'Было обновлено {count_updated} записей')
