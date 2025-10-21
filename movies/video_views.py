from ranged_response import RangedFileResponse
from django.shortcuts import get_object_or_404
from .models import Movie, Episode

def serve_movie_video(request, slug):
    movie = get_object_or_404(Movie, slug=slug)
    # Предполагается, что у модели Movie есть поле video_file
    response = RangedFileResponse(request, open(movie.video_file.path, 'rb'), content_type='video/mp4')
    response['Content-Disposition'] = f'inline; filename="{movie.video_file.name}"'
    return response

def serve_episode_video(request, series_slug, season_num, episode_num):
    episode = get_object_or_404(
        Episode, 
        season__series__slug=series_slug, 
        season__season_number=season_num, 
        episode_number=episode_num
    )
    # Предполагается, что у модели Episode есть поле video_file
    response = RangedFileResponse(request, open(episode.video_file.path, 'rb'), content_type='video/mp4')
    response['Content-Disposition'] = f'inline; filename="{episode.video_file.name}"'
    return response
