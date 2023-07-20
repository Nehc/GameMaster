import os, sys, threading, time
from collections import deque
import re, json, shortuuid 

import telebot
from telebot import types

from report import create_pdf
from googletrans import Translator

from my_db import get_current_state, get_db_fild, set_db_fild
from my_db import get_db_list, clr_db_list, app_db_list

from prompts import Gens, SD_Gens
from ChatGPT import ChatGPT
from SD_api import gen_image

#while True:
#    time.sleep(1)

TIMER = 20 

q = deque()
print('inits OK...')

if len(sys.argv)>1:
    token = sys.argv[1]
else:
    token = os.getenv('TG_TOKEN')
    if not token: 
        print('bot token needed...')
        quit()

if len(sys.argv)>2:
    api_key = sys.argv[2]
else:
    api_key = os.getenv('OPENAI_KEY')
    if not api_key: 
        print('openai api_key needed...')
        quit()

def apply_first_arg(func, first_arg):
    def wrapper(*args, **kwargs):
        return func(first_arg, *args, **kwargs)
    return wrapper

PROXY = '192.168.1.200:3128' # you must set proxy there... 
chat = ChatGPT(api_key, PROXY)
bot = telebot.TeleBot(token)
translator = Translator()

re_phase_data = re.compile(r'\[(\d)/(\d)[ ,]*(\d{,2})/10\]')
re_clear = re.compile(r'\[[^\]]*\]')

#my = re.compile(r'\w+')

