# The Ultimate Git Script

This script simplifies the process of managing feature branches in your Git repository while keeping your Trello board up to date. Simply run the script in a separate terminal at the root of your repository and let it handle the rest.

## Getting Started

### Prerequisites

- Obtain your Trello API credentials.

### Trello Configuration

To connect the script to your Trello account, create a file named `secrets.py` in the root of your repository and add the following variables:

```python
API_KEY = 'YOUR_API_KEY'
TOKEN = 'YOUR_TOKEN'
BOARD_ID = 'YOUR_BOARD_ID'
```

Replace 'YOUR_API_KEY', 'YOUR_TOKEN', and 'YOUR_BOARD_ID' with your actual Trello API key, token, and board ID.

## Known Bugs (Fixing Soon)

- Cannot move card from DOING to DONE
