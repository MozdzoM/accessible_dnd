from dataclasses import dataclass
from rest_framework.exceptions import NotFound, ValidationError
from reference_data.models import Armor

from .constants import (
    ABILITY_FIELDS,
    BASE_AC,
    MAX_CHARACTERS_PER_USER,
    MAX_LEVEL,
    SHIELD_AC_BONUS,
    XP_THRESHOLDS,
)
from .models import Character


@dataclass
class XpProgress:
    current_level_xp: int
    next_level_xp: int | None
    progress_percent: int


def calculate_level(xp: int) -> int:
    level = 1
    for index, threshold in enumerate(XP_THRESHOLDS, start=1):
        if xp >= threshold:
            level = index
    return min(level, MAX_LEVEL)

def xp_progress(level: int, xp: int) -> XpProgress:
    current_threshold = XP_THRESHOLDS[level - 1]
    if level >= MAX_LEVEL:
        return XpProgress(current_threshold, None, 100)
    next_threshold = XP_THRESHOLDS[level]
    span = next_threshold - current_threshold
    progress = xp - current_threshold
    percent = 0 if span == 0 else round((progress / span) * 100)
    return XpProgress(current_threshold, next_threshold, max(0, min(percent, 100)))

def proficiency_bonus(level: int) -> int:
    return 2 + ((max(level, 1) - 1) // 4)

def ability_modifier(score: int) -> int:
    return (score - 10) // 2

def ability_modifiers(character: Character) -> dict[str, int]:
    return {field: ability_modifier(getattr(character, field)) for field in ABILITY_FIELDS}

def hit_die_average(die_type: int) -> int:
    return (die_type // 2) + 1

def calculate_max_hp(level: int, die_type: int, constitution_score: int) -> int:
    constitution_mod = ability_modifier(constitution_score)
    first_level = max(1, die_type + constitution_mod)
    if level == 1:
        return first_level
    per_level_gain = max(1, hit_die_average(die_type) + constitution_mod)
    return first_level + (per_level_gain * (level - 1))

def max_hit_dice_count(level: int) -> int:
    return level

def remaining_hit_dice(character: Character) -> int:
    return max(max_hit_dice_count(character.level) - character.used_hit_dice, 0)

def armor_class(character: Character) -> int:
    dex_mod = ability_modifier(character.dexterity)
    armor = character.armor
    if armor.dex_mode == Armor.DexMode.FULL:
        dex_bonus = dex_mod
    elif armor.dex_mode == Armor.DexMode.CAP:
        dex_bonus = min(dex_mod, armor.dex_cap or 0)
    else:
        dex_bonus = 0
    shield_bonus = SHIELD_AC_BONUS if character.has_shield else 0
    return BASE_AC + armor.armor_bonus + dex_bonus + shield_bonus

def serialize_skill_bonuses(character: Character) -> list[dict]:
    modifiers = ability_modifiers(character)
    prof_bonus = proficiency_bonus(character.level)
    proficient_ids = set(character.skills.values_list("id", flat=True))
    bonuses = []
    for skill in character.skills.model.objects.order_by("name"):
        base_value = modifiers.get(skill.ability, 0)
        proficient = skill.id in proficient_ids
        bonuses.append(
            {
                "id": skill.id,
                "name": skill.name,
                "ability": skill.ability,
                "proficient": proficient,
                "bonus": base_value + (prof_bonus if proficient else 0),
            }
        )
    return bonuses

def ordered_character_queryset(user):
    return Character.objects.filter(user=user).select_related(
        "character_class",
        "race",
        "background",
        "alignment",
        "armor",
        "weapon",
    ).prefetch_related("skills", "spells").order_by("created_at", "id")

def get_character_for_slot(user, slot: int) -> Character:
    if slot < 1 or slot > MAX_CHARACTERS_PER_USER:
        raise NotFound("slot_not_found", code="slot_not_found")
    characters = list(ordered_character_queryset(user))
    try:
        return characters[slot - 1]
    except IndexError as exc:
        raise NotFound("slot_empty", code="slot_empty") from exc

def get_slot_for_character(character: Character) -> int | None:
    characters = list(ordered_character_queryset(character.user).values_list("id", flat=True))
    try:
        return characters.index(character.id) + 1
    except ValueError:
        return None

def ensure_character_limit(user) -> None:
    if Character.objects.filter(user=user).count() >= MAX_CHARACTERS_PER_USER:
        raise ValidationError({"detail": "character_limit_reached"}, code="character_limit_reached")
