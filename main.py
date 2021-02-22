import requests
import json
import re
import random
import threading
import os

with open("config.json") as conf:
    config = json.load(conf)
1123

token = config["token"]
group = config["group"]
api = 'https://api.vk.com/method/'
version = '5.130'
chats_path = os.getcwd() + r"\chats_config"
print(chats_path)


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


def update_chat_settings(record_type, record, peer_id):
    chat_path = chats_path + f"\\{str(peer_id)}.json"
    if record_type == 'register_chat':
        folder_path = os.path.dirname(chat_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        data = {
            'peer_id': record,
            'owner': [],
            'muted': [],
            'banned': [],
            'rank1': [],
            'rank2': [],
            'rank3': [],
            'rank4': [],
            'rank5': [],
            'admins': []
        }
        with open(chat_path, 'w') as write_chat_settings:
            json.dump(data, write_chat_settings, indent=4)
        return True
    with open(chat_path, 'r') as read_chat_settings:
        data = json.load(read_chat_settings)
        if record_type == 'owner':
            if record not in data['owner']:
                data['owner'].append(str(record))
            elif record in data['owner']:
                return []
        if record_type == 'rank1':
            if record not in data['rank1']:
                data['rank1'].append(str(record))
            elif record in data['rank1']:
                message_send(peer_id, 'пользователь уже имеет этот ранг')
        if record_type == 'rank2':
            if record not in data['rank2']:
                data['rank2'].append(str(record))
            elif record in data['rank2']:
                message_send(peer_id, 'пользователь уже имеет этот ранг')
        if record_type == 'rank3':
            if record not in data['rank3']:
                data['rank3'].append(str(record))
            elif record in data['rank3']:
                message_send(peer_id, 'пользователь уже имеет этот ранг')
        if record_type == 'rank4':
            if record not in data['rank4']:
                data['rank4'].append(str(record))
            elif record in data['rank4']:
                message_send(peer_id, 'пользователь уже имеет этот ранг')
        if record_type == 'rank5':
            if record not in data['rank5']:
                data['rank5'].append(str(record))
            elif record in data['rank5']:
                message_send(peer_id, 'пользователь уже имеет этот ранг')
        if record_type == 'ban':
            if record not in data['banned']:
                data['banned'].remove(str(record))
            elif record in data['banned']:
                message_send(peer_id, 'пользователь уже забанен')
        if record_type == 'mute':
            if record not in data['muted']:
                data['muted'].append(str(record))
            elif record in data['muted']:
                message_send(peer_id, 'пользователь уже в муте')
                return False
        if record_type == 'unban':
            if record in data['banned']:
                data['banned'].remove(str(record))
            elif record not in data['banned']:
                message_send(peer_id, 'у пользователя нет бана')
        if record_type == 'unmute':
            if record in data['muted']:
                data['muted'].remove(str(record))
            elif record not in data['muted']:
                message_send(peer_id, 'у пользователя нет мута')
                return False
        if record_type == 'admins':
            data['admins'].append(str(record))
    with open(chat_path, 'w') as write_chat_settings:
        json.dump(data, write_chat_settings, indent=4)


def check_admin(peer_id, user_id):
    chat_path = chats_path + f"\\{str(peer_id)}.json"
    with open(chat_path, 'r') as read_chat_settings:
        data = json.load(read_chat_settings)
    if str(user_id) in data['rank5'] or str(user_id) in data['admins']:
        return True


def check_ban(peer_id, user_id, from_id):
    chat_path = chats_path + f"\\{str(peer_id)}.json"
    with open(chat_path, 'r') as read_chat_settings:
        data = json.load(read_chat_settings)
    if str(user_id) in data['banned']:
        if not check_admin(peer_id, from_id) is True:
            remove_chat_user(peer_id, 0, user_id, 'autoban')
        else:
            message_send(peer_id, 'администратор пригласил забаненного участника\n'
                                  'удалаю его из бан листа')
            update_chat_settings('unban', user_id, peer_id)


def update_chat_admins(peer_id):
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
    if 'error' not in r:
        members = r['response']
        print(members)
        chat_path = chats_path + f"\\{str(peer_id)}.json"
        with open(chat_path, 'r') as read_chat_settings:
            data = json.load(read_chat_settings)
            data['admins'] = []
        with open(chat_path, 'w') as write_chat_settings:
            json.dump(data, write_chat_settings, indent=4)
        for i in members["items"]:
            if 'is_admin' in i:
                print(i)
                update_chat_settings('admins', i["member_id"], peer_id)
                if 'is_owner' in i:
                    update_chat_settings('owner', i["member_id"], peer_id)
        message_send(peer_id, 'список администраторов беседы обновлён')
    elif 'error' in r:
        message_send(peer_id, 'я не могу выполнить данную команду без прав администратора')


def check_mute(peer_id, user_id, conversation_message_id):
    try:
        chat_path = chats_path + f"\\{str(peer_id)}.json"
        with open(chat_path, 'r') as read_chat_settings:
            data = json.load(read_chat_settings)
        if str(user_id) in data['muted']:
            remove_chat_user(peer_id, '0', user_id, 'muteban')
    except FileNotFoundError:
        return []


def remove_chat_user(peer_id, text, from_id, type):
    if text == '0':
        data = {
            'chat_id': peer_id - 2000000000,
            'user_id': from_id,
            'member_id': from_id,
            'access_token': token,
            'v': version
        }
        r = requests.post('https://api.vk.com/method/messages.removeChatUser', data).json()
        print(r)
        if type == "autoban":
            message_send(peer_id, 'пользователь забанен в данной беседе')
        elif type == 'muteban':
            message_send(peer_id, 'нарушен срок молчания\n'
                                  'пользователь удален')
            update_chat_settings('unmute', from_id, peer_id)
            update_chat_settings('ban', from_id, peer_id)
        return True
    elif check_admin(peer_id, from_id) is True:
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
            if type == 'ban':
                message_send(peer_id, 'пользователь забанен')
                update_chat_settings('ban', user_id, peer_id)
            if type == 'kick':
                message_send(peer_id, 'пользователь исключен')
        elif r['error']['error_code'] == 15:
            message_send(peer_id, 'невозможно забанить администратора')
        elif r['error']['error_code'] == 935:
            message_send(peer_id, 'пользователь отсутствует в чате')
        elif r['error']['error_code'] == 917:
            message_send(peer_id, 'я не могу выполнить данную команду без прав администратора')
        elif r['error']['error_code']:
            message_send(peer_id, 'произошла ошибка при выполнении команды. \n'
                                  'проверьте корректность аргументов и попробуйте снова')
    else:
        message_send(peer_id, f'простите но вы не являетесь администратором этого чата')


def mute_end(peer_id, text, user_id, first_name):
    message_send(peer_id, f'[id{user_id}|{first_name}], срок действия мута окончен')
    update_chat_settings('unmute', user_id, peer_id)


def mute_chat_user(peer_id, from_id, text, key):
    if check_admin(peer_id, from_id) is True:
        print(text)
        user_id = re.findall(r'\d+', text)
        user_id = [int(i) for i in user_id if i.isdigit()]
        minutes = user_id[1]
        user_id = user_id[0]
        print(user_id)
        print(minutes)
        if check_admin(peer_id, user_id) is True:
            message_send(peer_id, 'невозможно выдать мут старшему администратору')
        else:
            data = {
                'user_ids': user_id,
                'access_token': token,
                'v': version
            }
            r = requests.post('https://api.vk.com/method/users.get', data).json()['response']
            print(r)
            r = r[0]
            if not minutes or (minutes > 999 or minutes < 1):
                message_send(peer_id, f'слишком большое значение, попробуйте снова')
            else:
                if update_chat_settings('mute', str(user_id), peer_id):
                    minutes = minutes * 60
                    if 'секунд' in text or 'секунда' in text:
                        minutes /= 60
                    elif 'часов' in text or 'час' in text:
                        minutes *= 60
                    elif 'дней' in text or 'дня' in text or 'день' in text:
                        minutes *= 1440
                    message_send(peer_id, f'[id{user_id}|{r["first_name"]}], вы в муте...')
                    global t1
                    t1 = threading.Timer(minutes, mute_end, (peer_id, text, user_id, r["first_name"]))
                    t1.start()



def unmute_chat_user(peer_id, from_id, text, key):
    user_id = re.findall(r'\d+', text)
    user_id = [int(i) for i in user_id if i.isdigit()]
    user_id = user_id[0]
    if check_admin(peer_id, from_id) is True:
        if update_chat_settings('unmute', str(user_id), peer_id):
            data = {
                'user_ids': user_id,
                'access_token': token,
                'v': version
            }
            r = requests.post('https://api.vk.com/method/users.get', data).json()['response']
            print(r)
            r = r[0]
            message_send(peer_id, f'[id{user_id}|{r["first_name"]}], ')
    elif key == 'auto':
        update_chat_settings('unmute', user_id, peer_id)


def unban_chat_user(peer_id, from_id, text, key):
    user_id = re.findall(r'\d+', text)
    user_id = [int(i) for i in user_id if i.isdigit()]
    user_id = user_id[0]
    if check_admin(peer_id, from_id) is True:
        update_chat_settings('unban', user_id, peer_id)
        data = {
            'user_ids': user_id,
            'access_token': token,
            'v': version
        }
        r = requests.post('https://api.vk.com/method/users.get', data).json()['response']
        print(r)
        r = r[0]
        message_send(peer_id, f'[id{user_id}|{r["first_name"]}], ')
    elif key == 'auto':
        update_chat_settings('unban', user_id, peer_id)


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
    check_mute(message['peer_id'], message['from_id'], message['conversation_message_id'])
    text = message['text'].lower()
    peer_id = message['peer_id']
    from_id = message['from_id']
    text = text.replace('.', '')
    if '/' in text:
        if 'кик' in text or 'kick' in text:
            remove_chat_user(peer_id, text, from_id, 'kick')
        elif 'разбан' in text or 'unban' in text:
            unban_chat_user(peer_id, text, from_id, [])
        elif 'размут' in text or 'unmute' in text:
            unmute_chat_user(peer_id, from_id, text, [])
        elif 'бан' in text or 'ban' in text:
            remove_chat_user(peer_id, text, from_id, 'ban')
        elif 'мут' in text or 'mute' in text:
            mute_chat_user(peer_id, from_id, text, '0')

        elif 'инфо' in text or 'инфа' in text or 'шанс' in text or 'вероятность' in text or 'info' in text:
            message_send(peer_id, f'полагаю что вероятность {random.randint(0, 100)}%')
        #    if '!скажи' in text:
        #        say_it(peer_id, text)
        elif 'timer' in text or 'таймер' in text:
            timer(peer_id, text, from_id)
        elif 'test' in text:
            message_send(peer_id, 'Бот работает')
        elif 'help' in text or 'помощь' in text:
            message_send(peer_id, 'nyi')
        elif 'update_admins' in text:
            update_chat_admins(peer_id)
        elif 'register_chat' in text:
            update_chat_settings('register_chat', peer_id, peer_id)
        else:
            message_send(peer_id, 'простите но я не знаю такой команды...')
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
        print(response)
        if 'failed' not in response:
            ts = response['ts']
            updates = response['updates']
            for update in updates:
                if update['type'] == 'message_new':
                    message = update['object']['message']
                    print(message)
                    if not 'action' in message:
                        check_message(message)
                    elif 'action' in message:
                        if message['action']['type'] == 'chat_invite_user':
                            if message['action']['member_id'] == (0 - int(group)):
                                message_send(message['peer_id'], 'приветствую\n'
                                                                 'для полной функциональности мне нужна админка\n'
                                                                 'после того как повысите меня введите команду\n'
                                                                 '"/update" чтобы обновить конфигурацию беседы')
                                update_chat_settings('register_chat', message['peer_id'], message['peer_id'])
                            elif True:
                                check_ban(message['peer_id'], message['action']['member_id'], message['from_id'])
                            else:
                                message_send(message['peer_id'], 'добро пожаловать')
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
