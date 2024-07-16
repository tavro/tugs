import subprocess
import random
import string
import json
import os

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
    project_name = input("Enter the project name: ").strip().upper().replace(" ", "_")
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
    ticket_number = input("Enter the ticket number (or press enter to generate a random string): ").strip()
    commit_message = input("Enter the commit message: ").strip()
    if not ticket_number:
        ticket_number = get_last_commit_hash()
    formatted_commit_message = f"{project_name}-{ticket_number}: {commit_message}"
    return formatted_commit_message


def choose_emoji():
    emojis = {
        1: "✨",  # Feature
        2: "🐛",  # Fix
        3: "📚",  # Docs
        4: "💄",  # Style
        5: "🔨",  # Refactor
        6: "🚨"   # Test
    }

    print("\nCommit categories:")
    for num, emoji in emojis.items():
        print(f"{num}. {emoji}")

    choice = input("Choose a commit category by number (1-6) or enter 7 to include your own emoji: ").strip()
    
    if choice.isdigit():
        choice = int(choice)
        if choice in emojis:
            return emojis[choice]
        elif choice == 7:
            return input("Enter your own emoji: ").strip()
    
    return ""


def add_commit_push(project_name):
    try:
        subprocess.run(['git', 'add', '--all'], check=True)
        commit_message = get_commit_message(project_name)
        emoji = choose_emoji()
        full_commit_message = f"{emoji} {commit_message}".strip()
        subprocess.run(['git', 'commit', '-m', full_commit_message], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\nChanges committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred: {e}")


def main():
    project_name = load_project_name() or set_project_name()

    while True:
        print("\nThe Ultimate Git Script:")
        print("1. Add, Commit and Push")
        print("2. Set Project Name")
        print("3. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            add_commit_push(project_name)
        elif choice == '2':
            project_name = set_project_name()
        elif choice == '3':
            print("Exiting Git Helper.")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
