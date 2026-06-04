import os
import re

count = 0
for root, dirs, files in os.walk('.'):
    # Exclude virtual environments and git
    if '.venv' in dirs:
        dirs.remove('.venv')
    if 'venv' in dirs:
        dirs.remove('venv')
    if '.git' in dirs:
        dirs.remove('.git')
        
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and replace all {{ ... }} blocks with newlines
            new_content = re.sub(
                r'\{\{(.*?)\}\}', 
                lambda m: "{{" + m.group(1).replace('\n', ' ').replace('\r', ' ') + "}}", 
                content, 
                flags=re.DOTALL
            )
            
            # Same for {% ... %}
            new_content = re.sub(
                r'\{%(.*?)%\}', 
                lambda m: "{%" + m.group(1).replace('\n', ' ').replace('\r', ' ') + "%}", 
                new_content, 
                flags=re.DOTALL
            )
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed {filepath}")
                count += 1

print(f"Total files fixed: {count}")