@bot.message_handler(commands=['help','start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Начали!', callback_data="start")
    markup.add(btn)
    bot.reply_to(message, ''''Это квестовый бот *Game Master*, который использует генеративные нейросети для создания небольших текстово-графических новелл. В процессе взаимодействия с ботом вы можете влиять на сюжет, что бы получить интересную и уникальную историю приключений вашего персонажа в фантастическом или фентезийном мире. В данном квестовом движке нет никаких иных механик, кроме повествовательной (т.е. нет показателей _жизней_, _урона_, _брони_ и тп), даже параметры персонажа типа _харизмы_ *(chr)*, _силы_ *(str)* и _интеллект_ *(int)* - это скорее задел на будущее. Зато полет вашей фантазии ограничен мало. 🤭 

 Перед тем, как приступить к приключению, вам нужно _создать_ *мир (сеттинг)* и *главного героя*. Это можно сделать тремя способами:

 🎲 - предоставить это дело боту. Он сделает просто какой-то рандомный сеттинг и/или персонажа.

 ✏️ - полностью написать описание мира или текст легенды персонажа сами (тогда бот по сути только синтезирует иллюстрацию). 

 🎭 - вы можете указать какие-то ключевые/важные аспекты, предоставив боту сгенерировать полный текст. 
 
 Можно сочетать эти способы для сеттинга/героя в любых вариантах. 
 
 После этого вы переходить в *режим квеста*. Данные режим еще достаточно сырой, поэтому нужно использовать его _аккуратно_. 😊

По задумке бот синтезирует от 3 до 6 сцен, каждая из которых начинается с завязки, сопровождаемой иллюстрацией. Бот запрашивает ваши (т.е. главного героя) действия и встраивает их в повествование. По мере развития сюжете растет показатель прогресса сцены и когда он доходит до 10 - происходит переход на новую сцену. 

Важный технический нюанс: в тексте описания сцены *всегда должен присутствовать* небольшой блок в квадратных скобках вида *[1/3,4/10]* (_Это значит первая сцена из трех, прогресс 4 из 10_). Если вы не видите такого блока, или их несколько (хотя первым будет взят тот, который идет раньше), или номер сцены не соответствует контексту, а так же в случае, если вам просто не нравится сцена и/или ее развитие - вы можете воспользоваться опцией 🎲 *Еще раз*.  Так же, с момента, как вы сгенерировали сеттинги персонажа вы можете сформировать 📕 *Журнал* текущего приключения в *формате pdf*.

_Команды /start и /help вернут вас к этому тексту и сбросят состояние движка (если вдруг что-то пошло не так и вы не понимаете что происходит)_

*Хороших приключений!* 🙋‍♂️''', reply_markup=markup, parse_mode='MARKDOWN')


@bot.callback_query_handler(func=lambda call: True)
def start(call):
    if call.data == "start":
        message = call.message
        scene_img = []
        for i in range(6):
            scene_img.append(shortuuid.uuid())    
        set_db_fild(message.chat.id,'setting_img',shortuuid.uuid())
        set_db_fild(message.chat.id,'hero_img',shortuuid.uuid())
        set_db_fild(message.chat.id,'scene_img',json.dumps(scene_img))
        state_send(message.chat.id,'S_START')


@bot.message_handler(content_types=['text'])
def message_deque(message):
    q.append(message)

#--------------------- Send section ------------------------

def send_setting(chat_id,sett, ru_sett=None):
    set_db_fild(chat_id,'setting',sett)
    prompt = SD_Gens.sett(sett)
    ans = chat.answer(prompt)
    img = gen_image(ans, {'height':480,'width':640})
    f_name = get_db_fild(chat_id, 'setting_img')
    with open('./images/'+f_name, 'wb') as f:
        f.write(img)
    ru_trl = ru_sett if ru_sett else translator.translate(sett,dest='ru').text
    set_db_fild(chat_id,'ru_sett',ru_trl)
    bot.send_photo(chat_id, img, caption=ru_trl[:1024])


def send_hero(chat_id,sett,hero, ru_hero=None):
    set_db_fild(chat_id,'hero',hero)
    prompt = SD_Gens.hero(sett,hero)
    hero_sd = chat.answer(prompt)
    print(hero_sd)
    img = gen_image(hero_sd, {'height':300,'width':300})
    f_name = get_db_fild(chat_id, 'hero_img')
    with open('./images/'+f_name, 'wb') as f:
        f.write(img)
    prompt = Gens.stats(hero)
    exp = chat.answer(prompt)
    atrs = exp.split(', ')
    set_db_fild(chat_id,'hero_name', atrs[0])
    for atr in atrs[1:]:
        at  = atr.split('=')
        set_db_fild(chat_id,at[0],at[1])
    ru_trl = ru_hero if ru_hero else translator.translate(hero,dest='ru').text    
    set_db_fild(chat_id,'ru_hero',ru_trl)
    bot.send_photo(chat_id, img, caption=f'{ru_trl[:1000]} \[*{exp}*]', parse_mode="Markdown")


def send_quest(chat_id,scene,f_name):
    sett = get_db_fild(chat_id,'setting')
    prompt = SD_Gens.scene(sett,scene)
    scene_sd = chat.answer(prompt)
    print(scene_sd)
    img = gen_image(scene_sd, {'height':480,'width':640})
    with open('./images/'+f_name, 'wb') as f:
        f.write(img)
    ru_trl = translator.translate(scene,dest='ru').text    
    bot.send_photo(chat_id, img, caption=ru_trl[:1000]+' <b>Ваши действия?</b>', parse_mode="HTML")


def quest_roll(chat_id, r=0):
    sett = get_db_fild(chat_id,'setting')
    hero = get_db_fild(chat_id,'hero')
    scene = get_db_list(chat_id,'scene_ls')[-1]
    gms = get_db_list(chat_id,'GM_ans')
    acts = get_db_list(chat_id, 'pl_act')
    q = len(gms) - gms.index(scene) 
    scene_num = get_db_fild(chat_id,'curent_scene')
    if scene_num == '1':
        scene = None
    max_scene_num = get_db_fild(chat_id,'max_scene')
    #_progress = get_db_fild(chat_id,'progress')
    chr_ = get_db_fild(chat_id,'chr')
    str_ = get_db_fild(chat_id,'str')
    int_ = get_db_fild(chat_id,'int')
    prompt = Gens.quest_roll(sett, hero, chr_, str_, int_, scene, acts, scene_num, max_scene_num, q, gms)
    ans = chat.answer(prompt)
    ans = re.sub(r'[\{\}]','',ans)
    try:
        cur_scene, max_scene, progress = tuple(map(int, re_phase_data.findall(ans)[-1])) 
        if not int(scene_num) == cur_scene:
            print(cur_scene, max_scene, progress)
            time.sleep(TIMER)
            if r<3:
                quest_roll(chat_id, r+1)
            else: 
                #bot.send_message(message.chat.id, f'cur_scene {cur_scene},max_scene {max_scene}, progress {progress}')
                bot.send_message(message.chat.id, 'Что-то пошло не так, перезапускаем...')
                main_phase(message.chat.id,None if str(scene_num)=="1" else scene_num)
            return
    except Exception as e:
        print(e)
        time.sleep(TIMER)
        if r<3:
            quest_roll(chat_id, r+1)
        else: 
            #bot.send_message(message.chat.id, f'{ans} #{e}')
            bot.send_message(message.chat.id, 'Что-то пошло не так, перезапускаем...')
            main_phase(message.chat.id,None if str(scene_num)=="1" else scene_num)
        return
    ans = re_clear.sub('',ans)+f' [{cur_scene}/{max_scene},{progress}/10]'
    app_db_list(message.chat.id,'GM_ans', ans)
    set_db_fild(message.chat.id,'curent_scene',cur_scene)
    set_db_fild(message.chat.id,'max_scene',max_scene)
    set_db_fild(message.chat.id,'progress',progress)
    if progress>=10:
        bot.send_message(message.chat.id, translator.translate(ans,dest='ru').text+' <b>Продвижение сюжета...</b>', parse_mode="HTML")
        if cur_scene == max_scene:
            bot.send_message(message.chat.id, '🧙‍♂️ Поздравляю, вы завершили сценарий!🤝 В дальнейшем здесь будет вручение наград и раздел добычи!💰💰💰', parse_mode="HTML")
        else:
            time.sleep(TIMER)
            main_phase(message.chat.id, next_scene=str(cur_scene+1))    
    else:
        bot.send_message(message.chat.id, translator.translate(ans,dest='ru').text+' <b>Ваши действия?</b>', parse_mode="HTML")

#-------------------- Utils section ------------------------

def main_phase(chat_id,next_scene=None,r=0):
    print(f'scene {next_scene if next_scene else "1"}') 
    if next_scene:
        sett = get_db_fild(chat_id,'setting')
        hero = get_db_fild(chat_id,'hero')
        gms = get_db_list(chat_id,'GM_ans')
        acts = get_db_list(chat_id, 'pl_act')
        q = len(gms) - gms.index(get_db_list(chat_id,'scene_ls')[-1]) 
        #summa = '' if next_scene == '2' else get_db_fild(chat_id,'summa')
        prompt = Gens.summa(sett, hero, gms, acts, q, re_clear)
        #summa = summa+'\n\n'+chat.answer(prompt); 
        summa = chat.answer(prompt); 
        print(summa)
        scene_num = next_scene
        prompt = Gens.quest_ns(sett, hero,
                                get_db_fild(chat_id,'chr'),
                                get_db_fild(chat_id,'str'),
                                get_db_fild(chat_id,'int'),
                                scene_num,
                                get_db_fild(chat_id,'max_scene'),
                                summa)
    else:
        prompt = Gens.quest(get_db_fild(chat_id,'setting'),
                            get_db_fild(chat_id,'hero'),
                            get_db_fild(chat_id,'chr'),
                            get_db_fild(chat_id,'str'),
                            get_db_fild(chat_id,'int'))
        scene_num = "1"
    ans = chat.answer(prompt)
    ans = re.sub(r'[\{\}]','',ans) 
    try:
        cur_scene, max_scene, progress = tuple(map(int, re_phase_data.findall(ans)[-1]))
        im_name = get_db_list(chat_id,'scene_img')[cur_scene-1]
    except Exception as e:
        print(ans,e)
        time.sleep(TIMER)
        if r<3:
            main_phase(chat_id,None if str(scene_num)=="1" else scene_num,r+1)
        else:
            bot.send_message(message.chat.id, 'Что-то пошло не так... Админ починит. Позже... Наверное... 🤗')    
        return
    ans = re_clear.sub('',ans)+f' [{cur_scene}/{max_scene},{progress}/10]'
    if next_scene:
        app_db_list(chat_id,'GM_ans', ans)
        app_db_list(chat_id,'scene_ls', ans)
        set_db_fild(chat_id,'summa',summa)
    else:
        clr_db_list(chat_id,'GM_ans', ans)
        clr_db_list(chat_id,'scene_ls', ans)
        clr_db_list(chat_id,'pl_act')
    set_db_fild(chat_id,'curent_scene',cur_scene)
    set_db_fild(chat_id,'max_scene',max_scene)
    set_db_fild(chat_id,'progress',progress)
    send_quest(message.chat.id,ans,im_name)


def game_card(chat_id):
    f_name = shortuuid.uuid()
    create_pdf(f"./game_cards/{f_name}.pdf",
                get_db_fild(chat_id, 'ru_sett'), 
                get_db_fild(chat_id, 'hero_name'), 
                f'''Харизма:{get_db_fild(chat_id, 'chr')},
                    Сила:{get_db_fild(chat_id, 'str')},
                    Интеллект: {get_db_fild(chat_id, 'int')}
                 ''', 
                get_db_fild(chat_id, 'ru_hero'), 
                get_db_fild(chat_id, 'summa'), 
                get_db_fild(chat_id, 'setting_img'),
                get_db_fild(chat_id, 'hero_img'),
                translator,
                get_db_list(chat_id, 'GM_ans'),
                get_db_list(chat_id, 'pl_act'),
                get_db_list(chat_id, 'scene_ls'),
                get_db_list(chat_id, 'scene_img'),
            )            
    with open(f"./game_cards/{f_name}.pdf","rb") as misc:
        bot.send_document(chat_id,misc)    


def roll_back_scene(chat_id):
    last = get_db_list(chat_id,'scene_ls')[-1]
    new_scene_ls = get_db_list(chat_id,'scene_ls')[:-1]
    gm = get_db_list(chat_id,'GM_ans')
    new_gm = gm[:gm.index(last)]
    pl_act = get_db_list(chat_id, 'pl_act')
    new_pl_act = pl_act[:len(new_gm)-len(new_scene_ls)]
    set_db_fild(chat_id,'scene_ls',json.dumps(new_scene_ls))
    set_db_fild(chat_id,'GM_ans',json.dumps(new_gm))
    set_db_fild(chat_id,'pl_act',json.dumps(new_pl_act))


def debug_mesage(message):
    bot.send_message(message.chat.id, f'State:[{get_current_state(message.chat.id)}], command:[{message.text}]')


def get_txt_mkp(state):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if state == 'S_START':
        markup.add( types.KeyboardButton("🎲 Случайный"),
                    types.KeyboardButton("🎭 Дополни..."),
                    types.KeyboardButton("✏️ Сам опишу..."))
        return ' '.join('''🧙‍♂️ Здравствуй, друг мой. Я Мастер игры, и я проведу тебя через замечательное приключение! 
                        Скажи, ты хочешь, чтобы я придумал сеттинг для игры, или это сделаешь ты?'''.split()), markup
    elif state == 'S_GEN_HERO':
        markup.add( types.KeyboardButton("◀️ Назад"),
                    types.KeyboardButton("🎭 Дополни"),
                    types.KeyboardButton("✏️ Я сам!"),
                    types.KeyboardButton("🎲 Создай героя!"))
        return ' '.join('''🧙‍♂️ Что ж, этот мир выглядит неплохо, как думаешь? 🤔 Пора перейти к созданию героя. 
                        Ты сам его опишешь, или мне? Впрочем, может быть тебе не понравился мир?'''.split()), markup
    elif state == 'S_SELECT_QST':    
        markup.add( types.KeyboardButton("◀️ Назад"),
                    types.KeyboardButton("⚜️ Вперед!"),
                    types.KeyboardButton("📕 Журнал"))
        return "🧙‍♂️ Интересный герой... Оставляем его? 🤭 Если да, то приключения ждут тебя!", markup
    elif state == 'S_IN_QUEST':
        markup.add( types.KeyboardButton("🆕 В начало"),
                    types.KeyboardButton("🎲 Reroll"),
                    types.KeyboardButton("📕 Журнал"))
        return "🧙‍♂️ Вперед к приключениям! ⚔️Готовься...", markup


def state_send(chat_id, state):
    set_db_fild(chat_id,'state',state)
    txt, markup = get_txt_mkp(state) 
    bot.send_message(chat_id, txt, reply_markup=markup)

#--------------------- Main section ------------------------

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        if q:
            message = q.popleft()
            state = get_current_state(message.chat.id)
            if state == 'S_START':
                if message.text == '🎲 Случайный':
                    send_setting(message.chat.id, chat.answer(Gens.sett()))
                    state_send(message.chat.id,'S_GEN_HERO')
                elif message.text == '🎭 Дополни...':
                    set_db_fild(message.chat.id,'state','S_COMBO_SETT')
                    bot.send_message(message.chat.id, '🧙‍♂️ Хорошо, напиши ключевые моменты, а я разовью тему.💫')
                elif message.text == '✏️ Сам опишу...':
                    set_db_fild(message.chat.id,'state','S_ENTER_SETT')
                    bot.send_message(message.chat.id, '🧙‍♂️ Хорошо, расскажи мне в каком мире нам предстоит приключение.🌏')
                else:
                    _, markup = get_txt_mkp(state) 
                    bot.send_message(message.chat.id, "Здесь нужно использовать кнопки. 🤭", reply_markup=markup)                   
            elif state == 'S_COMBO_SETT':
                prompt = Gens.sett(translator.translate(message.text).text)
                send_setting(message.chat.id,chat.answer(prompt))
                state_send(message.chat.id,'S_GEN_HERO')
            elif state == 'S_ENTER_SETT':
                en_txt = translator.translate(message.text).text
                send_setting(message.chat.id, en_txt, message.text)   
                state_send(message.chat.id,'S_GEN_HERO')
            elif state == 'S_GEN_HERO':
                if message.text == '◀️ Назад':
                    state_send(message.chat.id,'S_START')
                elif message.text == '🎲 Создай героя!':
                    sett = get_db_fild(message.chat.id,'setting')
                    send_hero(message.chat.id,sett,chat.answer(Gens.hero(sett)))
                    state_send(message.chat.id,'S_SELECT_QST')
                elif message.text == '🎭 Дополни':
                    set_db_fild(message.chat.id,'state','S_COMBO_HERO')
                    bot.send_message(message.chat.id, '🧙‍♂️ Хорошо, давай вводные, какой он? 👨🏻‍🎤 Я подхвачу! ')                
                elif message.text == '✏️ Я сам!':
                    set_db_fild(message.chat.id,'state','S_ENTER_HERO')
                    bot.send_message(message.chat.id, '🧙‍♂️ Хорошо, расскажи про своего персонажа.🎭 Незабудь про имя!')
                else:
                    _, markup = get_txt_mkp(state) 
                    bot.send_message(message.chat.id, "Здесь нужно использовать кнопки. 🤭", reply_markup=markup)
            elif state == 'S_COMBO_HERO':
                sett = get_db_fild(message.chat.id,'setting')
                prompt = Gens.hero(sett, translator.translate(message.text).text)
                send_hero(message.chat.id,sett,chat.answer(prompt))
                state_send(message.chat.id,'S_SELECT_QST')
            elif state == 'S_ENTER_HERO':
                en_txt = translator.translate(message.text).text
                sett = get_db_fild(message.chat.id, 'setting')
                send_hero(message.chat.id, sett, en_txt, message.text)  
                state_send(message.chat.id,'S_SELECT_QST')
            elif state == 'S_SELECT_QST':
                if message.text == '◀️ Назад':
                    state_send(message.chat.id,'S_GEN_HERO')
                elif message.text == '⚜️ Вперед!':
                    state_send(message.chat.id,'S_IN_QUEST')
                    main_phase(message.chat.id)
                elif message.text == '📕 Журнал':
                    game_card(message.chat.id)
                else:
                    _, markup = get_txt_mkp(state) 
                    bot.send_message(message.chat.id, "Здесь нужно использовать кнопки. 🤭", reply_markup=markup)
            elif state == 'S_IN_QUEST':
                if message.text == '🆕 В начало':
                    set_db_fild(message.chat.id,'curent_scene', 1)
                    state_send(message.chat.id,'S_START')
                elif message.text == '🎲 Reroll':
                    sc = get_db_fild(message.chat.id,'curent_scene')
                    if len(get_db_list(message.chat.id,'scene_ls'))>=int(sc):
                        roll_back_scene(message.chat.id)
                    main_phase(message.chat.id, None if sc=="1" else sc)
                elif message.text == '📕 Журнал':
                    game_card(message.chat.id)
                else:
                    app_db_list(message.chat.id, 'pl_act', translator.translate(message.text).text)
                    quest_roll(message.chat.id)                        
            else:
                debug_mesage(message)
        else:
           time.sleep(1)
