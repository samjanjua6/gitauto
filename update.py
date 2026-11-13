import datetime
import json
import random
import urllib.request
import os
import sys

SCHEDULED_HOURS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

FALLBACK_QUOTES = [
    {"quote": "Consistency is the DNA of mastery.", "author": "Robin Sharma", "topic": "mastery"},
    {"quote": "First, solve the problem. Then, write the code.", "author": "John Johnson", "topic": "problem-solving"},
    {"quote": "Code is like humor. When you have to explain it, it’s bad.", "author": "Cory House", "topic": "clean-code"},
    {"quote": "Make it work, make it right, make it fast.", "author": "Kent Beck", "topic": "architecture"},
    {"quote": "Simplicity is prerequisite for reliability.", "author": "Edsger W. Dijkstra", "topic": "simplicity"},
    {"quote": "Small daily improvements over time lead to stunning results.", "author": "Robin Sharma", "topic": "growth"},
    {"quote": "Programming isn't about what you know; it's about what you can figure out.", "author": "Chris Pine", "topic": "learning"},
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "topic": "passion"},
    {"quote": "Talk is cheap. Show me the code.", "author": "Linus Torvalds", "topic": "action"},
    {"quote": "Any fool can write code that a computer can understand. Good programmers write code that humans can understand.", "author": "Martin Fowler", "topic": "clean-code"},
    {"quote": "Experience is the name everyone gives to their mistakes.", "author": "Oscar Wilde", "topic": "experience"},
    {"quote": "Knowledge is power.", "author": "Francis Bacon", "topic": "knowledge"},
    {"quote": "Stay hungry, stay foolish.", "author": "Steve Jobs", "topic": "mindset"},
    {"quote": "Before software can be reusable it first has to be usable.", "author": "Ralph Johnson", "topic": "design"},
    {"quote": "Perfection is achieved not when there is nothing more to add, but rather when there is nothing more to take away.", "author": "Antoine de Saint-Exupery", "topic": "minimalism"},
    {"quote": "Optimism is an occupational hazard of programming: feedback is the treatment.", "author": "Kent Beck", "topic": "programming"},
    {"quote": "Fix the cause, not the symptom.", "author": "Steve Maguire", "topic": "debugging"},
    {"quote": "Simplicity is the soul of efficiency.", "author": "Austin Freeman", "topic": "efficiency"},
    {"quote": "Make each program do one thing well.", "author": "Ken Thompson", "topic": "unix-philosophy"},
    {"quote": "Good judgment comes from experience, and experience comes from bad judgment.", "author": "Fred Brooks", "topic": "wisdom"}
]

def fetch_quote():
    """Fetches a random inspirational or programming quote."""
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
            with urllib.request.urlopen(req, timeout=4) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    if isinstance(data, list) and len(data) > 0 and 'q' in data[0]:
                        return {"quote": data[0]['q'], "author": data[0]['a'], "topic": "inspiration"}
                    elif 'content' in data:
                        return {"quote": data['content'], "author": data.get('author', 'Unknown'), "topic": "wisdom"}
        except Exception:
            continue
    return random.choice(FALLBACK_QUOTES)

def generate_commit_message(quote_data, commit_num):
    """Generates natural, rotating conventional commit messages."""
    author_short = quote_data.get('author', 'Dev').split()[-1]
    topic = quote_data.get('topic', 'insights')

    templates = [
        f"docs(journal): quote by {author_short} [skip ci]",
        f"chore(data): record daily entry #{commit_num} [skip ci]",
        f"feat(notes): sync daily {topic} log [skip ci]",
        f"docs(daily): log insight by {author_short} [skip ci]",
        f"chore(activity): record daily progress #{commit_num} [skip ci]",
        f"feat(journal): daily thought on {topic} [skip ci]",
        f"docs(quote): sync wisdom from {author_short} [skip ci]",
        f"chore(sync): update streak log entry #{commit_num} [skip ci]"
    ]
    return random.choice(templates)

