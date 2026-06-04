import os, re
pattern = re.compile(r'\{\{\s*\n')
for root, dirs, files in os.walk('.'):
    if '.venv' in dirs: dirs.remove('.venv')
    if 'venv' in dirs: dirs.remove('venv')
    if '.git' in dirs: dirs.remove('.git')
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        print(f"{filepath}:{i+1} -> {line.strip()}")
