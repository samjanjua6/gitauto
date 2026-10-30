import datetime
import json
import random
import urllib.request
import os

# Fallback quotes in case external API is unreachable
FALLBACK_QUOTES = [
    {"quote": "Consistency is the DNA of mastery.", "author": "Robin Sharma"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson"},
    {"quote": "Code is like humor. When you have to explain it, it’s bad.", "author": "Cory House"},
    {"quote": "Make it work, make it right, make it fast.", "author": "Kent Beck"},
    {"quote": "Simplicity is prerequisite for reliability.", "author": "Edsger W. Dijkstra"},
    {"quote": "Small daily improvements over time lead to stunning results.", "author": "Robin Sharma"},
    {"quote": "Programming isn't about what you know; it's about what you can figure out.", "author": "Chris Pine"},
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds"},
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde"},
    {"quote": "Knowledge is power.", "author": "Francis Bacon"},
    {"quote": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"quote": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson"},
    {"quote": "Perfection is achieved not when there is nothing more to add, but rather when there is nothing more to take away.", "author": "Antoine de Saint-Exupery"}
]

def fetch_quote():
    """Fetches a random inspirational or programming quote."""
    # Attempt to fetch quote from public API with short timeout
    apis = [
        "https://api.quotable.io/random?tags=technology|inspirational|success",
        "https://zenquotes.io/api/random"
    ]
    for api_url in apis:
        try:
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if isinstance(data, list) and len(data) > 0 and 'q' in data[0]:
                        return {"quote": data[0]['q'], "author": data[0]['a']}
                    elif 'content' in data:
                        return {"quote": data['content'], "author": data.get('author', 'Unknown')}
        except Exception:
            continue
    return random.choice(FALLBACK_QUOTES)

def update_data():
    now = datetime.datetime.now(datetime.timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    quote_data = fetch_quote()

    # 1. Update history.json
    history_file = "history.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    entry = {
        "timestamp": timestamp_str,
        "date": date_str,
        "quote": quote_data["quote"],
        "author": quote_data["author"]
    }
    history.append(entry)

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    total_commits = len(history)

    # 2. Update LOG.md
    log_file = "LOG.md"
    log_entry = f"- **`{timestamp_str}`**: \"{quote_data['quote']}\" — *{quote_data['author']}*\n"
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("# 📜 Commit Activity Log\n\n")
            f.write("Log of automated daily commits maintaining GitHub activity streak.\n\n")
            f.write(log_entry)
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    # 3. Update README.md
    readme_file = "README.md"
    readme_template = f"""# 🚀 Automated GitHub Activity & Streak Keeper

![GitHub Streak](https://img.shields.io/badge/Daily_Streak-Active-brightgreen?style=for-the-badge&logo=github)
![Total Commits](https://img.shields.io/badge/Total_Logged_Commits-{total_commits}-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Workflow-Automated-orange?style=for-the-badge)

This repository automatically logs daily activity and inspiration to keep GitHub commit streaks healthy and active 365 days a year without needing a local computer running.

---

### 💡 Daily Thought
> *"{quote_data['quote']}"*  
> — **{quote_data['author']}**

---

### 📊 Streak Overview
- **Last Sync:** `{timestamp_str}`
- **Total Recorded Entries:** `{total_commits}`
- **Full History:** See [LOG.md](LOG.md)

---

### ⚙️ How It Works
1. **GitHub Actions** runs automatically on a scheduled cron trigger (`0 10 * * *` UTC) every day.
2. Runs [`update.py`](update.py) to record a new entry, timestamp, and motivational quote.
3. Automatically commits and pushes to the `main` branch with author attribution matching your GitHub account.
4. Can be manually triggered at any time from the **Actions** tab on GitHub via `workflow_dispatch`.
"""
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_template)

    print(f"Successfully recorded commit entry #{total_commits} at {timestamp_str}")

if __name__ == "__main__":
    update_data()
