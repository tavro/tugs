import subprocess
import random
import string
import json
import os
import time
import threading

CONFIG_FILE = 'git_helper_config.json'
EMOJI_FILE = 'custom_emojis.json'
WATCH_INTERVAL = 1  # in seconds

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


def load_project_name():
    config = load_json_file(CONFIG_FILE)
    return config.get('project_name', '')


def save_project_name(project_name):
    save_json_file(CONFIG_FILE, {'project_name': project_name})


def set_project_name():
    project_name = safe_input("\033[1;34mEnter the project name:\033[0m ").strip().upper().replace(" ", "_")
    save_project_name(project_name)
    return project_name


def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


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
    for num, (emoji, category) in {**emojis, **custom_emojis}.items():
        print(f"{num}. {emoji} {category}")

    choice = safe_input("\033[1;34mChoose a commit category by number or enter 7 to include your own emoji:\033[0m ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if choice in emojis:
            return emojis[choice]
        elif choice in custom_emojis:
            return custom_emojis[choice]
        elif choice == 7:
            emoji = safe_input("\033[1;34mEnter your own emoji:\033[0m ").strip()
            category = safe_input("\033[1;34mEnter the category:\033[0m ").strip()
            custom_emojis[choice] = (emoji, category)
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


def main():
    project_name = load_project_name() or set_project_name()
    print(f"\n\033[1;36mCurrent Project: {project_name}\033[0m")

    while True:
        print("\n\033[1;34mThe Ultimate Git Script:\033[0m")
        print("1. Add, Commit and Push")
        print("2. Set Project Name")
        print("3. Exit")
        choice = safe_input("\033[1;34mChoose an option:\033[0m ").strip()

        if choice == '1':
            add_commit_push(project_name)
        elif choice == '2':
            project_name = set_project_name()
            print(f"\n\033[1;36mCurrent Project: {project_name}\033[0m")
        elif choice == '3':
            print("\033[1;34mExiting Git Helper.\033[0m")
            break
        else:
            print("\033[1;31mInvalid option. Please try again.\033[0m")


if __name__ == "__main__":
    watcher_thread = threading.Thread(target=watch_directory, daemon=True)
    watcher_thread.start()
    main()
