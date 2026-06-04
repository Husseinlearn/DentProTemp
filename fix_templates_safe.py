import os
import re

apps = ['patients', 'appointment', 'procedures', 'medicalrecord', 'accounts', 'billing', 'core', 'templates']
log = open('fix_log.txt', 'w')
count = 0

for app in apps:
    app_dir = os.path.join('.', app)
    if not os.path.isdir(app_dir):
        continue
        
    for root, dirs, files in os.walk(app_dir):
        for f in files:
            if f.endswith('.html'):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    # Replace logic inside tags
                    def replacer(m):
                        inner = m.group(1).replace('\n', ' ').replace('\r', ' ')
                        inner = re.sub(r'\s+', ' ', inner)
                        return '{{ ' + inner.strip() + ' }}'
                    
                    new_content = re.sub(r'\{\{([^}]+)\}\}', replacer, content)
                    
                    # Also do {% ... %} tags!
                    def tag_replacer(m):
                        inner = m.group(1).replace('\n', ' ').replace('\r', ' ')
                        inner = re.sub(r'\s+', ' ', inner)
                        return '{% ' + inner.strip() + ' %}'
                        
                    new_content = re.sub(r'\{%([^%]+)%\}', tag_replacer, new_content)
                    
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as file:
                            file.write(new_content)
                        log.write(f"Fixed {filepath}\n")
                        count += 1
                except Exception as e:
                    log.write(f"Error {filepath}: {str(e)}\n")

log.write(f"Total: {count}\n")
log.close()
