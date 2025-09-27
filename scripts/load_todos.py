#!/usr/bin/env python3
"""Script to load persistent todos from JSON file."""

import json
from pathlib import Path

def load_todos():
    """Load todos from .claude-todos.json file."""
    project_root = Path(__file__).parent.parent
    todos_file = project_root / ".claude-todos.json"

    if not todos_file.exists():
        print("No todos file found. Create .claude-todos.json first.")
        return []

    with open(todos_file, 'r') as f:
        todos = json.load(f)

    return todos

def format_todos_for_claude(todos):
    """Format todos for Claude TodoWrite tool."""
    claude_todos = []
    for todo in todos:
        claude_todo = {
            "content": todo["content"],
            "status": todo["status"],
            "activeForm": todo["activeForm"]
        }
        claude_todos.append(claude_todo)

    return claude_todos

def save_todos(todos):
    """Save todos back to JSON file."""
    project_root = Path(__file__).parent.parent
    todos_file = project_root / ".claude-todos.json"

    with open(todos_file, 'w') as f:
        json.dump(todos, f, indent=2)

    print(f"Saved {len(todos)} todos to {todos_file}")

if __name__ == "__main__":
    todos = load_todos()
    print(f"Loaded {len(todos)} todos:")
    for i, todo in enumerate(todos, 1):
        status_icon = "✅" if todo["status"] == "completed" else "🔄" if todo["status"] == "in_progress" else "☐"
        print(f"{i}. {status_icon} {todo['content']}")