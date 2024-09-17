import re
from datetime import datetime

def clean_commit_message(message):
    lines = message.split('\n')
    first_line = re.sub(r'^(feat|fix|docs|style|refactor|test|chore)(\(.*?\))?:\s*', '', lines[0])
    first_line = first_line[0].upper() + first_line[1:] if first_line else first_line

    if len(lines) > 1:
        return first_line + '\n' + '\n'.join(lines[1:]).strip()
    return first_line

def extract_description_text(description):
    if not description:
        return ""
    cleaned = re.sub(r'<[^>]+>', '', description)
    lines = cleaned.split('\n')
    start_index = next((i for i, line in enumerate(lines) if "Description:" in line), 0) + 1
    relevant_lines = [line.strip() for line in lines[start_index:start_index+5] if line.strip() and not line.strip().endswith(':')]
    return ' '.join(relevant_lines)

def format_date(date=None, format="%d %B %Y"):
    if date is None:
        date = datetime.now()
    return date.strftime(format)