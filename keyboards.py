from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from quiz_data import quiz_data

def generate_options_keyboard(answer_options, right_answer, question_index):
    builder = InlineKeyboardBuilder()

    for i, option in enumerate(answer_options):
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"answer_{question_index}_{i}_{1 if option == right_answer else 0}")
        )

    builder.adjust(1)
    return builder.as_markup()

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
