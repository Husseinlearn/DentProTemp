import os, re

apps = ['patients', 'appointment', 'procedures', 'medicalrecord', 'accounts', 'billing', 'core', 'templates']
regex = re.compile(r'\{%[^%]*\n|\{\{[^}]*\n|\n[^%]*%\}|\n[^}]*\}\}')

for app in apps:
    app_dir = os.path.join('.', app)
    if not os.path.exists(app_dir): continue
    for root, dirs, files in os.walk(app_dir):
        for f in files:
            if f.endswith('.html'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    text = "".join(lines)
                
                # We can't easily find cross-line matches with line iteration.
                # Just output files that contain newlines between bracket starts/ends.
                matches = re.findall(r'\{\{[^}]*\n[^}]*\}\}', text)
                matches2 = re.findall(r'\{%[^%]*\n[^%]*%\}', text)
                
                if matches:
                    print(f"File {path} has bad variable tags: {len(matches)}")
                if matches2:
                    print(f"File {path} has bad logic tags: {len(matches2)}")
