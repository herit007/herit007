import sys
import json
import os
import re

BOARD_FILE = "data/connect4.json"
README_FILE = "README.md"
ROWS = 6
COLS = 7

def load_board():
    if os.path.exists(BOARD_FILE):
        with open(BOARD_FILE, "r") as f:
            return json.load(f)
    return {"board": [[0]*COLS for _ in range(ROWS)], "turn": 1, "winner": 0, "last_move": None}

def save_board(data):
    os.makedirs("data", exist_ok=True)
    with open(BOARD_FILE, "w") as f:
        json.dump(data, f)

def check_winner(board):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] != 0 and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return board[r][c]
    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] != 0 and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return board[r][c]
    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if board[r][c] != 0 and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]
    # Diagonal \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] != 0 and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]
    return 0

def make_move(data, col):
    if data["winner"] != 0: return False
    if col < 0 or col >= COLS: return False

    for r in range(ROWS-1, -1, -1):
        if data["board"][r][col] == 0:
            data["board"][r][col] = data["turn"]
            data["last_move"] = (r, col)
            data["winner"] = check_winner(data["board"])
            data["turn"] = 2 if data["turn"] == 1 else 1
            return True
    return False

def render_board(data):
    symbols = {0: "⚪", 1: "🔴", 2: "🟡"}
    res = "<!-- BEGIN CONNECT4 BOARD -->\n"
    res += "| 1 | 2 | 3 | 4 | 5 | 6 | 7 |\n"
    res += "|---|---|---|---|---|---|---|\n"
    for r in range(ROWS):
        line = "| " + " | ".join(symbols[cell] for cell in data["board"][r]) + " |"
        res += line + "\n"

    if data["winner"] == 0:
        turn_color = '🔴' if data['turn'] == 1 else '🟡'
        res += f"\n**Current Turn:** {turn_color}\n\n"
        res += "Drop a disc: "
        links = []
        for c in range(COLS):
            if data["board"][0][c] == 0:
                links.append(f"[Column {c+1}](https://github.com/herit007/herit007/issues/new?title=Connect4:+Drop+{c+1}&body=Just+click+'Submit+new+issue'+to+make+your+move!)")
            else:
                links.append(f"Full")
        res += " | ".join(links)
    else:
        res += f"\n🎉 **Winner: {'🔴 Red' if data['winner'] == 1 else '🟡 Yellow'}!**\n"
        res += f"[Start New Game](https://github.com/herit007/herit007/issues/new?title=Connect4:+New+Game)\n"

    res += "\n<!-- END CONNECT4 BOARD -->"
    return res

def main():
    title = os.getenv("ISSUE_TITLE", "")
    data = load_board()

    if "New Game" in title:
        data = {"board": [[0]*COLS for _ in range(ROWS)], "turn": 1, "winner": 0, "last_move": None}
    else:
        match = re.search(r"Drop (\d)", title)
        if match:
            col = int(match.group(1)) - 1
            make_move(data, col)

    save_board(data)
    board_html = render_board(data)

    with open(README_FILE, "r") as f:
        content = f.read()

    new_content = re.sub(r"<!-- BEGIN CONNECT4 BOARD -->.*?<!-- END CONNECT4 BOARD -->", board_html, content, flags=re.DOTALL)

    with open(README_FILE, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()
