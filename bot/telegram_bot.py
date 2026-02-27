"""
PlantCare Telegram Bot
Foydalanuvchilar rasm yuborib o'simlik kasalliklarini tekshirishi mumkin
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from diagnosis.model_loader import predict_plant_disease
from diagnosis.ai_utils import get_ai_recommendation
from PIL import Image
import io

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    welcome_text = f"""
🌱 Assalomu alaykum, {user.first_name}!

PlantCare AI botiga xush kelibsiz! 

Men o'simlik kasalliklarini aniqlashda yordam beraman. Shunchaki o'simlik rasmini yuboring va men:
✅ Kasallikni aniqlayman
✅ Aniqlik darajasini ko'rsataman
✅ Davolash bo'yicha tavsiyalar beraman

📸 Rasm yuboring va boshlaymiz!

/help - Yordam
/about - Bot haqida
"""
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = """
📚 Qanday foydalanish kerak?

1. O'simlik rasmini yuboring (kasallangan joyini yaxshi ko'rinadigan qilib)
2. Bir necha soniya kuting
3. Natijani va tavsiyalarni oling

💡 Maslahatlar:
• Rasmni yorug' joyda oling
• O'simlikning kasallangan qismini yaqindan tushiring
• Aniq va sifatli rasm yuboring

⚠️ Qo'llab-quvvatlanadigan o'simliklar:
Pomidor, kartoshka, qalampir, uzum, olma va boshqalar

❓ Savollar bormi? @plantcare_support ga yozing
"""
    await update.message.reply_text(help_text)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About command handler"""
    about_text = """
🌿 PlantCare AI haqida

PlantCare - sun'iy intellekt asosida o'simlik kasalliklarini aniqlaydigan platforma.

🎯 Maqsadimiz:
Fermerlar va bog'bonlarga kasalliklarni erta bosqichda aniqlash va samarali davolash bo'yicha yordam berish.

🔬 Texnologiya:
• Deep Learning (TensorFlow)
• Google Gemini AI
• 38+ kasallik klassi
• 90%+ aniqlik

🌐 Website: https://plantcare.uz (demo)
📧 Support: support@plantcare.uz

© 2025 PlantCare AI
"""
    await update.message.reply_text(about_text)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages"""
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Rasm tahlil qilinmoqda, iltimos kuting...")
        
        # Get the photo
        photo = update.message.photo[-1]  # Get highest resolution
        file = await context.bot.get_file(photo.file_id)
        
        # Download photo to memory
        photo_bytes = await file.download_as_bytearray()
        image = Image.open(io.BytesIO(photo_bytes))
        
        # Save to temporary location
        temp_path = f"/tmp/telegram_{update.effective_user.id}_{photo.file_id}.jpg"
        image.save(temp_path)
        
        # Predict disease
        disease_name, confidence = predict_plant_disease(temp_path)
        
        # Delete processing message
        await processing_msg.delete()
        
        if disease_name and confidence:
            # Format confidence
            confidence_percent = confidence * 100
            
            # Confidence emoji
            if confidence_percent >= 80:
                conf_emoji = "✅"
            elif confidence_percent >= 60:
                conf_emoji = "⚠️"
            else:
                conf_emoji = "❓"
            
            # Get AI recommendation
            try:
                ai_recommendation = get_ai_recommendation(disease_name, lang='uz')
            except:
                ai_recommendation = "AI tavsiya olishda xatolik yuz berdi."
            
            # Format response
            response_text = f"""
🔍 **Tahlil natijalari:**

🌱 Kasallik: **{disease_name}**
{conf_emoji} Aniqlik: **{confidence_percent:.1f}%**

💊 **Tavsiyalar:**
{ai_recommendation[:800]}...

📊 Batafsil ma'lumot uchun: https://plantcare.uz
"""
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            await update.message.reply_text(
                "❌ Kasallik aniqlanmadi. Iltimos, aniqroq rasm yuboring yoki boshqa burchakdan oling."
            )
    
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        await update.message.reply_text(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring yoki @plantcare_support ga murojaat qiling."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text.lower()
    
    if any(word in text for word in ['salom', 'hello', 'assalomu', 'hi']):
        await update.message.reply_text(
            "👋 Assalomu alaykum! O'simlik rasmini yuboring va men kasallikni aniqlayman. /help - yordam uchun"
        )
    elif any(word in text for word in ['yordam', 'help', 'qanday']):
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "📸 Iltimos, o'simlik rasmini yuboring. Matn emas, rasm kerak.\n\n/help - ko'proq ma'lumot"
        )


def start_telegram_bot():
    """Initialize and start the Telegram bot"""
    try:
        # Get token from settings
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        
        if not token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN topilmadi. Bot ishga tushmaydi.")
            return None
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        logger.info("✅ Telegram bot ishga tushirildi!")
        
        return application
        
    except Exception as e:
        logger.error(f"❌ Telegram bot ishga tushmadi: {e}")
        return None


async def run_bot():
    """Run the bot in polling mode"""
    application = start_telegram_bot()
    if application:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("🤖 Telegram bot ishlayapti...")