def should_commit(force=False):
    """Determines if a commit should happen in this run to reach 4-10 daily commits."""
    if force:
        return True, 1, 7

    now = datetime.datetime.now(datetime.timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    current_hour = now.hour

    state_file = "state.json"
    state = {
        "current_date": today_str,
        "target_commits": random.randint(4, 10),
        "commits_today": 0
    }

    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if saved.get("current_date") == today_str:
                    state = saved
                else:
                    # New day, fresh randomized target between 4 and 10
                    state["target_commits"] = random.randint(4, 10)
                    state["commits_today"] = 0
        except Exception:
            pass

    target = state["target_commits"]
    done = state["commits_today"]

    # Target already reached for today
    if done >= target:
        print(f"Daily target reached ({done}/{target} commits today). Skipping.")
        return False, done, target

    # Count scheduled slots remaining today (including current slot)
    slots_remaining = len([h for h in SCHEDULED_HOURS if h >= current_hour])
    if slots_remaining <= 0:
        slots_remaining = 1

    needed = target - done

    # If remaining slots equal or are less than needed commits, commit with 100% guarantee
    if needed >= slots_remaining:
        should_run = True
    else:
        # Otherwise, calculate dynamic probability
        prob = (needed / slots_remaining) * 1.15
        should_run = random.random() < prob

    if should_run:
        state["commits_today"] = done + 1
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True, state["commits_today"], target
    else:
        print(f"Skipping slot to preserve organic spacing ({done}/{target} commits done, {slots_remaining} slots left).")
        return False, done, target

def run():
    force = "--force" in sys.argv
    do_commit, commit_today_count, target_commits = should_commit(force=force)

    if not do_commit:
        # Output empty commit message so bash script knows to exit cleanly
        with open("commit_msg.txt", "w", encoding="utf-8") as f:
            f.write("")
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_str = now.strftime("%Y-%m-%d")
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
        "commit_today": commit_today_count,
        "target_today": target_commits,
        "quote": quote_data["quote"],
        "author": quote_data["author"]
    }
    history.append(entry)

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    total_commits = len(history)

    # 2. Update LOG.md
    log_file = "LOG.md"
    log_entry = f"- **`{timestamp_str}`** (Commit {commit_today_count}/{target_commits} today): \"{quote_data['quote']}\" — *{quote_data['author']}*\n"
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("# 📜 Commit Activity Log\n\n")
            f.write("Log of automated daily commits maintaining GitHub activity streak.\n\n")
            f.write(log_entry)
    else:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    # 3. Update README.md
    commit_msg = generate_commit_message(quote_data, commit_today_count)
    readme_file = "README.md"
    readme_template = f"""# 🚀 Automated GitHub Activity & Streak Keeper

![Daily Streak](https://img.shields.io/badge/Daily_Streak-Active-brightgreen?style=for-the-badge&logo=github)
![Today Progress](https://img.shields.io/badge/Today's_Commits-{commit_today_count}%2F{target_commits}-blueviolet?style=for-the-badge)
![Total Logged](https://img.shields.io/badge/Total_Commits-{total_commits}-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Workflow-Automated-orange?style=for-the-badge)

This repository automatically logs daily activity and inspiration to keep GitHub commit streaks healthy and active 365 days a year without needing a local computer running.

---

### 💡 Latest Thought
> *"{quote_data['quote']}"*  
> — **{quote_data['author']}**

---

### 📊 Streak Overview
- **Last Sync:** `{timestamp_str}`
- **Today's Progress:** `{commit_today_count} of {target_commits} commits`
- **Total Recorded Entries:** `{total_commits}`
- **Full History:** See [LOG.md](LOG.md)

---

### ⚙️ How It Works
1. Runs automatically across natural daily time slots on a scheduled cron trigger.
2. Dynamically randomizes **4 to 10 commits per day**, creating realistic, varied shades of green on your contribution graph.
3. Automatically rotates conventional commit messages and authors.
4. Includes automatic 60-day workflow keepalive to guarantee the schedule never pauses.
"""
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_template)

    # Write commit message for workflow to use
    with open("commit_msg.txt", "w", encoding="utf-8") as f:
        f.write(commit_msg)

    print(f"Ready: Commit #{commit_today_count}/{target_commits} today ({commit_msg})")

if __name__ == "__main__":
    run()
