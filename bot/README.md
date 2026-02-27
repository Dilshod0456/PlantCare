# PlantCare Telegram Bot

## Sozlash

### 1. Telegram Bot yaratish

1. Telegram'da @BotFather ga murojaat qiling
2. `/newbot` buyrug'ini yuboring
3. Bot nomi va username kiriting
4. Token oling (masalan: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Token sozlash

`.env` fayliga token qo'shing:
```env
TELEGRAM_BOT_TOKEN=sizning_token_bu_yerda
```

### 3. Botni ishga tushirish

#### Usul 1: Django management command
```bash
python manage.py start_bot
```

#### Usul 2: Alohida terminal oynasida
```bash
# Terminal 1 - Django server
python manage.py runserver

# Terminal 2 - Telegram bot
python manage.py start_bot
```

## Xususiyatlar

✅ **Rasm tahlili** - Foydalanuvchi o'simlik rasmini yuboradi, bot kasallikni aniqlaydi
✅ **AI tavsiyalar** - Gemini AI dan davolash bo'yicha tavsiyalar
✅ **Aniqlik ko'rsatkichi** - Model ishonchlilik darajasi
✅ **Ko'p til** - O'zbek tilida javoblar

## Buyruqlar

- `/start` - Botni boshlash
- `/help` - Yordam
- `/about` - Bot haqida ma'lumot

## Qo'llab-quvvatlanadigan formatlar

- JPG, JPEG, PNG rasmlar
- Maksimal hajm: Telegram limiti (20MB)

## Xatoliklar

### Bot ishlamayapti
1. `TELEGRAM_BOT_TOKEN` to'g'ri o'rnatilganini tekshiring
2. Internet bor ekanligini tekshiring
3. Loglarni ko'ring: `python manage.py start_bot`

### Rasm tahlil qilinmayapti
1. TensorFlow model yuklanganini tekshiring
2. Rasm formatini tekshiring
3. Gemini API ishlab turganini tekshiring

## Deployment

### Production uchun
Bot va Django serverni alohida servislarda ishlatish tavsiya etiladi:

```bash
# systemd service yarating
sudo nano /etc/systemd/system/plantcare-bot.service
```

```ini
[Unit]
Description=PlantCare Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/PlantCare
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python manage.py start_bot
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable plantcare-bot
sudo systemctl start plantcare-bot
```

## API limitlari

- Gemini API: 60 so'rov/minut (free tier)
- Telegram: 30 xabar/soniya

## Support

📧 Email: support@plantcare.uz
💬 Telegram: @plantcare_support
