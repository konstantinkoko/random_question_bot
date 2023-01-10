
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from question_box import QuestionBox
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
question_box = QuestionBox()

start_keyboard = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Задай мне парочку вопросов!", callback_data="ask me"))

def get_answer_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Ответ", callback_data=callback_data))


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message) -> None:
    await message.answer("Привет! Хочешь парочку вопросов?", reply_markup=start_keyboard)
    question_box.add_user(message.from_user.id, message.from_user.first_name, message.chat.id, True)

@dp.callback_query_handler(text="ask me")
async def ask_me(callback: types.CallbackQuery, state: FSMContext) -> None:
    question_list = question_box.get_questions(callback.from_user.id)
    data = await state.get_data()
    if "counter" not in data.keys():
        question_counter = 0
    else:
        question_counter = data["counter"] if data["counter"] < 98 else 0
    for question in question_list:
        question_counter += 1
        question_data = {"answer_" + str(question_counter) : {
            "answer" : question["answer"],
            "comment" : question["comment"]
            }
        }
        await state.update_data(data=question_data)
        await callback.message.answer(question["question"], reply_markup=get_answer_keyboard("answer_" + str(question_counter)))
    await state.update_data({"counter" : question_counter})
    await callback.message.answer("-------------------------------", reply_markup=start_keyboard)
    await callback.answer()

@dp.callback_query_handler(Text(startswith="answer_"))
async def get_answer(callback: types.CallbackQuery,  state: FSMContext) -> None:
    data = await state.get_data()
    answer = data[callback.data]
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(callback.message.text + '\n\n\n' + answer["answer"] + '\n\n\n' + answer["comment"])
    await callback.answer()

if __name__ == '__main__':
    executor.start_polling(dp)