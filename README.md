# cronscope

Lightweight utility to visualize and validate cron expressions with next-run previews in the terminal.

---

## Installation

```bash
pip install cronscope
```

Or install from source:

```bash
git clone https://github.com/yourusername/cronscope.git && cd cronscope && pip install .
```

---

## Usage

```bash
# Preview the next 5 scheduled runs for a cron expression
cronscope "*/15 9-17 * * 1-5"

# Validate a cron expression and show 10 upcoming runs
cronscope "0 0 1 * *" --runs 10

# Check if an expression is valid without output
cronscope "*/5 * * * *" --validate-only
```

**Example output:**

```
Expression : */15 9-17 * * 1-5
Description: Every 15 minutes, between 09:00 and 17:59, Monday through Friday

Next 5 runs:
  1 → 2024-11-18 09:00:00
  2 → 2024-11-18 09:15:00
  3 → 2024-11-18 09:30:00
  4 → 2024-11-18 09:45:00
  5 → 2024-11-18 10:00:00
```

---

## Options

| Flag             | Description                              |
|------------------|------------------------------------------|
| `--runs N`       | Number of upcoming runs to display (default: 5) |
| `--validate-only`| Only check if the expression is valid    |
| `--format`       | Output format: `text` or `json`          |

---

## Requirements

- Python 3.8+
- [`croniter`](https://github.com/kiorky/croniter)

---

## License

MIT © 2024 [yourusername](https://github.com/yourusername)