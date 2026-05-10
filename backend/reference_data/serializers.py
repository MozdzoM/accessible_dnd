from rest_framework import serializers

from .models import Alignment, Armor, Background, CharacterClass, Race, Skill, Spell, Weapon


class CharacterClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterClass
        fields = ("id", "name", "die_type")

class NamedSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name")

class RaceSerializer(NamedSerializer):
    class Meta(NamedSerializer.Meta):
        model = Race

class BackgroundSerializer(NamedSerializer):
    class Meta(NamedSerializer.Meta):
        model = Background

class AlignmentSerializer(NamedSerializer):
    class Meta(NamedSerializer.Meta):
        model = Alignment

class ArmorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Armor
        fields = ("id", "name", "armor_bonus", "dex_mode", "dex_cap")

class WeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weapon
        fields = ("id", "name", "die_count", "die_type")

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "ability")

class SpellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spell
        fields = ("id", "name", "spell_level")
        