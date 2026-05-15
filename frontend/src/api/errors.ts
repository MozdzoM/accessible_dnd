export type ApiErrorLanguage = "pl" | "en";

export interface ApiErrorCodeObject {
  code: string;
  [key: string]: unknown;
}

const apiErrorMessages: Record<ApiErrorLanguage, Record<string, string>> = {
  pl: {
    account_inactive: "To konto jest nieaktywne.",
    invalid_choice: "Wybierz jedną z dostępnych opcji.",
    invalid_credentials: "Nieprawidłowy login lub hasło.",
    invalid_email: "Podaj poprawny adres e-mail.",
    invalid_reference: "Wybrana wartość nie istnieje.",
    invalid_refresh_token: "Sesja wygasła. Zaloguj się ponownie.",
    missing_refresh_token: "Brakuje tokenu odświeżania. Zaloguj się ponownie.",
    username_taken: "Ta nazwa użytkownika jest już zajęta.",
    email_taken: "Ten adres e-mail jest już zajęty.",
    passwords_do_not_match: "Hasła muszą być takie same.",
    new_password_confirmation_mismatch: "Potwierdzenie nowego hasła musi być takie samo.",
    new_password_required: "Podaj nowe hasło.",
    current_password_incorrect: "Aktualne hasło jest nieprawidłowe.",
    current_password_required: "Podaj aktualne hasło.",
    slot_empty: "Ten slot nie zawiera jeszcze postaci.",
    slot_not_found: "Taki slot nie istnieje.",
    character_limit_reached: "Osiągnięto limit 4 postaci.",
    invalid_ability_score_set: "Atrybuty muszą zawierać dokładnie wartości: 15, 14, 13, 12, 10, 8.",
    used_hit_dice_exceeds_level: "Zużyte kości życia nie mogą przekraczać poziomu postaci.",
    not_enough_hit_dice: "Nie masz wystarczająco dostępnych kości.",
    current_hp_exceeds_max: "Aktualne HP nie może przekraczać maksymalnego HP.",
    max_length: "Wartość jest za długa.",
    max_value: "Wartość jest za duża.",
    min_length: "Wartość jest za krótka.",
    min_value: "Wartość jest za mała.",
    required: "To pole jest wymagane.",
    blank: "To pole nie może być puste.",
    invalid: "Wartość jest nieprawidłowa.",
    request_failed: "Nie udało się wykonać operacji.",
},
en: {
    account_inactive: "This account is inactive.",
    invalid_choice: "Choose one of the available options.",
    invalid_credentials: "Invalid username or password.",
    invalid_email: "Enter a valid email address.",
    invalid_reference: "The selected value does not exist.",
    invalid_refresh_token: "The session expired. Log in again.",
    missing_refresh_token: "Refresh token is missing. Log in again.",
    username_taken: "This username is already taken.",
    email_taken: "This email address is already taken.",
    passwords_do_not_match: "Passwords must match.",
    new_password_confirmation_mismatch: "New password confirmation must match.",
    new_password_required: "Enter a new password.",
    current_password_incorrect: "Current password is incorrect.",
    current_password_required: "Enter your current password.",
    slot_empty: "This slot does not contain a character yet.",
    slot_not_found: "This slot does not exist.",
    character_limit_reached: "You've reached 4 characters limit.",
    invalid_ability_score_set: "Ability scores must be exactly: 15, 14, 13, 12, 10, 8.",
    used_hit_dice_exceeds_level: "Used hit dice cannot exceed character level.",
    not_enough_hit_dice: "You do not have enough hit dice remaining.",
    current_hp_exceeds_max: "Current HP cannot exceed max HP.",
    max_length: "The value is too long.",
    max_value: "The value is too high.",
    min_length: "The value is too short.",
    min_value: "The value is too low.",
    required: "This field is required.",
    blank: "This field may not be blank.",
    invalid: "The value is invalid.",
    request_failed: "The operation could not be completed.",
  },
};

export function getApiErrorCode(value: unknown): string | null {
  if (typeof value === "string") {
    return value;
  }
  if (Array.isArray(value)) {
    return getApiErrorCode(value[0]);
  }
  if (typeof value === "object" && value && "code" in value) {
    const code = (value as ApiErrorCodeObject).code;
    return typeof code === "string" ? code : null;
  }
  return null;
}

export function translateApiError(language: ApiErrorLanguage, value: unknown): string {
  const code = getApiErrorCode(value);
  if (!code) {
    return apiErrorMessages[language].request_failed;
  }
  return apiErrorMessages[language][code] ?? apiErrorMessages.en[code] ?? code;
}
