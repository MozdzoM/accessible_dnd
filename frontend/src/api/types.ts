export interface UserSettings {
  language: "pl" | "en";
  theme: "light" | "dark";
  font_size: "small" | "medium" | "large" | "xlarge";
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  settings: UserSettings;
}

export type AbilityName = "strength" | "dexterity" | "constitution" | "intelligence" | "wisdom" | "charisma";

export interface NamedReference {
  id: number;
  name: string;
}

export interface CharacterClass extends NamedReference {
  die_type: number;
}

export interface Armor extends NamedReference {
  armor_bonus: number;
  dex_mode: "full" | "cap" | "none";
  dex_cap: number | null;
}

export interface Weapon extends NamedReference {
  die_count: number;
  die_type: number;
}

export interface SkillReference extends NamedReference {
  ability: AbilityName;
}

export interface SpellReferece extends NamedReference {
  spell_level: number;
}

export interface ReferenceData {
  classes: CharacterClass[];
  races: NamedReference[];
  backgrounds: NamedReference[];
  alignments: NamedReference[];
  armors: Armor[];
  weapons: Weapon[];
  skills: SkillReference[];
  spells: SpellReferece[];
}

export interface CharacterSkill extends SkillReference {
  proficient: boolean;
  bonus: number;
}

export interface XpProgress {
  current_level_xp: number;
  next_level_xp: number | null;
  progress_percent: number;
}

export interface Character {
  id: number;
  slot: number;
  name: string;
  character_class: CharacterClass;
  race: NamedReference;
  background: NamedReference;
  alignment: NamedReference;
  armor: Armor;
  weapon: Weapon;
  skills: CharacterSkill[];
  spells: SpellReferece[];
  current_hp: number;
  used_hit_dice: number;
  level: number;
  xp: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  has_shield: boolean;
  pp: number;
  gp: number;
  sp: number;
  cp: number;
  ability_modifiers: Record<AbilityName, number>;
  proficiency_bonus: number;
  max_hp: number;
  hit_die_size: number;
  max_hit_dice_count: number;
  remaining_hit_dice: number;
  armor_class: number;
  xp_progress: XpProgress;
}

export interface CharacterPayload {
  name: string;
  class_id: number;
  race_id: number;
  background_id: number;
  alignment_id: number;
  armor_id: number;
  weapon_id: number;
  skill_ids: number[];
  spell_ids: number[];
  current_hp?: number;
  used_hit_dice?: number;
  xp: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  has_shield: boolean;
  pp: number;
  gp: number;
  sp: number;
  cp: number;
}

export interface AuthResponse {
  access: string;
  user: User;
}

export interface ApiErrorCodeDetail {
  code: string;
  [key: string]: unknown;
}

export type ApiErrorValue = string | ApiErrorCodeDetail | Array<string | ApiErrorCodeDetail> | undefined;

export interface ApiFieldErrors {
  [key: string]: ApiErrorValue;
}
