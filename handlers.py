import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import API_TOKEN
from database import *
from quiz_data import quiz_data
from keyboards import generate_options_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)

class QuizStates(StatesGroup):
    playing = State()

# Хэндлер на команду /start
async def cmd_start(message: types.Message):
    await message.answer(
        "Добро пожаловать в квиз по Python!\n\n"
        "Команды:\n"
        "/start - начать работу\n"
        "/quiz - начать квиз\n"
        "/stats - статистика\n"
        "Или используйте кнопки ниже:",
        reply_markup=get_main_keyboard()
    )

# Хэндлер на команду /stats
async def cmd_stats(message: types.Message):
    user_stats = await get_user_stats(message.from_user.id)
    
    if user_stats:
        last_score, total_played, last_played, all_score = user_stats
        await message.answer(
            f"Ваша статистика:\n"
            f"Последний результат: {last_score}/{len(quiz_data)}\n"
            f"Всего сыграно: {total_played} раз\n"
            f"Общий счет: {all_score} очков\n"
            f"Последняя игра: {last_played.split()[0]}"
        )
    else:
        await message.answer("Вы еще не играли в квиз! Начните игру с помощью /quiz")

# Хэндлер на команду /leaderboard
async def cmd_leaderboard(message: types.Message):
    all_stats = await get_all_stats()
    
    if not all_stats:
        await message.answer("Пока нет статистики игроков")
        return
    
    leaderboard_text = "Таблица лидеров (по общему счету):\n\n"
    for i, (username, last_score, total_played, last_played, all_score) in enumerate(all_stats[:10], 1):
        leaderboard_text += f"{i}. {username or 'Без имени'}: {all_score} очков (игр: {total_played})\n"
    
    await message.answer(leaderboard_text)

async def get_question(message, user_id):
    current_question_index = await get_quiz_index(user_id)
    question_data = quiz_data[current_question_index]
    
    correct_index = question_data['correct_option']
    opts = question_data['options']
    right_answer = opts[correct_index]
    
    kb = generate_options_keyboard(opts, right_answer, current_question_index)
    await message.answer(f"Вопрос {current_question_index + 1}/{len(quiz_data)}:\n\n{question_data['question']}", reply_markup=kb)

async def new_quiz(message):
    user_id = message.from_user.id
    await update_quiz_index(user_id, 0)
    await get_question(message, user_id)

# Начало квиза
async def cmd_quiz(message: types.Message):
    await message.answer("Начинаем")
    await new_quiz(message)
user_scores = {}

# Хэндлер для правильного ответа
async def process_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_question_index = await get_quiz_index(user_id)
    
    _, q_index, answer_index, is_correct = callback.data.split("_")
    q_index = int(q_index)
    answer_index = int(answer_index)
    is_correct = bool(int(is_correct))
    
    await callback.bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    
    # Отоброжения ответа
    selected_answer = quiz_data[q_index]['options'][answer_index]
    await callback.message.answer(f"Ваш ответ: {selected_answer}")
    
    if is_correct:
        if user_id not in user_scores:
            user_scores[user_id] = 0
        user_scores[user_id] += 1
        await callback.message.answer("Верно!")
    else:
        correct_answer = quiz_data[q_index]['options'][quiz_data[q_index]['correct_option']]
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")
    
    # Переход к следующему вопросу и завершение квиза
    current_question_index += 1
    await update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(quiz_data):
        await get_question(callback.message, user_id)
    else:
        score = user_scores.get(user_id, 0)
        username = callback.from_user.username or callback.from_user.first_name
        await save_quiz_result(user_id, username, score)
        user_stats = await get_user_stats(user_id)
        all_score = user_stats[3] if user_stats else score   
        if user_id in user_scores:
            del user_scores[user_id]
        await callback.message.answer(
            f"Квиз завершен!\n"
            f"Результат этой игры: {score}/{len(quiz_data)}\n"
            f"Ваш общий счет: {all_score} очков\n\n"
            f"Используйте /stats чтобы посмотреть полную статистику",
            reply_markup=get_main_keyboard()
        )
