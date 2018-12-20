from django.shortcuts import render

from .models import Album


def index(request):
    album_list = Album.objects.order_by('-money')
    context = {'album_list': album_list}
    return render(request, 'index.html', context)
