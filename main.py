import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
from generator_captcha import generate_captcha, delete_captcha
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

bot = Bot(token="5284050419:AAH49YF_kQutdx5XwPga7RY5its439ejH4M")
dp = Dispatcher(bot)
keyboardanswer = ReplyKeyboardMarkup(resize_keyboard=True)
stat = KeyboardButton(text=f"Статистика📊")
solv_captch = KeyboardButton(text='Решить капчу🚨')
withdraw = KeyboardButton(text='Вывести средства💰')
keyboardanswer.add(stat, solv_captch)
keyboardanswer.add(withdraw)
stop_solv_captcha = ReplyKeyboardMarkup(resize_keyboard=True)
stop = KeyboardButton(text='Перестать решать капчу🛑')
stop_solv_captcha.add(stop)

try:
    os.mkdir('captchas')
except: pass
# qiwi_token = '4734c73d355626adc01a3afc5c7e3172'
#
# def get_profile(api_access_token):
#     s7 = requests.Session()
#     s7.headers['Accept']= 'application/json'
#     s7.headers['authorization'] = 'Bearer ' + api_access_token
#     p = s7.get('https://edge.qiwi.com/person-profile/v1/profile/current?authInfoEnabled=true&contractInfoEnabled=true&userInfoEnabled=true')
#     return p.json()
#
# print(get_profile(qiwi_token))
con = sqlite3.connect('db.db')
c = con.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
    user        INTEGER,
    balance     REAL DEFAULT (0),
    correct      INTERGER DEFAULT (0),
    incorrect   INTEGER DEFAULT (0),
    answer  TEXT 
    );
""")


@dp.message_handler(commands="start")
async def helloing(msg: types.Message):
    id_user = msg.from_user.id
    try:
        c = con.cursor()
        c.execute(f'SELECT balance FROM users where user = {id_user}')
        if c.fetchone() is None:
            '''
            Если пользователя нет, добавляет его
            '''
            await msg.reply(
                f'Доброго времени суток Друзья! Данный бот поможет вам заработать, решая капчу! Удачи в решении!\nЧтобы начать решать, напишите команду /solve')
            c.execute(f'INSERT INTO users VALUES({id_user}, 0.0, 0, 0, "none")')
            con.commit()

        c.execute(f'SELECT balance, correct, incorrect FROM users where user = {id_user}')
        balance, correct, incorrect = c.fetchone()
        balance = round(balance, 3)
        await msg.answer(f'Статистика:\n Баланс: {balance}₽\nВерные капчи: {correct}\n Неверные капчи: {incorrect}', reply_markup=keyboardanswer)
    except Exception as e:
        print(e)


@dp.message_handler(commands="withdraw")
async def withdraw(msg: types.Message):
     id_user = msg.from_user.id
     await msg.answer('Минимальная сумма вывода 10₽, Qiwi\nВведите свой номер телефона(без +): ')




@dp.message_handler(commands="solve")
async def solving(msg: types.Message):
    id_user = msg.from_user.id
    capt, captcha_text = generate_captcha()
    c = con.cursor()
    c.execute(f'UPDATE users SET answer = "{captcha_text.lower()}" where user = {id_user}')
    con.commit()
    await bot.send_photo(chat_id=id_user, photo=open(capt, 'rb'))
    delete_captcha(capt)



@dp.message_handler(content_types = ['text'])
async def text(msg: types.Message):
    id_user = msg.from_user.id
    if len(msg.text) == 4:
        c = con.cursor()
        c.execute(f'SELECT answer, correct, incorrect FROM users where user = {id_user}')
        answer, correct, incorrect = c.fetchone()
        if msg.text.lower() == answer:
            c.execute(f'SELECT balance, correct FROM users where user = {id_user}')
            balance, correct = c.fetchone()
            balance += 0.005
            correct += 1
            c.execute(f'UPDATE users SET balance = {balance}, correct = {correct} where user = {id_user}')
            con.commit()
            await msg.reply('Молодец, ты верно решил капчу!\nТвоя награда 0.005₽', reply_markup=stop_solv_captcha)
        else:
            incorrect += 1
            await msg.answer('К сожалению капча решена не верно, попробуй ещё раз!', reply_markup=stop_solv_captcha)
            c.execute(f'UPDATE users SET incorrect = {incorrect} where user = {id_user}')
        await solving(msg)

    if msg.text == 'Статистика📊':
        await helloing(msg)
    elif msg.text == 'Решить капчу🚨':
        await solving(msg)
    elif msg.text == 'Вывести средства💰':
        await withdraw(msg)
    elif msg.text.isdigit():
        c = con.cursor()
        c.execute(f'SELECT balance, correct FROM users where user = {id_user}')
        balance, correct = c.fetchone()
        if balance < 10:
            await msg.answer('Вы ещё не можете вывести средства')
        else:
            pass
    elif msg.text == 'Перестать решать капчу🛑':
        await helloing(msg)







if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)