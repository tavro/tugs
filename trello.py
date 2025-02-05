import requests
import secrets

SECRETS_FILE = 'secrets.py'
LIST_NAME = 'TODO'


def get_lists(board_id, api_key, token):
    url = f'https://api.trello.com/1/boards/{board_id}/lists'
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_cards(list_id, api_key, token):
    url = f'https://api.trello.com/1/lists/{list_id}/cards'
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def fetch_doing_cards():
    board_id = secrets.BOARD_ID
    api_key = secrets.API_KEY
    token = secrets.TOKEN

    lists = get_lists(board_id, api_key, token)
    doing_list = next((lst for lst in lists if lst['name'] == 'DOING'), None)

    if not doing_list:
        raise ValueError(f"No list named '{LIST_NAME}' found on board.")

    cards = get_cards(doing_list['id'], api_key, token)
    return cards


def fetch_cards():
    board_id = secrets.BOARD_ID
    api_key = secrets.API_KEY
    token = secrets.TOKEN

    lists = get_lists(board_id, api_key, token)
    todo_list = next((lst for lst in lists if lst['name'] == LIST_NAME), None)

    if not todo_list:
        raise ValueError(f"No list named '{LIST_NAME}' found on board.")

    cards = get_cards(todo_list['id'], api_key, token)
    return cards


def get_doing_list_id(board_id, api_key, token):
    url = f'https://api.trello.com/1/boards/{board_id}/lists'
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    lists = response.json()
    doing_list = next((lst for lst in lists if lst['name'].upper() == 'DOING'), None)
    if not doing_list:
        raise ValueError("No list named 'DOING' found on board.")
    return doing_list['id']


def move_card_to_list(card_id, list_id, api_key, token):
    url = f'https://api.trello.com/1/cards/{card_id}/idList'
    params = {
        'key': api_key,
        'token': token,
        'value': list_id
    }
    response = requests.put(url, params=params)
    response.raise_for_status()
    return response.json()


def create_card(list_id, name, desc, api_key, token):
    url = 'https://api.trello.com/1/cards'
    params = {
        'idList': list_id,
        'name': name,
        'desc': desc,
        'key': api_key,
        'token': token
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()


def get_done_list_id(board_id, api_key, token):
    url = f'https://api.trello.com/1/boards/{board_id}/lists'
    params = {
        'key': api_key,
        'token': token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    lists = response.json()
    done_list = next((lst for lst in lists if lst['name'].upper() == 'DONE'), None)
    if not done_list:
        raise ValueError("No list named 'DONE' found on board.")
    return done_list['id']


def get_cards(list_id, api_key, token):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {
        'key': api_key,
        'token': token
    }

    response = requests.get(url, params=query)
    response.raise_for_status()

    return response.json()