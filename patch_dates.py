with open('backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace month and year combinations
content = content.replace("strftime('%m', g.data) = ? AND strftime('%Y', g.data) = ?", "g.data LIKE ?")
content = content.replace("strftime('%Y', g.data) = ?", "g.data LIKE ?")
content = content.replace("strftime('%m', data) = ? AND strftime('%Y', data) = ?", "data LIKE ?")
content = content.replace("strftime('%Y', data) = ?", "data LIKE ?")

# Also fix the params arrays that match these changes

# In listar_gastos, listar_receitas, listar_investimentos:
# original: params.extend([mes.zfill(2), ano])
# new: params.append(f"{ano}-{mes.zfill(2)}-%")
content = content.replace("params.extend([mes.zfill(2), ano])", "params.append(f\"{ano}-{mes.zfill(2)}-%\")")

# original: params.append(ano) (for year only string matching)
# wait, actually we want params.append(f"{ano}-%")
# I can just use regex for replacing these parts
import re
content = re.sub(r"elif ano:\s+query \+= \" AND \w*\.?data LIKE \?\"\s+params\.append\(ano\)",
                 "elif ano:\\n        query += \" AND data LIKE ?\"\\n        params.append(f\"{ano}-%\")",
                 content) # actually let's just do an exact match or fix the entire block

# Just replace the blocks directly:
old_gastos_if = """    if mes and ano:
        query += " AND strftime('%m', g.data) = ? AND strftime('%Y', g.data) = ?"
        params.extend([mes.zfill(2), ano])
    elif ano:
        query += " AND strftime('%Y', g.data) = ?"
        params.append(ano)"""
new_gastos_if = """    if mes and ano:
        query += " AND g.data LIKE ?"
        params.append(f"{ano}-{mes.zfill(2)}-%")
    elif ano:
        query += " AND g.data LIKE ?"
        params.append(f"{ano}-%")"""
content = content.replace(old_gastos_if, new_gastos_if)

old_generic_if = """    if mes and ano:
        query += " AND strftime('%m', data) = ? AND strftime('%Y', data) = ?"
        params.extend([mes.zfill(2), ano])
    elif ano:
        query += " AND strftime('%Y', data) = ?"
        params.append(ano)"""
new_generic_if = """    if mes and ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-{mes.zfill(2)}-%")
    elif ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-%")"""
content = content.replace(old_generic_if, new_generic_if)

# Fix resumo_mensal queries
content = content.replace('''total_gastos = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM gastos WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ? AND usuario_id = ?\''',
        (mes.zfill(2), ano, usuario_id)''',
'''total_gastos = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM gastos WHERE data LIKE ? AND usuario_id = ?\''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)''')

content = content.replace('''total_receitas = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM receitas WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ? AND usuario_id = ?\''',
        (mes.zfill(2), ano, usuario_id)''',
'''total_receitas = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM receitas WHERE data LIKE ? AND usuario_id = ?\''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)''')

content = content.replace('''por_categoria = conn.execute(
        \'''SELECT c.id, c.nome, c.cor, COALESCE(SUM(g.valor), 0) as total
           FROM categorias c
           LEFT JOIN gastos g ON g.categoria_id = c.id
             AND strftime('%m', g.data) = ? AND strftime('%Y', g.data) = ? AND g.usuario_id = ?
           WHERE c.usuario_id = ?
           GROUP BY c.id HAVING total > 0 ORDER BY total DESC\''',
        (mes.zfill(2), ano, usuario_id, usuario_id)''',
'''por_categoria = conn.execute(
        \'''SELECT c.id, c.nome, c.cor, COALESCE(SUM(g.valor), 0) as total
           FROM categorias c
           LEFT JOIN gastos g ON g.categoria_id = c.id
             AND g.data LIKE ? AND g.usuario_id = ?
           WHERE c.usuario_id = ?
           GROUP BY c.id HAVING total > 0 ORDER BY total DESC\''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id, usuario_id)''')

content = content.replace('''contagem = conn.execute(
        \'''SELECT COUNT(*) as quantidade FROM gastos WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ? AND usuario_id = ?\''',
        (mes.zfill(2), ano, usuario_id)''',
'''contagem = conn.execute(
        \'''SELECT COUNT(*) as quantidade FROM gastos WHERE data LIKE ? AND usuario_id = ?\''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)''')

content = content.replace('''total_investimentos = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM investimentos WHERE strftime('%m', data) = ? AND strftime('%Y', data) = ? AND usuario_id = ?\''',
        (mes.zfill(2), ano, usuario_id)''',
'''total_investimentos = conn.execute(
        \'''SELECT COALESCE(SUM(valor), 0) as total FROM investimentos WHERE data LIKE ? AND usuario_id = ?\''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)''')

with open('backend.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("PATCHED")
