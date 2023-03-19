import os
import re
import traceback
import time
import requests
import configparser
import sqlite3
import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import BoundFilter
from cfg import token
import keyboard as kb

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
connection = sqlite3.connect('data.db')
q = connection.cursor()

class sender(StatesGroup):
    text = State()

class st(StatesGroup):
	item = State()
	item2 = State()
	item3 = State()
	item4 = State()

class bllist(StatesGroup):
    add = State()
    remove = State()

class Rass(StatesGroup):
  post = State()
  kb = State()
  time = State()

if not os.path.exists('audio'):
	os.makedirs('audio')

admin = 837817771

def join(user):
    q.execute(f"SELECT * FROM users WHERE user_id = {user.id}")
    result = q.fetchall()
    if len(result) == 0:
        q.execute("INSERT INTO `users` (`user_id`, `user_name`, `user_username`, `block`) VALUES (?, ?, ?, ?)", (user.id, user.full_name, user.username, 0))
        connection.commit()

@dp.message_handler(commands='admin')
async def handfler(message: types.Message, state: FSMContext):
 if message.chat.type == "private":
   join(message.from_user)
   q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
   result = q.fetchone()
   if result[0] == 0:
     if message.chat.id == admin:
         await message.answer('<b>Добро пожаловать в админ панель!</b>', reply_markup=kb.admin)

@dp.callback_query_handler(text='static_bot')
async def control_ekzekbots(call):
    row = q.execute('SELECT * FROM users').fetchall()
    lenght = len(row)
    bl = q.execute('SELECT * FROM users WHERE block = 1').fetchall()
    blc = len(bl)
    await call.message.edit_text(f"""
<b>Статистика бота:</b>

<b>Пользователей: </b><code>{lenght}</code>
<b>Заблокировано: </b><code>{blc}</code>
""", reply_markup=kb.men_bot_back)

@dp.callback_query_handler(text='backadm')
async def control_ekzekbots(call):
    await call.message.edit_text(f'<b>Добро пожаловать в админ панель!</b>', reply_markup=kb.admin)

@dp.callback_query_handler(lambda c: c.data == "ras_bot")
async def rass(callback_query: types.CallbackQuery):
    usid = callback_query.from_user.id
    await Rass.post.set()
    return await callback_query.message.answer('📃 Пришлите мне сообщение для рассылки:', reply_markup=kb.back_ctrlbot)

@dp.message_handler(content_types=types.ContentType.ANY, state=Rass.post)
async def rass_step2_handler(message, state: FSMContext):
    if message.text == '❌ Отмена':
        await message.answer('<b>Отмена! Возвращаю назад</b>', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'<b>Добро пожаловать в админ панель!</b>', reply_markup=kb.admin)
        await state.finish()
        return
    await Rass.next()
    await state.update_data(msg=message)
    return await message.answer('🎙️ Клавиатура (name|btn, name|btn\\n) или "-" чтобы пропустить', reply_markup=kb.back_ctrlbot)


@dp.message_handler(state=Rass.kb)
async def rass_finish_handler(message, state: FSMContext):
    if message.text == '❌ Отмена':
        await message.answer('Отмена! Возвращаю в главное меню.', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f'<b>Добро пожаловать в админ панель!</b>', reply_markup=kb.admin)
        await state.finish()
        return
    else:
        data = await state.get_data()
        await state.finish()
        text = message.text
        if message.text != '-':
            text = message.text.split('\n')
            lenght = len(text[0].split(','))
            kb = InlineKeyboardMarkup(row_width=lenght)
            for i in text:
                i = i.split(',')
                for z in i:
                    name, url = z.split('|')
                    kb.insert(InlineKeyboardButton(text=name, url=url))
        else:
            kb = None

        msg = data['msg']
        row = q.execute('SELECT user_id FROM users').fetchall()
        connection.commit()
        users = [user[0] for user in row]
        connection.commit()
        send=0
        error=0
        all=0
        await message.answer('Начинаю рассылку...')

        for i in users:
            all += 1
            try:
         #       await asyncio.sleep(3)
                await msg.send_copy(chat_id=i,reply_markup=kb)

                send+=1
            except:
                error+=1
        await message.answer(f'Отправлено: {all}\n'
                          f'Успешно: {send}\n'
                          f'Неуспешно: {error}',reply_markup=types.ReplyKeyboardRemove())

