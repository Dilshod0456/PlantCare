import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def get_ai_recommendation(disease_name, lang='uz'):
    """
    AI dan kasallik bo'yicha tavsiya olish (Fallback versiya)
    """
    if not GEMINI_API_KEY:
        return "AI tavsiya xizmati hozircha mavjud emas. API kalit sozlanmagan."
    
    # Fallback responses based on language
    responses = {
        'uz': f"""
🌱 {disease_name} kasalligi aniqlandi.

🔍 Asosiy belgilar:
- Barglar rangining o'zgarishi
- O'simlikning zaiflashishi
- Meva yoki barglarning dog'lanishi

⚡ Sabablari:
- Noto'g'ri parvarish
- Sug'orish rejimining buzilishi
- Havoning yuqori namligi

💊 Davolash usullari:
- Kasallangan qismlarni olib tashlash
- Fungitsid preparatlar bilan ishlov berish
- Sug'orish rejimini o'zgartirish

🛡️ Oldini olish:
- Muntazam tekshirish
- To'g'ri sug'orish
- O'simliklar orasida masofa saqlash

Batafsil ma'lumot uchun agronome bilan maslahatlashing.
        """,
        'ru': f"""
🌱 Обнаружена болезнь: {disease_name}

🔍 Основные симптомы:
- Изменение цвета листьев
- Ослабление растения
- Пятнистость на плодах или листьях

⚡ Причины:
- Неправильный уход
- Нарушение режима полива
- Высокая влажность воздуха

💊 Методы лечения:
- Удаление пораженных частей
- Обработка фунгицидами
- Корректировка режима полива

🛡️ Профилактика:
- Регулярный осмотр
- Правильный полив
- Соблюдение расстояния между растениями

Для подробной информации обратитесь к агроному.
        """,
        'en': f"""
🌱 Disease detected: {disease_name}

🔍 Main symptoms:
- Change in leaf color
- Plant weakening
- Spots on fruits or leaves

⚡ Causes:
- Improper care
- Irrigation regime violation
- High air humidity

💊 Treatment methods:
- Remove affected parts
- Fungicide treatment
- Adjust watering schedule

🛡️ Prevention:
- Regular inspection
- Proper watering
- Maintain distance between plants

For detailed information, consult an agronomist.
        """
    }
    
    return responses.get(lang, responses['uz'])

def chat_with_ai(question, lang='uz'):
    """
    AI bilan chat uchun (Fallback versiya)
    """
    if not GEMINI_API_KEY:
        return "AI chat xizmati hozircha mavjud emas. API kalit sozlanmagan."
    
    # Simple responses based on keywords
    responses = {
        'uz': {
            'kasallik': "O'simlik kasalliklari ko'p hollarda noto'g'ri parvarish natijasida yuzaga keladi. Asosiy sabablari: ortiqcha yoki kam sug'orish, noto'g'ri tuproq, harorat o'zgarishi.",
            'davolash': "Kasalliklarni davolash uchun avval kasallangan qismlarni olib tashlang, keyin tegishli dori vositalari bilan ishlov bering.",
            'sug\'orish': "Sug'orish rejimi o'simlik turiga qarab belgilanadi. Odatda haftada 2-3 marta etarli.",
            'o\'g\'it': "O'g'itlar o'simlikning o'sish davrida beriladi. Organik va mineral o'g'itlarni almashinuvchi ishlatish tavsiya etiladi."
        }
    }
    
    question_lower = question.lower()
    lang_responses = responses.get(lang, responses['uz'])
    
    for keyword, response in lang_responses.items():
        if keyword in question_lower:
            return response
    
    return "Savolingiz aniq emas. Iltimos, o'simlik kasalliklari, davolash, sug'orish yoki o'g'itlash haqida aniqroq savol bering."
