from pyrogram import Client, filters  # телеграм клиент

 
import shelve  # файловая база данных
db = shelve.open('data.db', writeback=True)
 
# Создать можно на my.telegram.org
API_ID = 19269573 
API_HASH = '41a1a4b1eef8eb4caa755b5ed353ef0e'

PRIVATE_PUBLIC = 'zfdw123'
PUBLIC_PUBLIC = 'RiverNewsMoscow'
SOURCE_PUBLIC = [
    'moscowtop'
    'kim_online_rus'
    'mosmap'
    'moscowach'
    'moscowlenta'
    'DtRoad'
]
PHONE_NUMBER = '+79774047800'
 
 
# создаем клиент телеграм
app = Client("cyberpunk", api_id=API_ID, api_hash=API_HASH,
             phone_number=PHONE_NUMBER)
 
# обработчик нового сообщения
# вызывается при появлении нового поста в одном из пабликов-доноров
@app.on_message(filters.chat(SOURCE_PUBLIC))
def new_channel_post(client, message):
    # сохраняем пост в базу (функцию add_post_to_db определим потом)
    post_id = add_post_to_db(message)
 
    # пересылаем пост в скрытый паблик
    message.forward(PRIVATE_PUBLIC)
 
    # в скрытый паблик отправляем присвоенный id поста
    client.send_message(PRIVATE_PUBLIC, post_id)
    # потом для пересылки в публичный паблик админ должен отправить боту этот id
 
# функция сохранения поста в бд
# генерирует уникальный id для поста и возвратит этот id
def add_post_to_db(message):
    try:
        # генерируем уникальный id для поста, равен максимальному в базе + 1
        new_id = max(int(k) for k in db.keys()
                     if k.isdigit()) + 1
    except:
        # если постов еще нет в базе вылетит ошибка и мы попадем сюда
        # тогда id ставим = 1
        new_id = 1
 
    # запись в базу необходимой информации про пост
    # Обратите внимание, shelve поддеживает только строковые ключи
    db[str(new_id)] = {
        'username': message.chat.username,  # паблик-донор
        'message_id': message.message_id,  # внутренний id сообщения
    }
    return new_id
 
# обработчик нового сообщения из скрытого паблика
# если админ пишет в паблик `132+` это значит переслать пост с id = 132 в публичный паблик
@app.on_message(filters.chat(PRIVATE_PUBLIC)
                & filters.regex(r'\d+\+') # фильтр текста сообщения `{число}+`
                )
def post_request(client, message):
    # получаем id поста из сообщения (обрезаем "+" в конце)
    post_id = str(message.text).strip('+')
    # получаем из базы пост по этому id
    post = db.get(post_id)
    if post is None:
        # если нет в базе пишем в скрытый паблик ошибку
        client.send_message(PRIVATE_PUBLIC,
                            '`ERROR NO POST ID IN DB`')
        # и выходим
        return
 
    try:
        # по данным из базы, получаем pyrogram обьект сообщения
        msg = client.get_messages(post['username'], post['message_id'])
        # пересылаем его в паблик
        # as_copy=True значит, что мы не будем отображать паблик донор, будто это наш пост XD
        msg.forward(PUBLIC_PUBLIC, as_copy=True)
        # отправляем сообщение в скрытый паблик о успехе
        client.send_message(PRIVATE_PUBLIC, f'`SUCCESS REPOST!`')
    except Exception as e:
        # если произойдет какая-то ошибка в 3 строчках выше - сообщим админу
        client.send_message(PRIVATE_PUBLIC, f'`ERROR {e}`')
 
 
if __name__ == '__main__':
    print('Atempt to run telegrabber')
    app.run()  # эта строка запустит все обработчики
