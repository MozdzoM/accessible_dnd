# from django.shortcuts import render
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Alignment,
    Armor,
    Background,
    CharacterClass,
    Race,
    Skill,
    Spell,
    Weapon,
)
from .serializers import (
    AlignmentSerializer,
    ArmorSerializer,
    BackgroundSerializer,
    CharacterClassSerializer,
    RaceSerializer,
    SkillSerializer,
    SpellSerializer,
    WeaponSerializer,
)

# Create your views here.
class BootstrapView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        payload = {
            "classes": CharacterClassSerializer(CharacterClass.objects.all(), many=True).data,
            "races": RaceSerializer(Race.objects.all(), many=True).data,
            "backgrounds": BackgroundSerializer(Background.objects.all(), many=True).data,
            "alignments": AlignmentSerializer(Alignment.objects.all(), many=True).data,
            "armors": ArmorSerializer(Armor.objects.all(), many=True).data,
            "weapons": WeaponSerializer(Weapon.objects.all(), many=True).data,
            "skills": SkillSerializer(Skill.objects.all(), many=True).data,
            "spells": SpellSerializer(Spell.objects.all(), many=True).data,
        }
        return Response(payload)
    