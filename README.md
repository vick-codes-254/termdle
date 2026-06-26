# Termdle

[Wordle](https://en.wikipedia.org/wiki/Wordle) for your terminal — colored feedback, an on-screen keyboard, and persistent stats. Written in **pure Python 3** (standard library only).

![lang](https://img.shields.io/badge/Python-3.8%2B-3776ab) ![deps](https://img.shields.io/badge/dependencies-none-ffd343) ![license](https://img.shields.io/badge/license-MIT-yellow)

## Features
- **Real Wordle scoring** — correct two-pass green/yellow logic that handles repeated letters properly
- **ANSI color board** + a live **on-screen keyboard** that tracks each letter's best-known state
- **Persistent stats** — games played, win %, current & best streak, and a guess-distribution histogram (saved to `termdle_stats.json`)
- **Cross-platform** — forces UTF-8 output and enables ANSI on Windows, so emoji and block characters render without crashing
- Built-in ~700-word dictionary; **no internet, no dependencies**

## Play
```bash
python termdle.py
```
Type a 5-letter word and press Enter. You get 6 guesses.

| Color | Meaning |
|-------|---------|
| Green | Right letter, right spot |
| Yellow | Right letter, wrong spot |
| Gray | Not in the word |

## Deterministic mode
Set the answer (handy for testing or sharing a puzzle):
```bash
TERMDLE_WORD=pizza python termdle.py      # macOS / Linux
set TERMDLE_WORD=pizza && python termdle.py  # Windows cmd
```

## How the scoring works
First pass marks exact matches green and decrements that letter's remaining count. A second pass marks a letter yellow only if an unmatched copy of it still remains in the answer — this is what makes guesses like `LLAMA` against `ALLAY` score correctly.

## License
MIT.
