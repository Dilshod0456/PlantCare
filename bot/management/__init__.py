"""
Django management command to start Telegram bot
"""
from django.core.management.base import BaseCommand
import asyncio
from bot.telegram_bot import run_bot


class Command(BaseCommand):
    help = 'Start Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Telegram bot...'))
        
        try:
            # Run bot
            asyncio.run(run_bot())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('⏹️ Bot stopped by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
