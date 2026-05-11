from django.db import transaction
from rest_framework import serializers

from reference_data.models import Alignment, Armor, Background, CharacterClass, Race, Skill, Spell, Weapon
from reference_data.serializers import (
    AlignmentSerializer,
    ArmorSerializer,
    BackgroundSerializer,
    CharacterClassSerializer,
    RaceSerializer,
    SkillSerializer,
    SpellSerializer,
    WeaponSerializer,
)

from .constants import ABILITY_FIELDS, ALLOWED_ABILITY_SET
from .models import Character
from .services import (
    ability_modifiers,
    armor_class,
    calculate_level,
    calculate_max_hp,
    ensure_character_limit,
    get_slot_for_character,
    max_hit_dice_count,
    proficiency_bonus,
    remaining_hit_dice,
    xp_progress,
)

COMMON_FIELD_ERROR_MESSAGES = {
    "blank": "blank",
    "invalid": "invalid",
    "max_length": "max_length",
    "min_length": "min_length",
    "required": "required",
}
NUMBER_FIELD_ERROR_MESSAGES = {
    **COMMON_FIELD_ERROR_MESSAGES,
    "max_value": "max_value",
    "min_value": "min_value",
}
REFERENCE_FIELD_ERROR_MESSAGES = {
    **COMMON_FIELD_ERROR_MESSAGES,
    "does_not_exist": "invalid_reference",
    "incorrect_type": "invalid_reference",
}


class CharacterSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, error_messages=COMMON_FIELD_ERROR_MESSAGES)
    class_id = serializers.PrimaryKeyRelatedField(
        source="character_class",
        queryset=CharacterClass.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    race_id = serializers.PrimaryKeyRelatedField(
        source="race",
        queryset=Race.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    background_id = serializers.PrimaryKeyRelatedField(
        source="background",
        queryset=Background.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    alignment_id = serializers.PrimaryKeyRelatedField(
        source="alignment",
        queryset=Alignment.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    armor_id = serializers.PrimaryKeyRelatedField(
        source="armor",
        queryset=Armor.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    weapon_id = serializers.PrimaryKeyRelatedField(
        source="weapon",
        queryset=Weapon.objects.all(),
        write_only=True,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    skill_ids = serializers.PrimaryKeyRelatedField(
        source="skills",
        queryset=Skill.objects.all(),
        many=True,
        write_only=True,
        required=False,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )
    spell_ids = serializers.PrimaryKeyRelatedField(
        source="spells",
        queryset=Spell.objects.all(),
        many=True,
        write_only=True,
        required=False,
        error_messages=REFERENCE_FIELD_ERROR_MESSAGES,
    )

    character_class = CharacterClassSerializer(read_only=True)
    race = RaceSerializer(read_only=True)
    background = BackgroundSerializer(read_only=True)
    alignment = AlignmentSerializer(read_only=True)

    has_shield = serializers.BooleanField(required=False, error_messages=COMMON_FIELD_ERROR_MESSAGES)
    armor = ArmorSerializer(read_only=True)
    weapon = WeaponSerializer(read_only=True)
    skills = serializers.SerializerMethodField()
    spells = SpellSerializer(read_only=True, many=True)

    current_hp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    used_hit_dice = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    xp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)

    strength = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    dexterity = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    constitution = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    intelligence = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    wisdom = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    charisma = serializers.IntegerField(min_value=1, max_value=30, error_messages=NUMBER_FIELD_ERROR_MESSAGES)

    pp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    gp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    sp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    cp = serializers.IntegerField(min_value=0, required=False, error_messages=NUMBER_FIELD_ERROR_MESSAGES)
    
    slot = serializers.SerializerMethodField()
    ability_modifiers = serializers.SerializerMethodField()
    proficiency_bonus = serializers.SerializerMethodField()
    max_hp = serializers.SerializerMethodField()
    hit_die_size = serializers.SerializerMethodField()
    max_hit_dice_count = serializers.SerializerMethodField()
    remaining_hit_dice = serializers.SerializerMethodField()
    armor_class = serializers.SerializerMethodField()
    xp_progress = serializers.SerializerMethodField()


    class Meta:
        model = Character
        fields = (
            "id",
            "slot",
            "name",
            "class_id",
            "race_id",
            "background_id",
            "alignment_id",
            "armor_id",
            "weapon_id",
            "skill_ids",
            "spell_ids",
            "character_class",
            "race",
            "background",
            "alignment",
            "armor",
            "weapon",
            "skills",
            "spells",
            "current_hp",
            "used_hit_dice",
            "level",
            "xp",
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
            "has_shield",
            "pp",
            "gp",
            "sp",
            "cp",
            "created_at",
            "ability_modifiers",
            "proficiency_bonus",
            "max_hp",
            "hit_die_size",
            "max_hit_dice_count",
            "remaining_hit_dice",
            "armor_class",
            "xp_progress",
        )
        read_only_fields = ("id", "slot", "level", "created_at")

    def get_skills(self, obj: Character):
        modifiers = ability_modifiers(obj)
        prof_bonus = proficiency_bonus(obj.level)
        selected_ids = set(obj.skills.values_list("id", flat=True))
        payload = []
        for skill in Skill.objects.order_by("name"):
            base = modifiers.get(skill.ability, 0)
            proficient = skill.id in selected_ids
            payload.append(
                {
                    "id": skill.id,
                    "name": skill.name,
                    "ability": skill.ability,
                    "proficient": proficient,
                    "bonus": base + (prof_bonus if proficient else 0),
                }
            )
        return payload

    def get_slot(self, obj: Character):
        return get_slot_for_character(obj)

    def get_ability_modifiers(self, obj: Character):
        return ability_modifiers(obj)

    def get_proficiency_bonus(self, obj: Character):
        return proficiency_bonus(obj.level)

    def get_max_hp(self, obj: Character):
        return calculate_max_hp(obj.level, obj.character_class.die_type, obj.constitution)

    def get_hit_die_size(self, obj: Character):
        return obj.character_class.die_type

    def get_max_hit_dice_count(self, obj: Character):
        return max_hit_dice_count(obj.level)

    def get_remaining_hit_dice(self, obj: Character):
        return remaining_hit_dice(obj)

    def get_armor_class(self, obj: Character):
        return armor_class(obj)

    def get_xp_progress(self, obj: Character):
        progress = xp_progress(obj.level, obj.xp)
        return {
            "current_level_xp": progress.current_level_xp,
            "next_level_xp": progress.next_level_xp,
            "progress_percent": progress.progress_percent,
        }

    def validate(self, attrs):
        instance = self.instance

        scores = [
            attrs.get(field, getattr(instance, field, None))
            for field in ABILITY_FIELDS
        ]
        if None not in scores and sorted(scores) != sorted(ALLOWED_ABILITY_SET):
            raise serializers.ValidationError(
                {"abilities": "invalid_ability_score_set"},
                code="invalid_ability_score_set",
            )

        xp_value = attrs.get("xp", getattr(instance, "xp", 0))
        level = calculate_level(xp_value)
        character_class = attrs.get("character_class", getattr(instance, "character_class", None))
        constitution = attrs.get("constitution", getattr(instance, "constitution", None))

        if character_class and constitution is not None:
            max_hp = calculate_max_hp(level, character_class.die_type, constitution)
            current_hp = attrs.get("current_hp", getattr(instance, "current_hp", None))
            if current_hp is not None and current_hp > max_hp:
                raise serializers.ValidationError({"current_hp": "current_hp_exceeds_max"})
            used_hit_dice = attrs.get("used_hit_dice", getattr(instance, "used_hit_dice", 0))
            if used_hit_dice > level:
                raise serializers.ValidationError({"used_hit_dice": "used_hit_dice_exceeds_level"})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        ensure_character_limit(request.user)
        skills = validated_data.pop("skills", [])
        spells = validated_data.pop("spells", [])
        character = Character(user=request.user, **validated_data)
        character.level = calculate_level(character.xp)
        max_hp = calculate_max_hp(character.level, character.character_class.die_type, character.constitution)
        if not character.current_hp:
            character.current_hp = max_hp
        character.used_hit_dice = min(character.used_hit_dice, character.level)
        character.save()
        if skills:
            character.skills.set(skills)
        if spells:
            character.spells.set(spells)
        return character

    @transaction.atomic
    def update(self, instance, validated_data):
        skills = validated_data.pop("skills", None)
        spells = validated_data.pop("spells", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.level = calculate_level(instance.xp)
        max_hp = calculate_max_hp(instance.level, instance.character_class.die_type, instance.constitution)
        instance.current_hp = min(instance.current_hp, max_hp)
        instance.used_hit_dice = min(instance.used_hit_dice, instance.level)
        instance.save()
        if skills is not None:
            instance.skills.set(skills)
        if spells is not None:
            instance.spells.set(spells)
        return instance

class ConfirmCharacterDeleteSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, error_messages=COMMON_FIELD_ERROR_MESSAGES)

    def validate_current_password(self, value):
        request = self.context["request"]
        if not request.user.check_password(value):
            raise serializers.ValidationError("current_password_incorrect", code="current_password_incorrect")
        return value

class AddXpSerializer(serializers.Serializer):
    amount = serializers.IntegerField(
        min_value=1,
        max_value=999999,
        error_messages=NUMBER_FIELD_ERROR_MESSAGES,
    )

class ShortRestSerializer(serializers.Serializer):
    spent_hit_dice = serializers.IntegerField(
        min_value=1,
        max_value=20,
        error_messages=NUMBER_FIELD_ERROR_MESSAGES,
    )
