from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

from reference_data.models import Alignment, Armor, Background, CharacterClass, Race, Skill, Spell, Weapon


# Create your models here.
class Character(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
    )
    name = models.CharField(max_length=50)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.PROTECT, related_name="characters")
    race = models.ForeignKey(Race, on_delete=models.PROTECT, related_name="characters")
    background = models.ForeignKey(Background, on_delete=models.PROTECT, related_name="characters")
    alignment = models.ForeignKey(Alignment, on_delete=models.PROTECT, related_name="characters")

    current_hp = models.PositiveIntegerField(default=0)
    used_hit_dice = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(20)])
    xp = models.PositiveIntegerField(default=0)

    strength = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    dexterity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    constitution = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    intelligence = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    wisdom = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])
    charisma = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(30)])

    has_shield = models.BooleanField(default=False)
    armor = models.ForeignKey(Armor, on_delete=models.PROTECT, related_name="characters")
    weapon = models.ForeignKey(Weapon, on_delete=models.PROTECT, related_name="characters")

    pp = models.PositiveIntegerField(default=0)
    gp = models.PositiveIntegerField(default=0)
    sp = models.PositiveIntegerField(default=0)
    cp = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    skills = models.ManyToManyField(Skill, through="CharacterSkill", related_name="characters", blank=True)
    spells = models.ManyToManyField(Spell, through="CharacterSpell", related_name="characters", blank=True)

    class Meta:
        ordering = ("created_at", "id")

    def __str__(self) -> str:
        return self.name


class CharacterSkill(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("character", "skill"), name="unique_character_skill"),
        ]


class CharacterSpell(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("character", "spell"), name="unique_character_spell"),
        ]
