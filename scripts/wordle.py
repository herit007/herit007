import os
import json
import re
import random

STATE_FILE = "data/wordle.json"
README_FILE = "README.md"
WORD_LIST = ["DATA", "CODE", "SQL", "PYTHON", "MLOPS", "TABLE", "QUERY", "MODEL", "CLOUD", "AI", "SPARK", "GRAPH", "KPI", "CHURN"]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return reset_game()

def reset_game():
    word = random.choice(WORD_LIST).upper()
    state = {"target": word, "guesses": [], "game_over": False, "winner": False}
    save_state(state)
    return state

def save_state(state):
    os.makedirs("data", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def get_feedback(target, guess):
    result = []
    target_list = list(target)
    guess_list = list(guess)

    # First pass: Green
    feedback = ["⬛"] * len(guess)
    for i in range(min(len(target), len(guess))):
        if guess_list[i] == target_list[i]:
            feedback[i] = "🟩"
            target_list[i] = None
            guess_list[i] = None

    # Second pass: Yellow
    for i in range(len(guess)):
        if guess_list[i] is not None:
            if guess_list[i] in target_list:
                feedback[i] = "🟨"
                target_list[target_list.index(guess_list[i])] = None

    return "".join(feedback)

def render_board(state):
    res = "<!-- BEGIN WORDLE BOARD -->\n"
    res += f"### 🧩 Data Wordle\n"
    res += "Guess the hidden data-related word!\n\n"

    for guess in state["guesses"]:
        feedback = get_feedback(state["target"], guess)
        res += f"` { ' '.join(list(guess)) } ` {feedback}\n\n"

    if not state["game_over"]:
        res += f"Tries remaining: {6 - len(state['guesses'])}\n\n"
        res += "Submit your 3-6 letter guess by [opening a new issue](https://github.com/herit007/herit007/issues/new?title=Wordle:+Guess+<YOUR_WORD>&body=Just+replace+<YOUR_WORD>+with+your+guess+and+submit!).\n"
    else:
        if state["winner"]:
            res += f"🎉 **You got it! The word was {state['target']}!**\n"
        else:
            res += f"❌ **Game Over! The word was {state['target']}.**\n"
        res += f"\n[Start New Game](https://github.com/herit007/herit007/issues/new?title=Wordle:+New+Game)\n"

    res += "\n<!-- END WORDLE BOARD -->"
    return res

def main():
    title = os.getenv("ISSUE_TITLE", "")
    state = load_state()

    if "New Game" in title:
        state = reset_game()
    else:
        match = re.search(r"Guess ([a-zA-Z]+)", title)
        if match:
            guess = match.group(1).upper()
            if guess not in state["guesses"] and not state["game_over"]:
                state["guesses"].append(guess)
                if guess == state["target"]:
                    state["game_over"] = True
                    state["winner"] = True
                elif len(state["guesses"]) >= 6:
                    state["game_over"] = True

    save_state(state)
    board_html = render_board(state)

    with open(README_FILE, "r") as f:
        content = f.read()

    new_content = re.sub(r"<!-- BEGIN WORDLE BOARD -->.*?<!-- END WORDLE BOARD -->", board_html, content, flags=re.DOTALL)

    with open(README_FILE, "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()
