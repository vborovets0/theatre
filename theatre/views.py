from django.db.models import F, Count
from django.shortcuts import render
from rest_framework import viewsets

from theatre.models import Genre, Actor, TheatreHall, Play, Performance
from theatre.serializers import GenreSerializer, ActorSerializer, TheatreHallSerializer, PlaySerializer, \
    PlayListSerializer, PlayDetailSerializer, PerformanceSerializer, PerformanceListSerializer, \
    PerformanceDetailSerializer


def _params_to_int(qs):
    return [int(str_id) for str_id in qs.split(",")]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_queryset(self):
        queryset = self.queryset

        # filtering
        title = self.request.query_params.get("title")
        actors = self.request.query_params.get("actors")
        genres = self.request.query_params.get("genres")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if actors:
            actors_ids = _params_to_int(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)

        if genres:
            genres_ids = _params_to_int(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("actors", "genres")

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        return PlaySerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset.select_related("play", "theatre_hall")

        if self.action == "list":
            queryset = queryset.annotate(
                tickets_available=(
                    F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                    - Count("tickets")
                )
            ).order_by("id")

        # filtering
        play = self.request.query_params.get("play")
        date = self.request.query_params.get("date")

        if play:
            play_id = _params_to_int(play)
            queryset = queryset.filter(play__id__in=play_id)

        if date:
            queryset = queryset.filter(show_time__date=date)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer



