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
