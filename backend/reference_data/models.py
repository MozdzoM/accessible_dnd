from django.db import models


# Create your models here.
class NamedModel(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

class CharacterClass(NamedModel):
    die_type = models.PositiveSmallIntegerField()

class Race(NamedModel):
    pass

class Background(NamedModel):
    pass

class Alignment(NamedModel):
    pass

class Armor(NamedModel):
    class DexMode(models.TextChoices):
        FULL = "full", "Full"
        CAP = "cap", "Cap"
        NONE = "none", "None"

    armor_bonus = models.PositiveSmallIntegerField(default=0)
    dex_mode = models.CharField(max_length=10, choices=DexMode.choices, default=DexMode.FULL)
    dex_cap = models.PositiveSmallIntegerField(blank=True, null=True)

class Weapon(NamedModel):
    die_count = models.PositiveSmallIntegerField(default=1)
    die_type = models.PositiveSmallIntegerField(default=4)

class Skill(NamedModel):
    ability = models.CharField(max_length=20)

class Spell(NamedModel):
    spell_level = models.PositiveSmallIntegerField(default=0)