from modeltranslation.translator import register, TranslationOptions
from .models import Disease, Recommendation

@register(Disease)
class DiseaseTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'symptoms', 'causes', 'prevention', 'treatment', 'region',)

@register(Recommendation)
class RecommendationTranslationOptions(TranslationOptions):
    fields = ('text',)
