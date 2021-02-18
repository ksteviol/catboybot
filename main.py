import requests
import yaml
import re
import random
import threading

with open("config.yaml") as conf:
    config = yaml.safe_load(conf)

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


def data_update(peer_id):
    data_file = open(f"{peer_id}.yaml", "a+")
    data_file.write


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
                id = re.findall(r'\d+', text)
                id = [int(i) for i in id]
                data = {
                    'chat_id': peer_id - 2000000000,
                    'user_id': id[0],
                    'member_id': id[0],
                    'access_token': token,
                    'v': version
                }
                r = requests.post('https://api.vk.com/method/messages.removeChatUser', data).json()
                print(r)
                message_send(peer_id, 'Пользователь забанен')
            else:
                message_send(peer_id, f'неа')


# def say_it(peer_id, text):
#     text = text.replace('!скажи ', '')
#     message_send(peer_id, text)


def timer_end(peer_id, text, from_id, first_name):
    message_send(peer_id, f'[id{from_id}|{first_name}], вы просили напомнить о "{text} "')


def timer(peer_id, text, from_id):
    text = text.replace('!таймер ', '')
    text = text.replace('!timer ', '')
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
        text = text.replace(str(minutes[0]), '')
        if 'секунд' in text or 'секунда' in text:
            minutes[0] /= 60
            text = text.replace('секунда', '')
            text = text.replace('секунд', '')
        elif 'минут' in text or 'минута' in text:
            text = text.replace('минута', '')
            text = text.replace('минут', '')
        elif 'часов' in text or 'час' in text:
            minutes[0] *= 60
            text = text.replace('минута', '')
            text = text.replace('минут', '')
        message_send(peer_id, f'[id{from_id}|{r["first_name"]}], таймер запущен. Текст напоминания: "{text} "')
        t1 = threading.Timer(minutes[0], timer_end, (peer_id, text, from_id, r["first_name"]))
        t1.start()


def check_message(message):
    text = message['text'].lower()
    peer_id = message['peer_id']
    from_id = message['from_id']
    if '!ban' in text:
        messages_remove_chat_user(peer_id, text, from_id)
    if '!инфо' in text or '!инфа' in text or '!шанс' in text or '!вероятность' in text or '!info' in text:
        message_send(peer_id, f'полагаю что вероятность {random.randint(0, 100)}%')
    #    if '!скажи' in text:
    #        say_it(peer_id, text)
    if '!timer' in text or '!таймер' in text:
        timer(peer_id, text, from_id)
    if text == '!test':
        message_send(peer_id, 'Бот работает')
    if text == '!help' or text == '!помощь':
        message_send(peer_id, 'список команд:\n'
                              '!ban\n'
                              '!info\n'
                              '!timer\n')
        message_send(peer_id, 'Бот работает')
    if text == 'соси':
        message_send(peer_id, 'сам соси')
    if text == 'мяу':
        message_send(peer_id, 'мур')
    if text == 'мур':
        message_send(peer_id, 'мяу')
    if text == 'owo':
        message_send(peer_id, 'uwu')
    if text == 'uwu':
        message_send(peer_id, 'owo')
    if text == 'n':
        message_send(peer_id, 'I')
    if text == 'e':
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
            ts = response['ts']
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
