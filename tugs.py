import subprocess
import random
import string
import json
import os
import time
import threading

from trello import LIST_NAME, fetch_cards, get_doing_list_id, get_done_list_id, get_lists, move_card_to_list, create_card

CONFIG_FILE = 'git_helper_config.json'
EMOJI_FILE = 'custom_emojis.json'
WATCH_INTERVAL = 1  # in seconds
UPSTREAM_CHECK_INTERVAL = 60  # in seconds

input_lock = threading.Lock()
input_event = threading.Event()


def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}


def save_json_file(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file)


def load_config():
    config = load_json_file(CONFIG_FILE)
    return config.get('project_name', ''), config.get('check_upstream', True)


def save_config(project_name, check_upstream):
    save_json_file(CONFIG_FILE, {'project_name': project_name, 'check_upstream': check_upstream})


def set_project_name():
    project_name = safe_input("\033[1;34mEnter the project name:\033[0m ").strip().upper().replace(" ", "_")
    check_upstream = load_json_file(CONFIG_FILE).get('check_upstream', True)
    save_config(project_name, check_upstream)
    return project_name


def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def get_current_branch():
    try:
        result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_last_commit_hash():
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return generate_random_string()


def get_commit_message(project_name):
    ticket_number = safe_input("\033[1;34mEnter the ticket number (or press enter to generate a random string):\033[0m ").strip()
    commit_message = safe_input("\033[1;34mEnter the commit message:\033[0m ").strip()
    if not ticket_number:
        ticket_number = get_last_commit_hash()
    formatted_commit_message = f"{project_name}-{ticket_number}: {commit_message}"
    return formatted_commit_message


