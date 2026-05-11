from django.urls import path

from .views import CharacterAddXpView, CharacterDetailView, CharacterListCreateView, CharacterLongRestView, CharacterShortRestView


urlpatterns = [
    path("", CharacterListCreateView.as_view(), name="character-list"),
    path("<int:slot>/", CharacterDetailView.as_view(), name="character-detail"),
    path("<int:slot>/add-xp/", CharacterAddXpView.as_view(), name="character-add-xp"),
    path("<int:slot>/short-rest/", CharacterShortRestView.as_view(), name="character-short-rest"),
    path("<int:slot>/long-rest/", CharacterLongRestView.as_view(), name="character-long-rest"),
]
