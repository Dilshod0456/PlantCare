# Django settings for modeltranslation
MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz'
MODELTRANSLATION_LANGUAGES = ('uz', 'ru', 'en')
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('uz', 'ru', 'en'),
    'uz': ('ru', 'en'),
    'ru': ('uz', 'en'),
    'en': ('uz', 'ru'),
}
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'uz'
