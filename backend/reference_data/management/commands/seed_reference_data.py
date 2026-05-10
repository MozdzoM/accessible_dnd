from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from reference_data.models import Alignment, Armor, Background, CharacterClass, Race, Skill, Spell, Weapon


REFERENCE_CLASSES = [
    {"name": "Barbarian", "die_type": 12},
    {"name": "Cleric", "die_type": 8},
    {"name": "Fighter", "die_type": 10},
    {"name": "Rogue", "die_type": 8},
    {"name": "Wizard", "die_type": 6},
]
REFERENCE_RACES = ["Dwarf", "Elf", "Halfling", "Human", "Tiefling"]
REFERENCE_BACKGROUNDS = ["Acolyte", "Criminal", "Entertainer", "Scholar", "Soldier"]
REFERENCE_ALIGNMENTS = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil",
]
REFERENCE_ARMORS = [
    {"name": "None", "armor_bonus": 0, "dex_mode": Armor.DexMode.FULL, "dex_cap": None},
    {"name": "Light", "armor_bonus": 1, "dex_mode": Armor.DexMode.FULL, "dex_cap": None},
    {"name": "Medium", "armor_bonus": 3, "dex_mode": Armor.DexMode.CAP, "dex_cap": 2},
    {"name": "Heavy", "armor_bonus": 6, "dex_mode": Armor.DexMode.NONE, "dex_cap": None},
]
REFERENCE_WEAPONS = [
    {"name": "Club", "die_count": 1, "die_type": 4},
    {"name": "Crossbow", "die_count": 1, "die_type": 8},
    {"name": "Dagger", "die_count": 1, "die_type": 4},
    {"name": "Fists", "die_count": 1, "die_type": 1},
    {"name": "Greataxe", "die_count": 1, "die_type": 12},
    {"name": "Handaxe", "die_count": 1, "die_type": 6},
    {"name": "Longbow", "die_count": 1, "die_type": 8},
    {"name": "Longsword", "die_count": 1, "die_type": 8},
    {"name": "Rapier", "die_count": 1, "die_type": 8},
    {"name": "Shortbow", "die_count": 1, "die_type": 6},
    {"name": "Shortsword", "die_count": 1, "die_type": 6},
    {"name": "Spear", "die_count": 1, "die_type": 6},
    {"name": "Warhammer", "die_count": 1, "die_type": 8},
]

REFERENCE_SKILLS = [
    ("Acrobatics", "dexterity"),
    ("Animal Handling", "wisdom"),
    ("Arcana", "intelligence"),
    ("Athletics", "strength"),
    ("Deception", "charisma"),
    ("History", "intelligence"),
    ("Insight", "wisdom"),
    ("Intimidation", "charisma"),
    ("Investigation", "intelligence"),
    ("Medicine", "wisdom"),
    ("Nature", "intelligence"),
    ("Perception", "wisdom"),
    ("Performance", "charisma"),
    ("Persuasion", "charisma"),
    ("Religion", "intelligence"),
    ("Sleight of Hand", "dexterity"),
    ("Stealth", "dexterity"),
    ("Survival", "wisdom"),
]
REFERENCE_SPELLS = [
    {"name": "Chill Touch", "spell_level": 0},
    {"name": "Fire Bolt", "spell_level": 0},
    {"name": "Mending", "spell_level": 0},
    {"name": "Mage Hand", "spell_level": 0},
    {"name": "Healing Word", "spell_level": 1},
    {"name": "Magic Missile", "spell_level": 1},
    {"name": "Misty Step", "spell_level": 2},
    {"name": "Fireball", "spell_level": 3},
]


class Command(BaseCommand):
    help = "Przykładowe dane dla aplikacji D&D" \
        "Seed reference data for the D&D app."

    def add_arguments(self, parser):
        parser.add_argument("--with-demo", action="store_true", help="Create a demo user and sample character.")

    def handle(self, *args, **options):
        for row in REFERENCE_CLASSES:
            CharacterClass.objects.update_or_create(name=row["name"], defaults=row)

        for name in REFERENCE_RACES:
            Race.objects.update_or_create(name=name, defaults={"name": name})

        for name in REFERENCE_BACKGROUNDS:
            Background.objects.update_or_create(name=name, defaults={"name": name})

        for name in REFERENCE_ALIGNMENTS:
            Alignment.objects.update_or_create(name=name, defaults={"name": name})

        for row in REFERENCE_ARMORS:
            Armor.objects.update_or_create(name=row["name"], defaults=row)

        for row in REFERENCE_WEAPONS:
            Weapon.objects.update_or_create(name=row["name"], defaults=row)

        for name, ability in REFERENCE_SKILLS:
            Skill.objects.update_or_create(name=name, defaults={"name": name, "ability": ability})

        for row in REFERENCE_SPELLS:
            Spell.objects.update_or_create(name=row["name"], defaults=row)

        self.stdout.write(self.style.SUCCESS("Reference data seeded."))

        if options["with_demo"]:
            self._create_demo_user()

    def _create_demo_user(self):
        User = get_user_model()
        demo_user, created = User.objects.get_or_create(
            username="MozdzoM",
            defaults={"email": "mozdzom@test.pl", "is_active": True},
        )
        if created or not demo_user.check_password("Password1!"):
            demo_user.set_password("Password1!")
            demo_user.save()

        from characters.models import Character

        if Character.objects.filter(user=demo_user).exists():
            self.stdout.write("Demo user already has a character.")
            return

        Character.objects.create(
            user=demo_user,
            name="Europa",
            character_class=CharacterClass.objects.get(name="Wizard"),
            race=Race.objects.get(name="Elf"),
            background=Background.objects.get(name="Scholar"),
            alignment=Alignment.objects.get(name="Neutral Good"),
            current_hp=8,
            used_hit_dice=0,
            xp=300,
            level=2,
            strength=8,
            dexterity=14,
            constitution=12,
            intelligence=15,
            wisdom=13,
            charisma=10,
            has_shield=False,
            armor=Armor.objects.get(name="None"),
            weapon=Weapon.objects.get(name="Dagger"),
            pp=0,
            gp=15,
            sp=10,
            cp=5,
        )
        self.stdout.write(self.style.SUCCESS("Demo user created: MozdzoM / Password1!"))
        