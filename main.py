import datetime
import random
import sqlite3
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from conf import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
ROLLS_PER_DAY = 10

btn = InlineKeyboardButton('Присоединиться', callback_data='btn1')
btn_coon = InlineKeyboardMarkup().add(btn)

btn_red = InlineKeyboardButton('🔴', callback_data='color1')
btn_black = InlineKeyboardButton('⚫️', callback_data='color2')
color_btn = InlineKeyboardMarkup().add(btn_red, btn_black)

btn_bet_500 = InlineKeyboardButton('500', callback_data='bet1')
btn_bet_1000 = InlineKeyboardButton('1000', callback_data='bet2')
btn_bet_2000 = InlineKeyboardButton('2000', callback_data='bet3')
btn_bet_5000 = InlineKeyboardButton('5000', callback_data='bet4')
bet_btn = InlineKeyboardMarkup().add(btn_bet_500, btn_bet_1000, btn_bet_2000, btn_bet_5000)

btn_confirm_lobby = InlineKeyboardButton('Начать игру', callback_data='play')
exit_lobby = InlineKeyboardButton('Выйти из лобби', callback_data='exit_lobby')
btn_exit_lobby = InlineKeyboardMarkup().add(exit_lobby)
btn_conf = InlineKeyboardMarkup().add(btn_confirm_lobby)

btn_play_solo = InlineKeyboardButton('Начать игру', callback_data='play_solo')
btn_play_exit = InlineKeyboardMarkup(row_width=1).add(btn_play_solo)


####Массивы####

####Классы для состояний####
class betInput(StatesGroup):
    bet = State()
    color = State()
    balance = State()
    roll = State()


class groupBet(StatesGroup):
    BET_CHOICE = State()
    COLOR_CHOICE = State()
    CHECK_MEMBERS = State()
    PLAY = State()
    ROLL = State()


class admin_pn(StatesGroup):
    choice_id = State()
    set_balance = State()


global db
global sql

database_path = 'server.db'

db = sqlite3.connect(database_path)
sql = db.cursor()

