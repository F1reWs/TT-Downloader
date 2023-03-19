from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from aiogram import types

admin = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton('📊 Статистика', callback_data='static_bot'),
        InlineKeyboardButton('📢 Рассылка', callback_data='ras_bot')
    ).add(
        InlineKeyboardButton('📋 Чёрный список', callback_data='bllist'),
    )

men_bot_back = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton('⬅️ Вернуться ↩️', callback_data='backadm'),
    )

back_ctrlbot = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_ctrlbot.add(
    types.KeyboardButton('❌ Отмена')
)

blacklist_men = InlineKeyboardMarkup(
    ).add(
        InlineKeyboardButton('➕ Добавить в чёрный список', callback_data='add_blacklist'),
        InlineKeyboardButton('➖ Удалить с чёрного списка', callback_data='remove_blacklist')
    ).add(
        InlineKeyboardButton('⬅️ Вернуться ↩️', callback_data='backadm'),
    )
