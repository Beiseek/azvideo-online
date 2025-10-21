"""
Custom admin forms
"""
from django import forms
from .models import Movie, Series, Season, Episode, Person


class TMDBMovieForm(forms.ModelForm):
    tmdb_id = forms.IntegerField(label='TMDB ID', required=False)

    class Meta:
        model = Movie
        fields = '__all__'


class TMDBSeriesForm(forms.ModelForm):
    tmdb_id = forms.IntegerField(label='TMDB ID', required=False)

    class Meta:
        model = Series
        fields = '__all__'


class PersonAdminForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bio_uz'].widget.attrs.update({'rows': 10})


class EpisodeForm(forms.ModelForm):
    """Форма для эпизода с валидацией номера"""
    class Meta:
        model = Episode
        fields = '__all__'


class SeasonForm(forms.ModelForm):
    """Форма для сезона с валидацией номера"""
    class Meta:
        model = Season
        fields = '__all__'