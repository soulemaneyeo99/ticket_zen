#!/usr/bin/env python3
"""
Script pour commenter temporairement les appels ActivityLog dans users/views.py
pour permettre les tests avec SQLite
"""

import re

# Lire le fichier
with open('apps/users/views.py', 'r') as f:
    content = f.read()

# Pattern pour trouver les blocs ActivityLog.objects.create
pattern = r'(\s+)(#\s*)?ActivityLog\.objects\.create\('
replacement = r'\1# ActivityLog.objects.create('

# Remplacer
new_content = re.sub(pattern, replacement, content)

# Pattern pour les lignes suivantes du bloc (indentées)
lines = new_content.split('\n')
in_activity_log = False
result_lines = []

for i, line in enumerate(lines):
    if '# ActivityLog.objects.create(' in line:
        in_activity_log = True
        result_lines.append(line)
    elif in_activity_log:
        # Vérifier si c'est la fin du bloc (ligne moins indentée ou vide)
        if line.strip() and not line.startswith(' ' * 12):
            in_activity_log = False
            result_lines.append(line)
        else:
            # Commenter cette ligne si elle n'est pas déjà commentée
            if line.strip() and not line.strip().startswith('#'):
                result_lines.append(line[:line.index(line.lstrip())] + '# ' + line.lstrip())
            else:
                result_lines.append(line)
    else:
        result_lines.append(line)

# Écrire le résultat
with open('apps/users/views.py', 'w') as f:
    f.write('\n'.join(result_lines))

print("ActivityLog calls commented out successfully")