@dp.callback_query_handler(text='add_blacklist')
async def control_ekzekbots(call):
    await call.message.answer('<b>Введите юзернейм или айди пользователя для выдачи админки в боте:</b>\n\n<i>Для отмены нажмите кнопку ниже 👇</i>', reply_markup=kb.back_ctrlbot)
    await bllist.add.set()

@dp.callback_query_handler(text='remove_blacklist')
async def control_ekzekbots(call):
    await call.message.answer('<b>Введите юзернейм или айди пользователя для разбана в боте:</b>\n\n<i>Для отмены нажмите кнопку ниже 👇</i>', reply_markup=kb.back_ctrlbot)
    await bllist.remove.set()

@dp.callback_query_handler(text='bllist')
async def control_bllist(call):
    bl = q.execute('SELECT * FROM users WHERE block = 1').fetchall()
    blc = len(bl)
    await call.message.edit_text(f'<b>Управление чёрным списком </b>\n\n<b>В чёрном списке: <code>{blc}</code> пользователей</b>', reply_markup=kb.blacklist_men)

@dp.message_handler(state=bllist.add)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == '❌ Отмена':
        await message.answer('<b>Отмена! Возвращаю назад</b>', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'<b>Управление чёрным списком </b>\n\n<b>В чёрном списке: <code>{blc}</code> пользователей</b>', reply_markup=kb.blacklist_men)
        return
    if "@" in message.text.lower():
       uforbl = q.execute("UPDATE users SET block = ? WHERE user_username = ?", (1, message.text[1:]))
       connection.commit()
       uubl = q.execute("SELECT user_id FROM users WHERE user_username = ?", (message.text[1:],))
       tuubl = uubl.fetchone()
       try:
         await bot.send_message(tuubl[0], f"<b>Вы были заблокировани в боте!</b>")
       except:
           pass
    else:
       uforbl = q.execute("UPDATE users SET block = ? WHERE user_id = ?", (1, message.text))
       connection.commit()
       await bot.send_message(message.text, f"<b>Вы были заблокировани в боте!</b>")
    await message.answer(f"<b>‼️ Пользователь был успешно заблокирован!</b>", reply_markup=ReplyKeyboardRemove())
    bl = q.execute('SELECT * FROM users WHERE block = 1').fetchall()
    blc = len(bl)
    await message.answer(f'<b>Управление чёрным списком </b>\n\n<b>В чёрном списке: <code>{blc}</code> пользователей</b>', reply_markup=kb.blacklist_men)

