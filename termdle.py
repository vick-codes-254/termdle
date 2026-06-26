#!/usr/bin/env python3
"""
Termdle — a Wordle clone for your terminal.

Colored feedback, an on-screen keyboard, and persistent stats — all with the
Python standard library only. Run:  python termdle.py
"""

import json
import os
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Word list (answers double as the allowed-guess dictionary).
# ---------------------------------------------------------------------------
WORDS = """
about above abuse actor adapt admit adopt adult after again agent agree ahead
alarm album alert alike alive allow alone along aloud alpha amber angel anger
angle angry apart apple apply arena argue arise array aside asset audio audit
avoid award aware badly baker bases basic beach began begin being below bench
birth black blade blame blank blast blaze bleed blend bless blind block blood
bloom board boast bonus boost booth bound brain brake brand brave bread break
breed brick bride brief bring broad broke brown brush build built bunch burst
buyer cabin cable candy carry catch cause chain chair chalk charm chart chase
cheap check chess chest chief child chill china chord chose civic civil claim
clean clear clerk click cliff climb cling clock close cloth cloud coach coast
could count court cover crack craft crash crazy cream crisp cross crowd crown
crude crush curve cycle daily dairy dance dealt death debut delay depth doing
doubt dozen draft drain drama drank dream dress dried drift drill drink drive
drove drown eager eagle early earth eight elbow elder elect elite empty enemy
enjoy enter entry equal error event every exact exist extra fable faith false
fancy fault favor feast fence fever fiber field fifth fifty fight final first
flame flash fleet flesh float flock flood floor flour fluid flush focus force
forge forth forty forum found frame frank fraud fresh front frost fruit fully
funny gauge ghost giant given glass globe glory glove going grace grade grain
grand grant grape graph grass grave great greed green greet grief grill grind
gross group grown guard guess guest guide guilt habit happy harsh haste hatch
heart heavy hedge hello hertz hobby honey honor horse hotel house human humor
hurry ideal image index inner input issue ivory japan jazzy jelly jewel joint
judge juice juicy jumbo karma kayak kebab khaki kinda knife knock known label
labor large laser later laugh layer learn lease least leave legal lemon level
light limit linen lobby local logic loose lorry lover lower loyal lucky lunar
lunch lying magic major maker maple march match maybe mayor meant medal media
medic melon mercy merge merit metal meter midst might minor minus mixed model
money month moral motor mound mount mouse mouth movie music naval needy nerve
never newly night noble noise north notch novel nurse nylon ocean offer often
olive onion opera orbit order organ other ought ounce outer owner ozone paint
panel panic paper party pasta patch pause peace peach pearl penny phase phone
photo piano piece pilot pinch pitch pixel pizza place plain plane plant plate
plaza plead plot pluck plumb point polar porch pound power press price pride
prime print prior prize probe proof proud prove pulse punch pupil puppy purse
queen query quest quick quiet quilt quite quota quote radar radio raise rally
ranch range rapid ratio reach react ready realm rebel refer relax relay reply
rhyme rider ridge rifle right rigid risky rival river roast robin robot rocky
roman rough round route royal rugby ruler rural saint salad sauce scale scarf
scene scent scope score scout scrap screw sense serve seven shade shake shall
shape share shark sharp sheep sheet shelf shell shift shine shirt shock shoot
shore short shown shrub sight silly since siren sixth sixty skate skill skirt
skull slate sleep slice slide slope small smart smell smile smoke snack snake
sneak solar solid solve sorry sound south space spare spark speak spear speed
spell spend spent spice spike spine split spoke spoon sport spray squad stack
staff stage stair stake stand stare start state steam steel steep steer stern
stick stiff still stock stone stool store storm story stove strap straw stray
strip stuck study stuff style sugar suite sunny super surge swear sweat sweep
sweet swift swing sword table taken taste teach teeth tempo tenth thank theme
there these thick thief thing think third those three threw throw thumb tiger
tight timer title toast today token tooth topic torch total touch tough tower
toxic trace track trade trail train trait tread treat trend trial tribe trick
tried tripe trout truck truly trust truth twice twist ulcer ultra uncle under
union unite unity until upper upset urban usage usual vague valid value vault
venue verse video villa vinyl viper viral virus visit vital vivid vocal voice
voter wagon waist waste watch water weary weird whale wheat wheel where which
while white whole whose widen widow width witch woman world worry worse worst
worth would wound woven wrist write wrong wrote yacht yield young youth zebra
""".split()
WORDS = sorted(set(w for w in WORDS if len(w) == 5))
WORDSET = set(WORDS)

STATS_FILE = Path(__file__).with_name("termdle_stats.json")
ROWS = 6

# ANSI styles
RESET = "\033[0m"
GREEN = "\033[1;30;42m"
YELLOW = "\033[1;30;43m"
GRAY = "\033[1;97;100m"
DGRAY = "\033[90m"
BOLD = "\033[1m"
CYAN = "\033[96m"


