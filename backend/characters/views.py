# from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Character
from .serializers import AddXpSerializer, CharacterSerializer, ConfirmCharacterDeleteSerializer, ShortRestSerializer
from .services import (
    ability_modifier,
    calculate_level,
    calculate_max_hp,
    get_character_for_slot,
    hit_die_average,
)


# Create your views here.
class CharacterListCreateView(generics.ListCreateAPIView):
    serializer_class = CharacterSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Character.objects.filter(user=self.request.user).select_related(
            "character_class",
            "race",
            "background",
            "alignment",
            "armor",
            "weapon",
        ).prefetch_related("skills", "spells").order_by("created_at", "id")

    def get_serializer_context(self):
        return {"request": self.request}


class CharacterDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, request: Request, slot: int) -> Character:
        return get_character_for_slot(request.user, slot)

    def get(self, request: Request, slot: int) -> Response:
        character = self.get_object(request, slot)
        return Response(CharacterSerializer(character).data)

    def patch(self, request: Request, slot: int) -> Response:
        character = self.get_object(request, slot)
        serializer = CharacterSerializer(character, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CharacterSerializer(character).data)

    def delete(self, request: Request, slot: int) -> Response:
        character = self.get_object(request, slot)
        serializer = ConfirmCharacterDeleteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        character.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CharacterAddXpView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request, slot: int) -> Response:
        character = get_character_for_slot(request.user, slot)
        serializer = AddXpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        previous_level = character.level
        character.xp += serializer.validated_data["amount"]
        character.level = calculate_level(character.xp)
        character.save()
        payload = CharacterSerializer(character).data
        payload["level_up"] = character.level > previous_level
        return Response(payload)


class CharacterShortRestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request, slot: int) -> Response:
        character = get_character_for_slot(request.user, slot)
        serializer = ShortRestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        spent = serializer.validated_data["spent_hit_dice"]
        available = max(character.level - character.used_hit_dice, 0)
        if spent > available:
            return Response(
                {
                    "spent_hit_dice": "not_enough_hit_dice",
                    "available_hit_dice": available,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        heal_per_die = max(1, hit_die_average(character.character_class.die_type) + ability_modifier(character.constitution))
        max_hp = calculate_max_hp(character.level, character.character_class.die_type, character.constitution)
        character.current_hp = min(max_hp, character.current_hp + (heal_per_die * spent))
        character.used_hit_dice += spent
        character.save()
        return Response(CharacterSerializer(character).data)


class CharacterLongRestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request, slot: int) -> Response:
        character = get_character_for_slot(request.user, slot)
        character.used_hit_dice = 0
        character.current_hp = calculate_max_hp(
            character.level,
            character.character_class.die_type,
            character.constitution,
        )
        character.save()
        return Response(CharacterSerializer(character).data)
    