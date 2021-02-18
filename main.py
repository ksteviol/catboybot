import requests
import json
import re
import random
import threading

with open("config.json") as conf:
    config = json.load(conf)

token = config["token"]
group = config["group"]
api = 'https://api.vk.com/method/'
version = '5.130'


def message_send(peer_id, text):
    data = {
        'random_id': '0',
        'peer_id': peer_id,
        'message': text,
        'access_token': token,
        'v': version
    }
    r = requests.post('https://api.vk.com/method/messages.send', data).json()
    print(r)


def messages_remove_chat_user(peer_id, text, from_id):
    data = {
        'peer_id': peer_id,
        'offset': '0',
        'count': '200',
        'fields': 'is_admin',
        'group_id': group,
        'access_token': token,
        'v': version
    }
    r = requests.post('https://api.vk.com/method/messages.getConversationMembers', data).json()
    print(r)
    members = r['response']
    print(members)
    for i in members["items"]:
        if i["member_id"] == from_id:
            admin = i.get('is_admin', False)
            if admin is True:
                user_id = re.findall(r'\d+', text)
                user_id = [int(i) for i in user_id]
                user_id = user_id[0]
                data = {
                    'chat_id': peer_id - 2000000000,
                    'user_id': user_id,
                    'member_id': user_id,
                    'access_token': token,
                    'v': version
                }
                r = requests.post('https://api.vk.com/method/messages.removeChatUser', data).json()
                print(r)
                if 'error' not in r:
                    message_send(peer_id, 'пользователь забанен')
                elif r['error']['error_code'] == 15:
                    message_send(peer_id, 'невозможно забанить администратора')
                elif r['error']['error_code'] == 935:
                    message_send(peer_id, 'пользователь отсутствует в чате')
                elif r['error']['error_code']:
                    message_send(peer_id, 'произошла ошибка при выполнении команды. \n'
                                          'проверьте корректность аргументов и попробуйте снова')
            else:
                message_send(peer_id, f'простите но вы не являетесь вдминистратором этого чата')


# def say_it(peer_id, text):
#     text = text.replace('!скажи ', '')
#     message_send(peer_id, text)


def timer_end(peer_id, text, from_id, first_name):
    message_send(peer_id, f'[id{from_id}|{first_name}], вы просили напомнить о\n"{text}"')


def timer(peer_id, text, from_id):
    text = text.replace('/таймер ', '')
    text = text.replace('/timer ', '')
    data = {
        'user_ids': from_id,
        'access_token': token,
        'v': version
    }
    r = requests.post('https://api.vk.com/method/users.get', data).json()['response']
    print(r)
    r = r[0]
    minutes = [int(i) for i in text.split() if i.isdigit()]
    if not minutes or (minutes[0] > 999 or minutes[0] < 1):
        message_send(peer_id, f'слишком большое значение, попробуйте снова')
    else:
        text = text.replace(str(minutes[0]) + ' ', '')
        minutes = minutes[0] * 60
        if 'секунд' in text or 'секунда' in text:
            minutes /= 60
            text = text.replace('секунда ', '')
            text = text.replace('секунд ', '')
        elif 'минут' in text or 'минута' in text:
            text = text.replace('минута ', '')
            text = text.replace('минут ', '')
        elif 'часов' in text or 'час' in text:
            minutes *= 60
            text = text.replace('часов ', '')
            text = text.replace('час ', '')
        message_send(peer_id, f'[id{from_id}|{r["first_name"]}], таймер запущен. Текст напоминания:\n"{text}"')
        t1 = threading.Timer(minutes, timer_end, (peer_id, text, from_id, r["first_name"]))
        t1.start()


def check_message(message):
    text = message['text'].lower()
    peer_id = message['peer_id']
    from_id = message['from_id']
    if '/' in text:
        if 'ban' in text or 'бан' in text:
            messages_remove_chat_user(peer_id, text, from_id)
        elif 'инфо' in text or 'инфа' in text or 'шанс' in text or 'вероятность' in text or 'info' in text:
            message_send(peer_id, f'полагаю что вероятность {random.randint(0, 100)}%')
        #    if '!скажи' in text:
        #        say_it(peer_id, text)
        elif 'timer' in text or 'таймер' in text:
            timer(peer_id, text, from_id)
        elif text == 'test':
            message_send(peer_id, 'Бот работает')
        elif text == 'help' or text == 'помощь':
            message_send(peer_id, 'список команд:\n'
                                  '/ban\n'
                                  '/info\n'
                                  '/timer\n')
            message_send(peer_id, 'Бот работает')
        else:
            message_send(peer_id, 'простите но я не знаю такой киманды...')
    elif text == 'соси':
        message_send(peer_id, 'сам соси')
    elif text == 'мяу':
        message_send(peer_id, 'мур')
    elif text == 'мур':
        message_send(peer_id, 'мяу')
    elif text == 'owo':
        message_send(peer_id, 'uwu')
    elif text == 'uwu':
        message_send(peer_id, 'owo')
    elif text == 'n':
        message_send(peer_id, 'I')
    elif text == 'e':
        message_send(peer_id, 'R')


def main():
    data = requests.get('https://api.vk.com/method/groups.getLongPollServer',
                        params={'group_id': group, 'access_token': token, 'v': version}).json()['response']
    server = data['server']
    ts = data['ts']
    key = data['key']
    while True:
        response = requests.get(
            f"{server}?act=a_check&key={key}&wait=25&mode=2&ts={ts}&version=2").json()
        if 'failed' not in response:
            ts = response['ts']
            updates = response['updates']
            for update in updates:
                if update['type'] == 'message_new':
                    message = update['object']['message']
                    print(message)
                    check_message(message)
        elif response['failed'] == 1:
            data = requests.get('https://api.vk.com/method/groups.getLongPollServer',
                                params={'group_id': group, 'access_token': token, 'v': version}).json()['response']
            ts = data['ts']
        elif response['failed'] == 2:
            data = requests.get('https://api.vk.com/method/groups.getLongPollServer',
                                params={'group_id': group, 'access_token': token, 'v': version}).json()['response']
            key = data['key']
        elif response['failed'] == 3:
            data = requests.get('https://api.vk.com/method/groups.getLongPollServer',
                                params={'group_id': group, 'access_token': token, 'v': version}).json()['response']
            key = data['key']
            ts = data['ts']


if __name__ == "__main__":
    main()
