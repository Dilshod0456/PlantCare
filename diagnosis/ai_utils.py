import os
import requests
from dotenv import load_dotenv
import bleach
import re

def markdown_formatter(text):
    """
    Markdown formatidagi matnni HTML ga aylantiradi va sanitizatsiya qiladi.
    """
    # Dozvoljen teglar va atributlar
    allowed_tags = ['p', 'b', 'i', 's', 'code', 'h1', 'h2', 'h3', 'a', 'ul', 'li']
    allowed_attributes = {'a': ['href']}

    # Formatlash qoidalari (tartib muhim!)
    rules = [
        (r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>'),  # Bold va italic
        (r'\*\*(.*?)\*\*', r'<b>\1</b>'),  # Bold
        (r'\*(.*?)\*', r'<i>\1</i>'),  # Italic
        (r'---(.*?)---', r'<s>\1</s>'),  # Strikethrough
        (r'`([^`]+)`', r'<code>\1</code>'),  # Inline code
        (r'\n# (.*?)(?=\n|$)', r'\n<h1>\1</h1>'),  # Sarlavha 1
        (r'\n## (.*?)(?=\n|$)', r'\n<h2>\1</h2>'),  # Sarlavha 2
        (r'\n### (.*?)(?=\n|$)', r'\n<h3>\1</h3>'),  # Sarlavha 3
        (r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>'),  # Havola
        (r'\n- (.*?)(?=\n|$)', r'\n<li>\1</li>'),  # Ro‘yxat elementi
        (r'</li>\n<li>', r'</li><li>'),  # Ro‘yxat elementlarini tozalash
        (r'(<li>.*?</li>)', r'<ul>\1</ul>')  # Ro‘yxatni ul tegi bilan o‘rash
    ]

    formatted_text = text.strip()

    # Har bir formatlash qoidasini qo‘llash
    for pattern, replacement in rules:
        formatted_text = re.sub(pattern, replacement, formatted_text, flags=re.DOTALL if pattern == r'(<li>.*?</li>)' else 0)

    # Paragraflarni saqlash uchun qator tashlashlar
    formatted_text = re.sub(r'\n\n+', '</p><p>', formatted_text)

    # Agar matn HTML teglari bilan boshlanmasa, uni p tegiga o‘rash
    if not re.match(r'^<(h[1-3]|ul|li|p)', formatted_text):
        formatted_text = f'<p>{formatted_text}</p>'

    # Ortiqcha bo‘sh paragraflarni olib tashlash
    formatted_text = re.sub(r'</p>\s*<p>\s*</p>', '', formatted_text)

    # HTML ni sanitizatsiya qilish
    formatted_text = bleach.clean(formatted_text, tags=allowed_tags, attributes=allowed_attributes)

    return formatted_text

# Google Generative AI import
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini AI
if GEMINI_API_KEY and GENAI_AVAILABLE:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Gemini AI configuration error: {e}")
        GENAI_AVAILABLE = False

def get_ai_recommendation(disease_name, lang='uz'):
    """
    GEMINI AI dan kasallik bo'yicha tavsiya olish
    """
    if not GEMINI_API_KEY:
        return "AI tavsiya xizmati hozircha mavjud emas. API kalit sozlanmagan."
    
    if not GENAI_AVAILABLE:
        return "Google Generative AI kutubxonasi mavjud emas. Iltimos, kutubxonani o'rnating."
    
    try:
        # Language-specific prompts
        prompts = {
            'uz': f"""
            {disease_name} kasalligi aniqlandi. 
            
            Iltimos, quyidagi ma'lumotlarni o'zbek tilida bering:
            1. Kasallik haqida qisqa ma'lumot
            2. Asosiy belgilar va alomatlar
            3. Kasallikning sabablari
            4. O'zbekistan sharoitida davolash usullari
            5. Oldini olish choralari
            6. Tavsiya etiladigan dori vositalari (agar mavjud bo'lsa)
            7. Qo'shimcha parvarish bo'yicha maslahatlar
            
            Javobni aniq va tushunarli tarzda yozing. O'zbekistan fermerlari uchun amaliy bo'lsin.
            """,
            'ru': f"""
            Обнаружена болезнь: {disease_name}
            
            Пожалуйста, предоставьте информацию на русском языке:
            1. Краткая информация о болезни
            2. Основные симптомы и признаки
            3. Причины заболевания
            4. Методы лечения в условиях Узбекистана
            5. Профилактические меры
            6. Рекомендуемые препараты (если имеются)
            7. Дополнительные советы по уходу
            
            Ответ должен быть практичным для фермеров Узбекистана.
            """,
            'en': f"""
            Disease detected: {disease_name}
            
            Please provide information in English:
            1. Brief information about the disease
            2. Main symptoms and signs
            3. Causes of the disease
            4. Treatment methods suitable for Uzbekistan conditions
            5. Prevention measures
            6. Recommended medications (if available)
            7. Additional care advice
            
            The answer should be practical for farmers in Uzbekistan.
            """
        }
        
        prompt = prompts.get(lang, prompts['uz'])
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Generate response
        response = model.generate_content(prompt)
        
        if response and response.text:
            return markdown_formatter(response.text.strip())
        else:
            return "AI javob bermadi. Iltimos, keyinroq urinib ko'ring."
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ AI xatolik: {error_msg}")
        
        # Agar quota tugagan bo'lsa yoki limit oshgan bo'lsa, fallback
        if any(word in error_msg.lower() for word in ["quota", "limit", "429", "rate"]):
            print("⚠️ Gemini API limiti tugagan, fallback rejimiga o'tilmoqda...")
            try:
                from .ai_utils_simple import get_ai_recommendation as fallback_recommendation
                return fallback_recommendation(disease_name, lang)
            except:
                pass
        
        return f"AI tavsiya olishda vaqtincha xatolik. Iltimos, keyinroq qayta urinib ko'ring."

def chat_with_ai(question, lang='uz'):
    """
    AI bilan chat uchun
    """
    if not GEMINI_API_KEY:
        return "AI chat xizmati hozircha mavjud emas. API kalit sozlanmagan."
    
    if not GENAI_AVAILABLE:
        return "Google Generative AI kutubxonasi mavjud emas. Iltimos, kutubxonani o'rnating."
    
    try:
        # Language-specific system prompts
        system_prompts = {
            'uz': "Siz o'simlik kasalliklari bo'yicha mutaxassis AI yordamchisiz. O'zbekiston fermerlari va bog'bonlariga yordam berasiz. Javoblarni o'zbek tilida, aniq va amaliy bering.",
            'ru': "Вы AI-помощник по болезням растений. Помогаете фермерам и садоводам Узбекистана. Отвечайте на русском языке, точно и практично.",
            'en': "You are an AI assistant specializing in plant diseases. You help farmers and gardeners in Uzbekistan. Answer in English, accurately and practically."
        }
        
        system_prompt = system_prompts.get(lang, system_prompts['uz'])
        full_prompt = f"{system_prompt}\n\nSavol: {question}"
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return "AI javob bermadi. Iltimos, savolingizni boshqacha tarzda bering."
            
    except Exception as e:
        error_str = str(e).lower()
        # Check if error is related to quota/rate limit
        if any(keyword in error_str for keyword in ['quota', 'limit', '429', 'rate']):
            from .ai_utils_simple import chat_with_ai as fallback_chat
            print("⚠️ Gemini API limiti tugagan (chat), fallback rejimiga o'tilmoqda...")
            return fallback_chat(question, lang)
        
        print(f"❌ Gemini chat xatolik: {str(e)}")
        return "AI javob bermadi. Iltimos, keyinroq qayta urinib ko'ring."