####Обозначение столбцов таблиц####
sql.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT,
        cash INT,
        name TEXT,
        color TEXT,
        bet_solo INT
        )""")
sql.execute("""
CREATE TABLE IF NOT EXISTS rolls(
        last TEXT,
        roll INT,
        i_r INT)""")
sql.execute("""CREATE TABLE IF NOT EXISTS group_bet(
        chat_id INT,
        player_id INT,
        bet INT,
        player_name TEXT,
        colors TEXT)""")
db.commit()


####Функции####
def id_bal_val(name: str, id: int, color: str, bet):
    sql.execute(f'SELECT id FROM users WHERE id = {id}')
    if sql.fetchone() is None:
        sql.execute(f'INSERT INTO users VALUES(?, ?, ?, ?, ?)', (id, 10000, name, color, bet))
        db.commit()


def group_b(chat_id: int, id: int, player_name: str, colors_: str):
    sql.execute(f'SELECT player_id FROM group_bet WHERE player_id = {id}')
    if sql.fetchone() is None:
        sql.execute(f'INSERT INTO group_bet VALUES (?,?,?,?,?)', (chat_id, id, 0, player_name, colors_))
    db.commit()


def last_rolls_today(id: int):
    sql.execute(f'SELECT i_r FROM rolls WHERE i_r = {id}')
    if sql.fetchone() is None:
        sql.execute(f"INSERT INTO rolls VALUES(date('now'), ?, ?)", (0, id))
        db.commit()


def admin_panel(id: int):
    sql.execute(f'SELECT id FROM users WHERE id = {id}')


#######Одиночная ставка#######
@dp.message_handler(commands=['bet'])
async def bet_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['me'] = message.from_user.id
        data['name'] = message.from_user.first_name
        color = 'colors'
        id_bal_val(data['name'], data['me'], color, 0)
        now_balance = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
        if now_balance[0] < 500:
            await message.answer('Ваш баланс меньше 500')
        else:
            cash_check = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
            if cash_check == 0:
                await message.answer('Выш баланс равен нулю')
            else:
                await message.reply(f"{message.from_user.first_name}\n"
                                    f"Выберите цвет", reply_markup=color_btn)
                await state.set_state(betInput.color)


@dp.callback_query_handler(state=betInput.color, text="color1")
async def colors(callback_query: types.CallbackQuery, state: FSMContext):
    check = callback_query.from_user.id
    check_reply = callback_query.message.reply_to_message.from_user.id
    if check != check_reply:
        await callback_query.answer('Вы не можете этого сделать')
    else:
        async with state.proxy() as data:
            sql.execute(f'UPDATE users SET color = ? WHERE id = {data["me"]}', ('🔴',))
            db.commit()
            data['color_user'] = list(i[0] for i in sql.execute(f'SELECT color FROM users WHERE id = {data["me"]}'))
            data['name_color'] = f'{data["name"]} {data["color_user"][0]}'
            await callback_query.message.edit_text(f'Ставка:\n'
                                                   f'{data["name_color"]}\n'
                                                   f'Выберите ставку', reply_markup=bet_btn)
            await state.set_state(betInput.bet)


@dp.callback_query_handler(state=betInput.color, text="color2")
async def colors(callback_query: types.CallbackQuery, state: FSMContext):
    check = callback_query.from_user.id
    check_reply = callback_query.message.reply_to_message.from_user.id
    if check != check_reply:
        await callback_query.answer('Вы не можете этого сделать')
    else:
        async with state.proxy() as data:
            sql.execute(f'UPDATE users SET color = ? WHERE id = {data["me"]}', ('⚫️',))
            db.commit()
            data['color_user'] = list(i[0] for i in sql.execute(f'SELECT color FROM users WHERE id = {data["me"]}'))
            data['name_color'] = f'{data["name"]} {data["color_user"][0]}'
            await callback_query.message.edit_text(f'Ставка:\n'
                                                   f'{data["name_color"]}\n'
                                                   f'Выберите ставку', reply_markup=bet_btn)
            await state.set_state(betInput.bet)


@dp.callback_query_handler(state=betInput.bet, text='bet1')
async def bet500(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            sql.execute(f'UPDATE users SET bet_solo = 500 WHERE id = {data["me"]}')
            sql.execute(f'UPDATE users SET cash = cash - 500 WHERE id = {data["me"]}')
            db.commit()
            user_bet = list(i for i in sql.execute(f'SELECT bet_solo FROM users WHERE id = {data["me"]}'))
            for i in user_bet:
                data['bet_solo'] = i[0]
            data['color_name_bet'] = f"{data['name_color']} {data['bet_solo']}"
            await callback_query.message.edit_text(f'Ставка:\n'
                                                   f'{data["color_name_bet"]}\n', reply_markup=btn_play_exit)
            await state.set_state(betInput.roll)


@dp.callback_query_handler(state=betInput.bet, text='bet2')
async def bet1000(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            now_balance = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
            if now_balance[0] < 1000:
                await callback_query.answer('У вас не достаточно денег')
            else:
                sql.execute(
                    f'UPDATE users SET bet_solo = 1000 WHERE id = {data["me"]}')
                sql.execute(f'UPDATE users SET cash = cash - 1000 WHERE id = {data["me"]}')
                db.commit()
                user_bet = list(i for i in sql.execute(f'SELECT bet_solo FROM users WHERE id = {data["me"]}'))
                for i in user_bet:
                    data['bet_solo'] = i[0]
                data['color_name_bet'] = f"{data['name_color']} {data['bet_solo']}"
                await callback_query.message.edit_text(f'Ставка:\n'
                                                       f'{data["color_name_bet"]}\n', reply_markup=btn_play_exit)
                await state.set_state(betInput.roll)


@dp.callback_query_handler(state=betInput.bet, text='bet3')
async def bet2000(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            now_balance = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
            if now_balance[0] < 2000:
                await callback_query.answer('У вас не достаточно денег')
            else:
                sql.execute(
                    f'UPDATE users SET bet_solo = 2000 WHERE id = {data["me"]}')
                sql.execute(f'UPDATE users SET cash = cash - 2000 WHERE id = {data["me"]}')
                db.commit()
                user_bet = list(i for i in sql.execute(f'SELECT bet_solo FROM users WHERE id = {data["me"]}'))
                for i in user_bet:
                    data['bet_solo'] = i[0]
                data['color_name_bet'] = f"{data['name_color']} {data['bet_solo']}"
                await callback_query.message.edit_text(f'Ставка:\n'
                                                       f'{data["color_name_bet"]}\n', reply_markup=btn_play_exit)
                await state.set_state(betInput.roll)


@dp.callback_query_handler(state=betInput.bet, text='bet4')
async def bet5000(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            now_balance = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
            if now_balance[0] < 5000:
                await callback_query.answer('У вас не достаточно денег')
            else:
                sql.execute(
                    f'UPDATE users SET bet_solo = 5000 WHERE id = {data["me"]}')
                sql.execute(f'UPDATE users SET cash = cash - 5000 WHERE id = {data["me"]}')
                db.commit()
                user_bet = list(i for i in sql.execute(f'SELECT bet_solo FROM users WHERE id = {data["me"]}'))
                for i in user_bet:
                    data['bet_solo'] = i[0]
                data['color_name_bet'] = f"{data['name_color']} {data['bet_solo']}"
                await callback_query.message.edit_text(f'Ставка:\n'
                                                       f'{data["color_name_bet"]}\n', reply_markup=btn_play_exit)
                await state.set_state(betInput.roll)


@dp.callback_query_handler(state=betInput.roll, text="play_solo")
async def roll(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            color_arr = ['🔴','⚫️']
            color_rand = random.choice(color_arr)
            if color_rand == '🔴':
                red = []
                red_winners = list(
                    i[0] for i in sql.execute(f'SELECT name FROM users WHERE color = ? AND id = {data["me"]}', ('🔴',)))
                player_bet_red = list(i[0] for i in
                                      sql.execute(f'SELECT bet_solo FROM users WHERE color = ? AND id = {data["me"]}',
                                                  ('🔴',)))
                if player_bet_red != []:
                    sql.execute(f'UPDATE users SET cash = cash + {player_bet_red[0] * 2} WHERE id = {data["me"]}')
                    db.commit()
                    balance_red = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
                    red.append(red_winners)
                    if red !=[]:
                        await callback_query.message.edit_text(f'Выпало 🔴\n'
                                                               f'{red_winners[0]}\n'
                                                               f'Вам улыбнулась удача!\n'
                                                               f'Ваш баланс: {balance_red[0]}')
                        sql.execute(f'UPDATE users SET color = ? WHERE id = {data["me"]}',('colors',))
                        sql.execute(f'UPDATE users SET bet_solo = {0} WHERE id = {data["me"]}')
                        db.commit()

                    else:
                        balance_red = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
                        await callback_query.message.edit_text(f'Выпало 🔴\n'
                                                               f'Не повезло:(\n'
                                                               f'Ваш баланс: {balance_red[0]}')
                        sql.execute(f'UPDATE users SET color ? WHERE id = {data["me"]}',('colors',))
                        sql.execute(f'UPDATE users SET bet_solo = {0} WHERE id = {data["me"]}')
                        db.commit()
                    await state.finish()

            if color_rand == '⚫️':
                black = []
                black_winners = list(
                    i[0] for i in sql.execute(f'SELECT name FROM users WHERE color = ? AND id = {data["me"]}', ('⚫️',)))
                player_bet_black = list(i[0] for i in
                                        sql.execute(f'SELECT bet_solo FROM users WHERE color = ? AND id = {data["me"]}',
                                                    ('⚫️',)))
                black.append(black_winners)
                if black != []:
                    sql.execute(f'UPDATE users SET cash = cash + {player_bet_black[0] * 2} WHERE id = {data["me"]}')
                    db.commit()
                    balance_black = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
                    await callback_query.message.edit_text(f'Выпало ⚫️\n'
                                                           f'{black_winners[0]}\n'
                                                           f'Вам улыбнулась удача!\n'
                                                           f'Ваш баланс: {balance_black[0]}')
                    sql.execute(f'UPDATE users SET color = ? WHERE id = {data["me"]}',('colors',))
                    sql.execute(f'UPDATE users SET bet_solo = {0} WHERE id = {data["me"]}')
                    db.commit()

                else:
                    balance_black = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["me"]}'))
                    await callback_query.message.edit_text(f'Выпало ⚫️\n'
                                                           f'Не повезло:(\n'
                                                           f'Ваш баланс: {balance_black[0]}')
                    sql.execute(f'UPDATE users SET color = ? WHERE id = {data["me"]}',('colors',))
                    sql.execute(f'UPDATE users SET bet_solo = {0} WHERE id = {data["me"]}')
                    db.commit()
                await state.finish()


@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    for i in sql.execute(f'SELECT cash FROM users WHERE id = {message.from_user.id}'):
        await message.answer(f"{message.from_user.first_name}\n"
                             f"Ваш баланс: {i[0]}₽")


@dp.message_handler(commands=['top'])
async def balance(message: types.Message):
    top_arr = []
    names = []
    name_ball_list = []
    for i in list(sql.execute(f"SELECT name FROM users ORDER BY cash"))[::-1]:
        top_arr.append(i[0])
    for j in list(sql.execute(f"SELECT cash FROM users ORDER BY cash"))[::-1]:
        names.append(j[0])

    a = list(zip(top_arr, names))
    for i in a:
        name_list = f"{i[0]}: {i[1]}₽"
        name_ball_list.append(name_list)
    name_bal_str = '\n'.join(name_ball_list[0:11])
    await message.answer(f"ТОП 10 ВСЕХ ИГРОКОВ\n"
                         f"{name_bal_str}")


#######Групповая ставка#######
@dp.message_handler(commands=['join'])
async def join_bet(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.from_user.id
        data['chat_id'] = message.chat.id
        data['my_name'] = message.from_user.first_name
        data['name'] = 'name'
        data['color'] = 'colors'
        data['join_name'] = " "
        balance_now = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["id"]}'))
        if balance_now[0] < 500:
            await message.answer('На вашем балансе меньше 500 рублей\n')
        else:
            group_b(data['chat_id'], data['id'], data['name'], data['color'])
            player = list(
                i[0] for i in sql.execute(f'SELECT player_name FROM group_bet WHERE player_id = {data["id"]}'))
            if data['my_name'] in player:
                await message.answer(f'Вы уже в лобби')
            else:
                sql.execute(f'UPDATE group_bet SET player_name = (?) WHERE player_id = {data["id"]}',
                            (data['my_name'],))
                name = list(i for i in sql.execute(
                    f'SELECT player_name FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
                for i in name:
                    data['join_name'] = i[0]
                await message.reply(f'{data["join_name"]} \n'
                                    f'Выберите цвет', reply_markup=color_btn)
                await state.set_state(groupBet.COLOR_CHOICE)


@dp.callback_query_handler(state=groupBet.COLOR_CHOICE, text="color1")
async def colors(callback_query: types.CallbackQuery, state: FSMContext):
    check = callback_query.from_user.id
    check_reply = callback_query.message.reply_to_message.from_user.id
    if check != check_reply:
        await callback_query.answer('Вы не можете этого сделать')
    else:
        async with state.proxy() as data:
            id_check = list(
                i[0] for i in sql.execute(f'SELECT player_id FROM group_bet WHERE player_id = {data["id"]}'))
            if data['id'] != id_check[0]:
                await callback_query.answer('Вы не можете этого сделать')
            else:
                sql.execute(f'UPDATE group_bet SET colors = (?) WHERE player_id = {data["id"]}', '🔴')
                db.commit()
                user_color = list(i for i in sql.execute(
                    f'SELECT colors FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
                for i in user_color:
                    data['join_color'] = i[0]

                data['color_name'] = f"{data['join_name']} {data['join_color']}"

                await callback_query.message.edit_text(f'{data["color_name"]} \n'
                                                       f'Выберите ставку', reply_markup=bet_btn)
                await state.set_state(groupBet.BET_CHOICE)


@dp.callback_query_handler(state=groupBet.COLOR_CHOICE, text="color2")
async def colors(callback_query: types.CallbackQuery, state: FSMContext):
    check = callback_query.from_user.id
    check_reply = callback_query.message.reply_to_message.from_user.id
    if check != check_reply:
        await callback_query.answer('Вы не можете этого сделать')
    else:
        async with state.proxy() as data:
            sql.execute(f'UPDATE group_bet SET colors = (?) WHERE player_id = {data["id"]}', ('⚫️',))
            db.commit()
            user_color = list(i for i in sql.execute(
                f'SELECT colors FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
            for i in user_color:
                data['join_color'] = i[0]

            data['color_name'] = f"{data['join_name']} {data['join_color']}"

            await callback_query.message.edit_text(f'{data["color_name"]} \n'
                                                   f'Выберите ставку', reply_markup=bet_btn)
            await state.set_state(groupBet.BET_CHOICE)


@dp.callback_query_handler(state=groupBet.BET_CHOICE, text='bet1')
async def bets(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            sql.execute(
                f'UPDATE group_bet SET bet = 500 WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}')
            sql.execute(f'UPDATE users SET cash = cash - 500 WHERE id = {data["id"]}')
            db.commit()
            user_bet = list(i for i in sql.execute(
                f'SELECT bet FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
            for i in user_bet:
                data['join_bet'] = i[0]
            data['color_name_bet'] = f"{data['color_name']} {data['join_bet']}"
            await callback_query.message.edit_text(f'{data["color_name_bet"]}\n'
                                                   f'Вы добавлены в лобби!', reply_markup=btn_exit_lobby)
            await state.finish()


@dp.callback_query_handler(state=groupBet.BET_CHOICE, text='bet2')
async def bets(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            balance_now = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["id"]}'))
            if balance_now[0] < 1000:
                await callback_query.answer(f'У вас недостаточно средств для этой ставки\n')
            else:
                sql.execute(
                    f'UPDATE group_bet SET bet = 1000 WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}')
                sql.execute(f'UPDATE users SET cash = cash - 1000 WHERE id = {data["id"]}')
                db.commit()
                user_bet = list(i for i in sql.execute(
                    f'SELECT bet FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
                for i in user_bet:
                    data['join_bet'] = i[0]
                data['color_name_bet'] = f"{data['color_name']} {data['join_bet']}"
                await callback_query.message.edit_text(f'Участники:\n'
                                                       f'{data["color_name_bet"]} \n'
                                                       f'Вы добавлены в лобби!', reply_markup=btn_exit_lobby)
                await state.finish()


@dp.callback_query_handler(state=groupBet.BET_CHOICE, text='bet3')
async def bets(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            balance_now = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["id"]}'))
            if balance_now[0] < 2000:
                await callback_query.answer(f'У вас недостаточно средств для этой ставки\n')
            else:
                sql.execute(
                    f'UPDATE group_bet SET bet = 2000 WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}')
                sql.execute(f'UPDATE users SET cash = cash - 2000 WHERE id = {data["id"]}')
                db.commit()
                user_bet = list(i for i in sql.execute(
                    f'SELECT bet FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
                for i in user_bet:
                    data['join_bet'] = i[0]
                data['color_name_bet'] = f"{data['color_name']} {data['join_bet']}"
                await callback_query.message.edit_text(f'{data["color_name_bet"]} \n'
                                                       f'Вы добавлены в лобби!', reply_markup=btn_exit_lobby)
                await state.finish()


@dp.callback_query_handler(state=groupBet.BET_CHOICE, text='bet4')
async def bets(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        check = callback_query.from_user.id
        check_reply = callback_query.message.reply_to_message.from_user.id
        if check != check_reply:
            await callback_query.answer('Вы не можете этого сделать')
        else:
            balance_now = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {data["id"]}'))
        if balance_now[0] < 5000:
            await callback_query.answer(f'У вас недостаточно средств для этой ставки\n')
        else:
            sql.execute(
                f'UPDATE group_bet SET bet = 5000 WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}')
            sql.execute(f'UPDATE users SET cash = cash - 5000 WHERE id = {data["id"]}')
            db.commit()
            user_bet = list(i for i in sql.execute(
                f'SELECT bet FROM group_bet WHERE player_id = {data["id"]} AND chat_id = {data["chat_id"]}'))
            for i in user_bet:
                data['join_bet'] = i[0]
            data['color_name_bet'] = f"{data['color_name']} {data['join_bet']}"
            await callback_query.message.edit_text(f'{data["color_name_bet"]} \n'
                                                   f'Вы добавлены в лобби!', reply_markup=btn_exit_lobby)
            await state.finish()


@dp.callback_query_handler(text='exit_lobby')
async def exit_func(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    check_id = list(i[0] for i in sql.execute(f'SELECT player_id FROM group_bet'))
    if user_id not in check_id:
        await callback_query.answer('Вы не в лобби')
    else:
        sql.execute(f'DELETE FROM group_bet WHERE player_id = {user_id} AND chat_id = {chat_id}')
        db.commit()
    await callback_query.message.edit_text('Вы удалены из лобби')


@dp.message_handler(commands=['play'])
async def group_play(message: types.Message):
    id = message.from_user.id
    chat_id = message.chat.id
    check_id = list(i[0] for i in sql.execute(f'SELECT player_id FROM group_bet'))
    if id not in check_id:
        await message.answer('Вы не в лобби')
    else:
        players_name_arr = []
        players_color_arr = []
        players_bet_arr = []
        players_in_lobby_arr = []
        players = list(i for i in sql.execute(f'SELECT player_id FROM group_bet WHERE chat_id = {chat_id}'))
        if len(players) < 2:
            await message.answer('В лобби должно быть минимум 2 человека')
        else:
            players_name = list(i for i in sql.execute(f'SELECT player_name FROM group_bet WHERE chat_id = {chat_id}'))
            for i in range(len(players_name)):
                players_name_arr.append(players_name[i][0])
            players_color = list(i for i in sql.execute(f'SELECT colors FROM group_bet WHERE chat_id = {chat_id}'))
            for i in range(len(players_color)):
                players_color_arr.append(players_color[i][0])
            players_bet = list(i for i in sql.execute(f'SELECT bet FROM group_bet WHERE chat_id = {chat_id}'))
            for i in range(len(players_bet)):
                players_bet_arr.append(players_bet[i][0])

            for i in range(len(players)):
                participants = f"{players_name_arr[i]} {players_color_arr[i]} {players_bet_arr[i]}"
                players_in_lobby_arr.append(participants)

            players_in_lobby_str = '\n'.join(players_in_lobby_arr)
            await message.answer(f'Игроки в лобби:\n'
                                 f'{players_in_lobby_str}', reply_markup=btn_conf)


@dp.callback_query_handler(text='play')
async def start_game(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    colors_arr = ['🔴', '⚫️']
    colors_rand = random.choice(colors_arr)
    if colors_rand == '🔴':
        red = []
        plus_bet_red = []
        id_red = []
        red_winners = list(i for i in
                           sql.execute(f'SELECT player_name FROM group_bet WHERE chat_id = {chat_id} AND colors = ?',
                                       '🔴', ))
        red_bed = list(
            i for i in sql.execute(f'SELECT bet FROM group_bet WHERE chat_id = {chat_id} AND colors = ?', '🔴'))
        for i in range(len(red_bed)):
            plus_bet_red.append(red_bed[i][0])
        player_id_red = list(
            i for i in sql.execute(f'SELECT player_id FROM group_bet WHERE chat_id = {chat_id} AND colors = ?', '🔴'))
        for i in range(len(player_id_red)):
            id_red.append(player_id_red[i][0])
        for i in range(len(red_winners)):
            red.append(red_winners[i][0])
            sql.execute(f'UPDATE users SET cash = cash + {plus_bet_red[i] * 2} WHERE id = {id_red[i]}')
        red_winners_str = '\n'.join(red)
        if red != []:
            await callback_query.message.edit_text(f'Выпало 🔴\n'
                                                   f'Победители:\n'
                                                   f'{red_winners_str}\n\n'
                                                   f'Проверьте ваши балансы /balance')
            sql.execute(f'DELETE FROM group_bet WHERE chat_id = {chat_id}')
        else:
            await callback_query.message.edit_text(f'Выпало 🔴\n'
                                                   f'Победителей нет:(\n\n'
                                                   f'Проверьте ваши балансы /balance')

        sql.execute(f'DELETE FROM group_bet WHERE chat_id = {chat_id}')
        db.commit()

    if colors_rand == '⚫️':
        black = []
        id_black = []
        plus_bet_black = []

        black_winners = list(i for i in sql.execute(
            f'SELECT player_name FROM group_bet WHERE chat_id = {chat_id} AND colors = ?', ('⚫️',)))
        black_bed = list(
            i for i in sql.execute(f'SELECT bet FROM group_bet WHERE chat_id = {chat_id} AND colors = ?', ('⚫️',)))
        for i in range(len(black_bed)):
            plus_bet_black.append(black_bed[i][0])

        player_id_black = list(i for i in sql.execute(
            f'SELECT player_id FROM group_bet WHERE chat_id = {chat_id} AND colors = ?', ('⚫️',)))

        for i in range(len(player_id_black)):
            id_black.append(player_id_black[i][0])

        for i in range(len(black_winners)):
            black.append(black_winners[i][0])
        for i in range(len(id_black)):
            sql.execute(f'UPDATE users SET cash = cash + {plus_bet_black[i] * 2} WHERE id = {id_black[i]}')
            db.commit()
        black_winners_str = '\n'.join(black)
        if black != []:
            await callback_query.message.edit_text(f'Выпало ⚫️\n'
                                                   f'Победители:\n'
                                                   f'{black_winners_str}\n\n'
                                                   f'Проверьте ваши балансы /balance')
        else:
            await callback_query.message.edit_text(f'Выпало ⚫️'
                                                   f'Победителей нет:(\n\n'
                                                   f'Проверьте ваши балансы /balance')

        sql.execute(f'DELETE FROM group_bet WHERE chat_id = {chat_id}')
        db.commit()


#######Общие команды#######
@dp.message_handler(commands=['admin'])
async def admin(message: types.Message, state: FSMContext):
    check_admin = message.from_user.id
    if check_admin == 792220062:
        all = list(i for i in sql.execute(f'SELECT * FROM users'))
        await message.answer(all)
        await message.answer('Введи id')
        await state.set_state(admin_pn.choice_id)
    else:
        await message.answer('У вас недостаточно прав')


@dp.message_handler(state=admin_pn.choice_id)
async def id_select(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['select_id'] = int(message.text)
        sql.execute(f'SELECT id FROM users WHERE id = {data["select_id"]}')
        await message.answer('Баланс: ')
        await state.set_state(admin_pn.set_balance)


@dp.message_handler(state=admin_pn.set_balance)
async def set_cash(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        cash = int(message.text)
        sql.execute(f'UPDATE users SET cash = {cash} WHERE id={data["select_id"]}')
        db.commit()
        await state.finish()


@dp.message_handler(commands=['bonus'])
async def bonus(message: types.Message):
    me = message.from_user.id
    balance_now = list(i[0] for i in sql.execute(f'SELECT cash FROM users WHERE id = {me}'))
    if balance_now[0] < 500:
        sql.execute(f'UPDATE users SET cash = 3000 WHERE id = {me}')
        db.commit()
        await message.answer(f'{message.from_user.first_name}\n'
                             f'Вам начислено 3000 бонусов')
    else:
        await message.answer('Ваш баланс больше либо равен 500₽\n'
                             'Бонус доступен только при балансе меньше 500₽')


@dp.message_handler(commands=['help'])
async def help_func(message: types.Message):
    await message.answer('Список команд:\n'
                         '1) /bet - Ввод ставки\n'
                         '2) /roll - Сделать ставку\n'
                         '3) /balance - Проверка баланса\n'
                         '4) /top - Топ 10 со всех чатов\n'
                         '5) /bonus - Бонус в случае, если балан нижем 500₽\n'
                         'Связь: Если вы нашли баг или у вас есть вопросы - @ac1ds')


###############################################################

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