def enable_ansi():
    # force UTF-8 so emoji / block chars don't crash on Windows' cp1252 console
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if os.name == "nt":
        os.system("")  # enables ANSI escape processing on Windows 10+


def score(guess: str, answer: str):
    """Return a list of 'g'/'y'/'b' for green/yellow/black per position."""
    result = ["b"] * 5
    counts = {}
    for a in answer:
        counts[a] = counts.get(a, 0) + 1
    # greens first
    for i, ch in enumerate(guess):
        if ch == answer[i]:
            result[i] = "g"
            counts[ch] -= 1
    # then yellows, respecting remaining letter counts
    for i, ch in enumerate(guess):
        if result[i] == "b" and counts.get(ch, 0) > 0:
            result[i] = "y"
            counts[ch] -= 1
    return result


def color_for(kind, ch):
    style = {"g": GREEN, "y": YELLOW, "b": GRAY}[kind]
    return f"{style} {ch.upper()} {RESET}"


def render(board, keyboard):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\n  {BOLD}{CYAN}T E R M D L E{RESET}   {DGRAY}guess the 5-letter word{RESET}\n")
    for r in range(ROWS):
        if r < len(board):
            guess, marks = board[r]
            print("   " + "".join(color_for(m, c) for c, m in zip(guess, marks)))
        else:
            print("   " + "".join(f"{DGRAY}[ ]{RESET}" for _ in range(5)))
    print()
    # keyboard
    for line in ("qwertyuiop", "asdfghjkl", "zxcvbnm"):
        pad = "  " if line == "asdfghjkl" else (" " if line == "zxcvbnm" else "")
        row = "   " + pad
        for ch in line:
            st = keyboard.get(ch)
            if st == "g":
                row += f"{GREEN}{ch.upper()}{RESET} "
            elif st == "y":
                row += f"{YELLOW}{ch.upper()}{RESET} "
            elif st == "b":
                row += f"{DGRAY}{ch.upper()}{RESET} "
            else:
                row += f"{ch.upper()} "
        print(row)
    print()


def update_keyboard(keyboard, guess, marks):
    """Upgrade each key's color, but never downgrade (green beats yellow beats black)."""
    rank = {None: 0, "b": 1, "y": 2, "g": 3}
    for ch, m in zip(guess, marks):
        if rank[m] > rank[keyboard.get(ch)]:
            keyboard[ch] = m


def load_stats():
    try:
        return json.loads(STATS_FILE.read_text())
    except Exception:
        return {"played": 0, "wins": 0, "streak": 0, "best_streak": 0, "dist": [0] * 6}


def save_stats(s):
    try:
        STATS_FILE.write_text(json.dumps(s, indent=2))
    except Exception:
        pass


def show_stats(s):
    played = s["played"]
    win_pct = round(100 * s["wins"] / played) if played else 0
    print(f"  {BOLD}Stats{RESET}   played {played}   win {win_pct}%   "
          f"streak {s['streak']}   best {s['best_streak']}")
    if any(s["dist"]):
        print(f"  {DGRAY}guess distribution:{RESET}")
        mx = max(s["dist"]) or 1
        for i, n in enumerate(s["dist"], 1):
            bar = "█" * round(20 * n / mx)
            print(f"   {i} {GREEN if n else DGRAY}{bar or '·'}{RESET} {n}")
    print()


def play():
    answer = os.environ.get("TERMDLE_WORD", "").lower().strip()
    if answer not in WORDSET:
        answer = random.choice(WORDS)

    board, keyboard = [], {}
    stats = load_stats()
    won = False

    render(board, keyboard)
    while len(board) < ROWS:
        try:
            guess = input(f"  guess {len(board)+1}/{ROWS} > ").lower().strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n  {DGRAY}bye! the word was {BOLD}{answer.upper()}{RESET}\n")
            return

        if len(guess) != 5 or not guess.isalpha():
            print(f"  {YELLOW} ! {RESET} type a 5-letter word")
            continue
        if guess not in WORDSET:
            print(f"  {YELLOW} ! {RESET} '{guess}' isn't in the word list")
            continue

        marks = score(guess, answer)
        board.append((guess, marks))
        update_keyboard(keyboard, guess, marks)
        render(board, keyboard)

        if guess == answer:
            won = True
            break

    # results + stats
    stats["played"] += 1
    if won:
        stats["wins"] += 1
        stats["streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["streak"])
        stats["dist"][len(board) - 1] += 1
        print(f"  {GREEN} SOLVED {RESET} in {len(board)} "
              f"{'guess' if len(board)==1 else 'guesses'}!  🎉\n")
    else:
        stats["streak"] = 0
        print(f"  {GRAY} OUT {RESET} the word was {BOLD}{answer.upper()}{RESET}\n")
    save_stats(stats)
    show_stats(stats)


if __name__ == "__main__":
    enable_ansi()
    play()