@dp.message_handler(state=bllist.remove)
async def process_name(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == '❌ Отмена':
        await message.answer('<b>Отмена! Возвращаю назад</b>', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'<b>Управление чёрным списком</b>\n\n<b>В чёрном списке: <code>{blc}</code> пользователей</b>', reply_markup=kb.blacklist_men)
        return
    if "@" in message.text.lower():
       uforbl = q.execute("UPDATE users SET block = ? WHERE user_username = ?", (0, message.text[1:]))
       connection.commit()
       uubl = q.execute("SELECT user_id FROM users WHERE user_username = ?", (message.text[1:],))
       tuubl = uubl.fetchone()
       try:
         await bot.send_message(tuubl[0], f"<b>Вы были разблокированы в боте!</b>")
       except:
           pass
    else:
       uforbl = q.execute("UPDATE users SET block = ? WHERE user_id = ?", (1, message.text))
       connection.commit()
       await bot.send_message(message.text, f"<b>Вы были разблокированы в боте!</b>")
    await message.answer(f"<b>‼️ Пользователь был успешно разблокированы!</b>", reply_markup=ReplyKeyboardRemove())
    bl = q.execute('SELECT * FROM users WHERE block = 1').fetchall()
    blc = len(bl)
    await message.answer(f'<b>Управление чёрным списком </b>\n\n<b>В чёрном списке: <code>{blc}</code> пользователей</b>', reply_markup=kb.blacklist_men)

@dp.message_handler(state=sender.text)
async def process_name(message: types.Message, state: FSMContext):
    info = q.execute('SELECT user_id FROM users').fetchall()
    if message.text == '❌ Отмена':
        await message.answer('<b>Отмена! Возвращаю назад</b>', reply_markup=ReplyKeyboardRemove())
        await message.answer(f'<b>Добро пожаловать в админ панель!</b>', reply_markup=kb.admin)
        await state.finish()
        return
    await message.answer('<b>Начинаю рассылку...</b>', reply_markup=ReplyKeyboardRemove())
    for i in range(len(info)):
      try:
        print(info[i][0])
        await bot.send_message(info[i][0], message.text)
      except:
        pass
    await message.answer('<b>Рассылка завершена.</b>')
    await state.finish()

def get_download_links(video_url):
    r = requests.get(f'https://api.douyin.wtf/api?url={video_url}').json()
    if r["status"] == "success":
        video_url2 = r['video_data']['nwm_video_url']
        video_r = requests.get(video_url2).content
        audio_url = r['music']['play_url']['uri']
        audio_r = requests.get(audio_url).content
        return video_r, audio_r
    return None, None
    
@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
 if message.chat.type == "private":
    join(message.from_user)
    chbl = q.execute("SELECT block FROM users WHERE user_id = ?", (message.from_user.id,))
    tchbl = chbl.fetchone()
    if tchbl[0] == 1:
        return
    else:
       result = q.fetchone()
       keyboard = InlineKeyboardMarkup()
       button = InlineKeyboardButton('☎️ Поддержка', url='https://t.me/F1reW')
       dd = keyboard.add(button)
       await message.reply('<b>Привет! Я бот для скачивания видео из TikTok. \nПросто пришли мне ссылку на видео которое хочешь скачать</b>', reply_markup=dd)

@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
 if message.chat.type == "private":
    if message.text.startswith(
            ('https://www.tiktok.com', 'http://www.tiktok.com', 'https://vm.tiktok.com', 'http://vm.tiktok.com', 'https://vt.tiktok.com')):
      chbl = q.execute("SELECT block FROM users WHERE user_id = ?", (message.from_user.id,))
      tchbl = chbl.fetchone()
      if tchbl[0] == 1:
           return
      else:
        Year = int(datetime.datetime.now().strftime("%Y"))
        Mounth = datetime.datetime.now().strftime("%B")
        Dey = int(datetime.datetime.now().strftime("%d"))
        Hour = int(datetime.datetime.now().strftime("%H"))
        Minute = datetime.datetime.now().strftime("%M")
        Dates = [Dey, Hour, Minute, Mounth, Year]
        date = f"{Dates[4]}y {Dates[3]} {Dates[0]} {Dates[1]}:{Dates[2]}"
        print(f"{message.from_user.id} | {message.from_user.full_name} | @{message.from_user.username} | {date}")
        mmsg = await message.reply('<b>Загрузка... Пожалуста подождите!</b>')
        try:
           video_url = message.text
           video_r, audio_r = get_download_links(video_url)
        except Exception:
            await mmsg.edit('<b>Ошибка при загрузке видео!</b>')
            return
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Скачано через', url='https://t.me/BotTTLoad_bot')
        dd = keyboard.add(button)
        if video_r != None:
            await bot.send_video(
                chat_id=message.chat.id,
                video=video_r,
                caption='<b>Скачано через: @botTTLoad_bot</b>'
            )
            await bot.send_audio(
                chat_id=message.chat.id,
                audio=audio_r,
                title=f'result_{message.from_user.id}.mp3',
                caption='',
                reply_markup=dd
            )
            await mmsg.delete()
        else:
            await mmsg.edit_text('<b>Похоже что такого видео не существует.</b>')
    else:
        await message.answer('<b>Пожалуйста отправь ссылку на видео.</b>')


if __name__ == "__main__":
    print("<<<START>>>")
    executor.start_polling(dp, skip_updates=False)