def choose_emoji():
    emojis = {
        1: ("✨", "Feature"),
        2: ("🐛", "Fix"),
        3: ("📚", "Docs"),
        4: ("💄", "Style"),
        5: ("🔨", "Refactor"),
        6: ("🚨", "Test")
    }
    custom_emojis = load_json_file(EMOJI_FILE)

    print("\n\033[1;34mCommit categories:\033[0m")
    all_emojis = {**emojis, **custom_emojis}
    for num, (emoji, category) in all_emojis.items():
        print(f"{num}. {emoji} {category}")

    next_custom_number = max(all_emojis.keys()) + 1

    choice = safe_input(f"\033[1;34mChoose a commit category by number or enter {next_custom_number} to include your own emoji:\033[0m ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if choice in emojis:
            return emojis[choice]
        elif choice in custom_emojis:
            return custom_emojis[choice]
        elif choice == next_custom_number:
            emoji = safe_input("\033[1;34mEnter your own emoji:\033[0m ").strip()
            category = safe_input("\033[1;34mEnter the category:\033[0m ").strip()
            custom_emojis[next_custom_number] = (emoji, category)
            save_json_file(EMOJI_FILE, custom_emojis)
            return (emoji, category)
    
    return ("", "")


def add_commit_push(project_name):
    try:
        subprocess.run(['git', 'add', '--all'], check=True)
        commit_message = get_commit_message(project_name)
        emoji, category = choose_emoji()
        full_commit_message = f"{emoji} {commit_message}".strip()
        subprocess.run(['git', 'commit', '-m', full_commit_message], check=True)
        subprocess.run(['git', 'push'], check=True)
        print(f"\n\033[1;32mChanges committed and pushed successfully. Category: {category}\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\n\033[1;31mAn error occurred: {e}\033[0m")


def watch_directory(path='.'):
    before = dict([(f, None) for f in os.listdir(path)])
    current_changes = []
    while True:
        time.sleep(WATCH_INTERVAL)
        after = dict([(f, None) for f in os.listdir(path)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added or removed:
            changes = ""
            if added:
                changes += f"\033[1;33mAdded: {', '.join(added)}\033[0m\n"
            if removed:
                changes += f"\033[1;33mRemoved: {', '.join(removed)}\033[0m\n"
            current_changes.append(changes.strip())
            display_changes(current_changes)
            input_event.set()
        before = after


def display_changes(changes):
    with input_lock:
        clear_terminal()
        print("\033[1;34mCurrent Changes in Directory:\033[0m")
        for change in changes:
            print(change)
        print("\n\033[1;34mPress Enter to continue...\033[0m", end='', flush=True)


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def safe_input(prompt):
    while True:
        input_event.clear()
        with input_lock:
            user_input = input(prompt)
        if not input_event.is_set():
            return user_input
        print("\n\033[1;33mDirectory changed. Please re-enter your input.\033[0m")


def check_and_pull_upstream():
    while True:
        time.sleep(UPSTREAM_CHECK_INTERVAL)
        with input_lock:
            try:
                result = subprocess.run(['git', 'fetch'], capture_output=True, text=True, check=True)
                if result.stdout or result.stderr:
                    print("\033[1;34mChecking for updates...\033[0m")
                    result = subprocess.run(['git', 'status'], capture_output=True, text=True, check=True)
                    if "Your branch is behind" in result.stdout:
                        print("\033[1;33mUpdates found. Pulling from upstream...\033[0m")
                        subprocess.run(['git', 'pull'], check=True)
                        print("\033[1;32mRepository updated successfully.\033[0m")
            except subprocess.CalledProcessError as e:
                print(f"\n\033[1;31mAn error occurred while checking for updates: {e}\033[0m")


def pull_standing_branch():
    try:
        subprocess.run(['git', 'pull'], check=True)
        print("\033[1;32mPulled the latest changes from the upstream branch successfully.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31mAn error occurred while pulling the standing branch: {e}\033[0m")


def main():
    project_name, check_upstream = load_config()
    if not project_name:
        project_name = set_project_name()

    if check_upstream:
        threading.Thread(target=check_and_pull_upstream, daemon=True).start()

    while True:
        current_branch = get_current_branch()
        print(f"\n\033[1;36mCurrent Project: {project_name}\033[0m")
        print(f"\033[1;36mCurrent Branch: {current_branch}\033[0m")
        
        print("\n\033[1;34mThe Ultimate Git Script:\033[0m")
        print("1. Add, Commit and Push")
        print("2. Set Project Name")
        print("3. Select Trello Card and Create Branch")
        print("4. Create a New Trello Ticket")
        print("5. Merge Branch into Main and Move Trello Card to DONE")
        print(f"6. {'Disable' if check_upstream else 'Enable'} Upstream Check")
        
        if not check_upstream:
            print("7. Pull Standing Branch")
            print("8. Exit")
        else:
            print("7. Exit")
        
        choice = safe_input("\033[1;34mChoose an option:\033[0m ").strip()
        
        if choice == '1':
            add_commit_push(project_name)
        elif choice == '2':
            project_name = set_project_name()
            print(f"\n\033[1;36mCurrent Project: {project_name}\033[0m")
        elif choice == '3':
            select_trello_card_and_create_branch(project_name)
        elif choice == '4':
            create_trello_ticket()
        elif choice == '5':
            merge_branch_to_main(project_name)
        elif choice == '6':
            check_upstream = not check_upstream
            save_config(project_name, check_upstream)
            if check_upstream:
                threading.Thread(target=check_and_pull_upstream, daemon=True).start()
            print(f"\033[1;34mUpstream check {'enabled' if check_upstream else 'disabled'}.\033[0m")
        elif choice == '7' and not check_upstream:
            pull_standing_branch()
        elif choice == '7' and check_upstream or choice == '8' and not check_upstream:
            print("\033[1;34mExiting Git Helper.\033[0m")
            break
        else:
            print("\033[1;31mInvalid option. Please try again.\033[0m")


def select_trello_card_and_create_branch(project_name):
    try:
        cards = fetch_cards()
        
        print("\n\033[1;34mBacklog Cards:\033[0m")
        for idx, card in enumerate(cards, start=1):
            print(f"{idx}. {card['name']}")
        
        choice = safe_input("\033[1;34mChoose a card number to create a feature branch (or press enter to cancel):\033[0m ").strip()
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(cards):
                card = cards[idx]
                card_name = card['name']
                card_id = card['id']
                branch_name = create_branch_name(project_name, card_name)
                create_git_branch(branch_name)
                
                import secrets
                board_id = secrets.BOARD_ID
                api_key = secrets.API_KEY
                token = secrets.TOKEN
                doing_list_id = get_doing_list_id(board_id, api_key, token)
                move_card_to_list(card_id, doing_list_id, api_key, token)
                print(f"\033[1;32mMoved card '{card_name}' to the 'DOING' list.\033[0m")
            else:
                print("\033[1;31mInvalid card number.\033[0m")
        elif choice == '':
            return
        else:
            print("\033[1;31mInvalid input.\033[0m")
    
    except Exception as e:
        print(f"\033[1;31mAn error occurred: {e}\033[0m")


def create_branch_name(project_name, card_name):
    card_number = card_name.split(':')[0].strip()
    card_name_slug = '-'.join(card_name.split(':')[1].strip().split()).lower()
    return f"{project_name}-{card_number}-{card_name_slug}"


def create_git_branch(branch_name):
    try:
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
        subprocess.run(['git', 'push', '--set-upstream', 'origin', branch_name], check=True)
        print(f"\033[1;32mCreated branch '{branch_name}' and pushed to remote successfully.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31mAn error occurred: {e}\033[0m")


def create_trello_ticket():
    try:
        import secrets
        board_id = secrets.BOARD_ID
        api_key = secrets.API_KEY
        token = secrets.TOKEN
        
        lists = get_lists(board_id, api_key, token)
        todo_list = next((lst for lst in lists if lst['name'] == LIST_NAME), None)
        
        if not todo_list:
            print(f"\033[1;31mNo list named '{LIST_NAME}' found on board.\033[0m")
            return
        
        ticket_name = safe_input("\033[1;34mEnter the ticket name:\033[0m ").strip()
        ticket_desc = safe_input("\033[1;34mEnter the ticket description:\033[0m ").strip()
        
        if not ticket_name:
            print("\033[1;31mTicket name cannot be empty.\033[0m")
            return
        
        create_card(todo_list['id'], ticket_name, ticket_desc, api_key, token)
        print(f"\033[1;32mTicket '{ticket_name}' created successfully in the TODO list.\033[0m")
    except Exception as e:
        print(f"\033[1;31mAn error occurred: {e}\033[0m")


def merge_branch_to_main(project_name):
    try:
        current_branch = get_current_branch()
        if current_branch == 'main':
            print("\033[1;31mYou are already on the main branch.\033[0m")
            return

        subprocess.run(['git', 'checkout', 'main'], check=True)
        subprocess.run(['git', 'merge', current_branch], check=True)
        subprocess.run(['git', 'push'], check=True)

        subprocess.run(['git', 'branch', '-d', current_branch], check=True)
        subprocess.run(['git', 'push', 'origin', '--delete', current_branch], check=True)

        add_commit_push(project_name)

        import secrets
        board_id = secrets.BOARD_ID
        api_key = secrets.API_KEY
        token = secrets.TOKEN

        cards = fetch_cards()
        card = next((card for card in cards if create_branch_name(project_name, card['name']) == current_branch), None)

        if card:
            done_list_id = get_done_list_id(board_id, api_key, token)
            move_card_to_list(card['id'], done_list_id, api_key, token)
            print(f"\033[1;32mMoved card '{card['name']}' to the 'DONE' list.\033[0m")
        else:
            print("\033[1;31mNo matching card found for the current branch.\033[0m")

        print(f"\033[1;32mBranch '{current_branch}' merged into 'main' and pushed successfully.\033[0m")
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31mAn error occurred during the merge process: {e}\033[0m")
    except Exception as e:
        print(f"\033[1;31mAn unexpected error occurred: {e}\033[0m")



if __name__ == "__main__":
    watcher_thread = threading.Thread(target=watch_directory, daemon=True)
    watcher_thread.start()
    main()
