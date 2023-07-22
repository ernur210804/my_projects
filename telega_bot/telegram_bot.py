from typing import Final
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
import aiosqlite

import sqlite3

# подключения к БД
db = sqlite3.connect('tg_db.db')
c = db.cursor()

#для создания таблицы
# c.execute("""CREATE TABLE tasks (
#     task text,
#     done text)""")


#для заполнения таблицы вручную
#c.execute("INSERT INTO tasks VALUES ('lunch2', 'no')")
#db.commit()

# Telegram Bot API token и username
TOKEN: Final = '5867327086:AAGc2yE3MzQ9u6Zu8Q-1AI9yRN6Uqef9gHI'
BOT_USERNAME: Final = '@Ukitaka_bot'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Комманды от клавиш
keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("/add"),
                                                            KeyboardButton("/view"),
                                                            KeyboardButton("/done"),
                                                            KeyboardButton("/delete"))

# Command handlers
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Здравствуйте! Спасибо что выбрали меня. Меня зовут Ukitaka! \n /add-добавляет задание. Для добавления пишите (/add+ваше задание) \n /done-пометка выполнения задания. Для выполнения пишите (/done+id) \n /delete-Очистка списка. Для очистки пишите(/delete+all) \n /view-просмотр списка. Для просмотра списка пишите(/view)')

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Меня зовут Ukitaka! Чем я могу вам помочь?')

@dp.message_handler(commands=['custom'])
async def custom_command(message: types.Message):
    await bot.send_message(message.chat.id, 'Здравствуйте! Спасибо что выбрали меня. Меня зовут Ukitaka!')

# Ответы на handling
def handle_response(text: str) -> str:
    processed: str = text.lower()
    if '/view' in processed:
        c.execute("SELECT rowid,task,done FROM tasks")
        tasks = c.fetchall()
        response=''
        for el in tasks:
            response += f"Id: {str(el[0])}, Task: {el[1]}, Done: {el[2]} \n"
            
        if response == '':
            return 'To do list is empty!'
        else:
            return response
        
    if 'help' in processed:
        return 'how can i help you?'
    return 'I cannot understand you'

# Добавление task-ов
@dp.message_handler(commands=['add'])
async def add_task(message: types.Message):
    task_text = message.text.replace('/add', '').strip()  # получения  TASK-ов из текста 
    if task_text:
        async with aiosqlite.connect('tg_db.db') as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("INSERT INTO tasks (task, done) VALUES (?, ?)", (task_text, 'no')):
                await db.commit()
        await message.answer(f"Task '{task_text}' added.", reply_markup=keyboard)
    else:
        await message.answer("Please provide a task description after the /add command.",
                             reply_markup=ReplyKeyboardRemove())

     
c.execute("SELECT COUNT(*) FROM tasks")
row_count = c.fetchone()[0]     #Кол-во строк в бд
     
# Done task
@dp.message_handler(commands=['done'])
async def done_task(message: types.Message):
    task_text = message.text.split('/done', 1)[-1].strip() 
    
    
    
   
        
    if task_text:
        c.execute("UPDATE tasks SET done = ? WHERE rowid = ?", ('yes', task_text))
        db.commit()

        await message.answer(f"Task '{task_text}' is marked as done.", reply_markup=keyboard)
    
    else:
        await message.answer("Please provide a task description after the /done command.",
                             reply_markup=ReplyKeyboardRemove())
    
        
    


# DELETE task
@dp.message_handler(commands=['delete'])
async def done_task(message: types.Message):
    task_text = message.text.split('/delete', 1)[-1].strip()  
    if task_text=='all':
        c.execute("DELETE  FROM tasks ")
        db.commit()
       
        await message.answer(f"Delete '{task_text}' is marked as done.", reply_markup=keyboard)
    else:
        await message.answer("Please provide a task description after the /delete command.",
                             reply_markup=ReplyKeyboardRemove())



# Handling для ответов пользователя
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_message(message: types.Message):
    message_type: str = message.chat.type
    text: str = message.text

    print(f"User ({message.chat.id}) in ({message_type}): '({text})' ")

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)

    await bot.send_message(message.chat.id, response)  

# Error handling
async def on_error(update: types.Update, exception: Exception):
    print(f'Update {update} caused error {exception}')

if __name__ == '__main__':
    dp.register_errors_handler(on_error)
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
