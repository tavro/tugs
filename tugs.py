import subprocess
import random
import string
import json
import os
import time

CONFIG_FILE = 'git_helper_config.json'


def load_project_name():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config.get('project_name', '')
    return ''


def save_project_name(project_name):
    with open(CONFIG_FILE, 'w') as file:
        json.dump({'project_name': project_name}, file)


def set_project_name():
    project_name = input("\033[1;34mEnter the project name:\033[0m ").strip().upper().replace(" ", "_")
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
    ticket_number = input("\033[1;34mEnter the ticket number (or press enter to generate a random string):\033[0m ").strip()
    commit_message = input("\033[1;34mEnter the commit message:\033[0m ").strip()
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

    print("\n\033[1;34mCommit categories:\033[0m")
    for num, (emoji, category) in emojis.items():
        print(f"{num}. {emoji} {category}")

    choice = input("\033[1;34mChoose a commit category by number (1-6) or enter 7 to include your own emoji:\033[0m ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if choice in emojis:
            return emojis[choice]
        elif choice == 7:
            emoji = input("\033[1;34mEnter your own emoji:\033[0m ").strip()
            category = input("\033[1;34mEnter the category:\033[0m ").strip()
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
    while True:
        time.sleep(1)
        after = dict([(f, None) for f in os.listdir(path)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            print(f"\033[1;33mAdded: {', '.join(added)}\033[0m")
        if removed:
            print(f"\033[1;33mRemoved: {', '.join(removed)}\033[0m")
        before = after


def main():
    project_name = load_project_name() or set_project_name()
    print(f"\n\033[1;36mCurrent Project: {project_name}\033[0m")

    while True:
        print("\n\033[1;34mThe Ultimate Git Script:\033[0m")
        print("1. Add, Commit and Push")
        print("2. Set Project Name")
        print("3. Exit")
        choice = input("\033[1;34mChoose an option:\033[0m ").strip()

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
    import threading
    watcher_thread = threading.Thread(target=watch_directory, daemon=True)
    watcher_thread.start()
    main()
