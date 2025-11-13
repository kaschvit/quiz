import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from database import create_tables
from handlers import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_quiz, Command("quiz"))
dp.message.register(cmd_quiz, F.text == "Начать игру")
dp.message.register(cmd_stats, Command("stats"))
dp.message.register(cmd_stats, F.text == "Статистика")
dp.message.register(cmd_leaderboard, Command("leaderboard"))
dp.callback_query.register(process_answer, F.data.startswith("answer_"))

async def main():
    logger.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
