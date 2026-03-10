"""
Organizador de Custos - Backend Flask
API REST para gerenciamento de gastos mensais com SQLite.
Integração com ExchangeRate-API para conversão de moedas.
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from psycopg2.errors import UniqueViolation, DuplicateColumn
from dotenv import load_dotenv

load_dotenv()
import os
import requests as http_requests
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from functools import wraps

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')

EXCHANGE_API_URL = "https://open.er-api.com/v6/latest"


# ─────────────────────────────────────────────
# Banco de Dados
# ─────────────────────────────────────────────


class DBWrapper:
    def __init__(self, conn):
        self.conn = conn
    def execute(self, sql, params=()):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        sql = sql.replace('?', '%s')
        
        # intercept lastrowid for INSERT
        try:
            if sql.strip().upper().startswith("INSERT"):
                if "RETURNING id" not in sql:
                    sql += " RETURNING id"
                cur.execute(sql, params)
                try:
                    self.lastrowid = cur.fetchone()['id']
                except:
                    self.lastrowid = None
            else:
                cur.execute(sql, params)
                self.lastrowid = None
        except Exception as e:
            self.conn.rollback()
            raise e
        
        class CursorProxy:
            def __init__(self, c, l):
                self.cur = c
                self.lastrowid = l
            def fetchone(self): return self.cur.fetchone()
            def fetchall(self): return self.cur.fetchall()
            @property
            def rowcount(self): return self.cur.rowcount
            
        return CursorProxy(cur, self.lastrowid)
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return DBWrapper(conn)


def init_db():
    conn = get_db()
    cursor = conn

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            token TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            cor TEXT DEFAULT '#6c63ff',
            usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            UNIQUE(nome, usuario_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            categoria_id INTEGER,
            data TEXT NOT NULL,
            anotacao TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receitas (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            anotacao TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investimentos (
            id SERIAL PRIMARY KEY,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'Outro',
            data TEXT NOT NULL,
            anotacao TEXT DEFAULT '',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            usuario_id INTEGER,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixa_config (
            id SERIAL PRIMARY KEY,
            saldo_inicial REAL NOT NULL DEFAULT 0,
            usuario_id INTEGER UNIQUE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gastos_usuario_data ON gastos(usuario_id, data)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_receitas_usuario_data ON receitas(usuario_id, data)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_investimentos_user_data ON investimentos(usuario_id, data)')

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# Auth Middleware
# ─────────────────────────────────────────────

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'erro': 'Não autorizado'}), 401
        
        token = auth_header.split(' ')[1]
        
        conn = get_db()
        user = conn.execute('SELECT id FROM usuarios WHERE token = ?', (token,)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401
            
        return f(user['id'], *args, **kwargs)
    return decorated

# ─────────────────────────────────────────────
# Rotas - Páginas
# ─────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

# ─────────────────────────────────────────────
# API - Autenticação
# ─────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    dados = request.get_json()
    username = dados.get('username', '').strip()
    password = dados.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'erro': 'Usuário e senha são obrigatórios'}), 400
        
    if len(password) < 6:
        return jsonify({'erro': 'A senha deve ter pelo menos 6 caracteres'}), 400
        
    conn = get_db()
    try:
        pw_hash = generate_password_hash(password)
        cursor = conn.execute('INSERT INTO usuarios (username, password_hash) VALUES (?, ?)', (username, pw_hash))
        user_id = cursor.lastrowid
        
        # Categorias padrão
        categorias_padrao = [
            ('Alimentação', '#38bdf8'),
            ('Transporte', '#22d3ee'),
            ('Moradia', '#2dd4bf'),
            ('Saúde', '#818cf8'),
            ('Educação', '#a78bfa'),
            ('Lazer', '#67e8f9'),
            ('Outros', '#94a3b8'),
        ]
        for nome, cor in categorias_padrao:
            conn.execute('INSERT INTO categorias (nome, cor, usuario_id) VALUES (?, ?, ?)', (nome, cor, user_id))
            
        # Caixa config
        conn.execute('INSERT INTO caixa_config (saldo_inicial, usuario_id) VALUES (0, ?)', (user_id,))
        
        conn.commit()
        return jsonify({'mensagem': 'Conta criada com sucesso!'}), 201
    except UniqueViolation:
        return jsonify({'erro': 'Nome de usuário já existe'}), 409
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json()
    username = dados.get('username', '').strip()
    password = dados.get('password', '').strip()
    
    conn = get_db()
    user = conn.execute('SELECT * FROM usuarios WHERE username = ?', (username,)).fetchone()
    
    if user and check_password_hash(user['password_hash'], password):
        token = secrets.token_hex(32)
        conn.execute('UPDATE usuarios SET token = ? WHERE id = ?', (token, user['id']))
        conn.commit()
        conn.close()
        return jsonify({'token': token, 'username': user['username']}), 200
    
    conn.close()
    return jsonify({'erro': 'Usuário ou senha inválidos'}), 401

@app.route('/api/logout', methods=['POST'])
@require_auth
def logout(usuario_id):
    conn = get_db()
    conn.execute('UPDATE usuarios SET token = NULL WHERE id = ?', (usuario_id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Logout realizado'}), 200


# ─────────────────────────────────────────────
# API - Categorias
# ─────────────────────────────────────────────

@app.route('/api/categorias', methods=['GET'])
@require_auth
def listar_categorias(usuario_id):
    conn = get_db()
    categorias = conn.execute('SELECT * FROM categorias WHERE usuario_id = ? ORDER BY nome', (usuario_id,)).fetchall()
    conn.close()
    return jsonify([dict(c) for c in categorias])

@app.route('/api/categorias', methods=['POST'])
@require_auth
def criar_categoria(usuario_id):
    dados = request.get_json()
    nome = dados.get('nome', '').strip()
    cor = dados.get('cor', '#6c63ff')

    if not nome:
        return jsonify({'erro': 'Nome da categoria é obrigatório'}), 400

    conn = get_db()
    try:
        conn.execute('INSERT INTO categorias (nome, cor, usuario_id) VALUES (?, ?, ?)', (nome, cor, usuario_id))
        conn.commit()
        categoria = conn.execute(
            'SELECT * FROM categorias WHERE nome = ? AND usuario_id = ?', (nome, usuario_id)
        ).fetchone()
        conn.close()
        return jsonify(dict(categoria)), 201
    except UniqueViolation:
        conn.close()
        return jsonify({'erro': 'Categoria já existe'}), 409

@app.route('/api/categorias/<int:id>', methods=['DELETE'])
@require_auth
def deletar_categoria(usuario_id, id):
    conn = get_db()
    conn.execute('DELETE FROM categorias WHERE id = ? AND usuario_id = ?', (id, usuario_id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Categoria removida'}), 200

# ─────────────────────────────────────────────
# API - Gastos
# ─────────────────────────────────────────────

@app.route('/api/gastos', methods=['GET'])
@require_auth
def listar_gastos(usuario_id):
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    conn = get_db()
    query = '''
        SELECT g.*, c.nome as categoria_nome, c.cor as categoria_cor
        FROM gastos g
        LEFT JOIN categorias c ON g.categoria_id = c.id
        WHERE g.usuario_id = ?
    '''
    params = [usuario_id]

    if mes and ano:
        query += " AND g.data LIKE ?"
        params.append(f"{ano}-{mes.zfill(2)}-%")
    elif ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-%")

    query += ' ORDER BY g.data DESC, g.id DESC'

    gastos = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(g) for g in gastos])

@app.route('/api/gastos', methods=['POST'])
@require_auth
def criar_gasto(usuario_id):
    dados = request.get_json()

    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    categoria_id = dados.get('categoria_id')
    data = dados.get('data', datetime.now().strftime('%Y-%m-%d'))
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) < 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    # Verifica se a categoria pertence ao usuário (se informada)
    if categoria_id:
        cat = conn.execute('SELECT id FROM categorias WHERE id = ? AND usuario_id = ?', (categoria_id, usuario_id)).fetchone()
        if not cat:
            categoria_id = None
            
    cursor = conn.execute(
        '''INSERT INTO gastos (descricao, valor, categoria_id, data, anotacao, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (descricao, float(valor), categoria_id, data, anotacao, usuario_id)
    )
    gasto_id = cursor.lastrowid
    conn.commit()

    gasto = conn.execute(
        '''SELECT g.*, c.nome as categoria_nome, c.cor as categoria_cor
           FROM gastos g
           LEFT JOIN categorias c ON g.categoria_id = c.id
           WHERE g.id = ?''',
        (gasto_id,)
    ).fetchone()
    conn.close()
    return jsonify(dict(gasto)), 201

@app.route('/api/gastos/<int:id>', methods=['PUT'])
@require_auth
def editar_gasto(usuario_id, id):
    dados = request.get_json()

    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    categoria_id = dados.get('categoria_id')
    data = dados.get('data')
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) < 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    if categoria_id:
        cat = conn.execute('SELECT id FROM categorias WHERE id = ? AND usuario_id = ?', (categoria_id, usuario_id)).fetchone()
        if not cat:
            categoria_id = None
            
    conn.execute(
        '''UPDATE gastos
           SET descricao = ?, valor = ?, categoria_id = ?, data = ?, anotacao = ?
           WHERE id = ? AND usuario_id = ?''',
        (descricao, float(valor), categoria_id, data, anotacao, id, usuario_id)
    )
    conn.commit()

    gasto = conn.execute(
        '''SELECT g.*, c.nome as categoria_nome, c.cor as categoria_cor
           FROM gastos g
           LEFT JOIN categorias c ON g.categoria_id = c.id
           WHERE g.id = ?''',
        (id,)
    ).fetchone()
    conn.close()

    if gasto is None:
        return jsonify({'erro': 'Gasto não encontrado'}), 404

    return jsonify(dict(gasto))

@app.route('/api/gastos/<int:id>', methods=['DELETE'])
@require_auth
def deletar_gasto(usuario_id, id):
    conn = get_db()
    conn.execute('DELETE FROM gastos WHERE id = ? AND usuario_id = ?', (id, usuario_id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Gasto removido'}), 200

# ─────────────────────────────────────────────
# API - Receitas (Entradas de dinheiro)
# ─────────────────────────────────────────────

@app.route('/api/receitas', methods=['GET'])
@require_auth
def listar_receitas(usuario_id):
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    conn = get_db()
    query = 'SELECT * FROM receitas WHERE usuario_id = ?'
    params = [usuario_id]

    if mes and ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-{mes.zfill(2)}-%")
    elif ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-%")

    query += ' ORDER BY data DESC, id DESC'
    receitas = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(r) for r in receitas])

@app.route('/api/receitas', methods=['POST'])
@require_auth
def criar_receita(usuario_id):
    dados = request.get_json()
    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    data = dados.get('data', datetime.now().strftime('%Y-%m-%d'))
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) <= 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO receitas (descricao, valor, data, anotacao, usuario_id)
           VALUES (?, ?, ?, ?, ?)''',
        (descricao, float(valor), data, anotacao, usuario_id)
    )
    receita_id = cursor.lastrowid
    conn.commit()
    receita = conn.execute('SELECT * FROM receitas WHERE id = ?', (receita_id,)).fetchone()
    conn.close()
    return jsonify(dict(receita)), 201

@app.route('/api/receitas/<int:id>', methods=['PUT'])
@require_auth
def editar_receita(usuario_id, id):
    dados = request.get_json()
    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    data = dados.get('data')
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) <= 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    conn.execute(
        '''UPDATE receitas SET descricao = ?, valor = ?, data = ?, anotacao = ? WHERE id = ? AND usuario_id = ?''',
        (descricao, float(valor), data, anotacao, id, usuario_id)
    )
    conn.commit()
    receita = conn.execute('SELECT * FROM receitas WHERE id = ?', (id,)).fetchone()
    conn.close()

    if receita is None:
        return jsonify({'erro': 'Receita não encontrada'}), 404
    return jsonify(dict(receita))

@app.route('/api/receitas/<int:id>', methods=['DELETE'])
@require_auth
def deletar_receita(usuario_id, id):
    conn = get_db()
    conn.execute('DELETE FROM receitas WHERE id = ? AND usuario_id = ?', (id, usuario_id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Receita removida'}), 200

# ─────────────────────────────────────────────
# API - Investimentos
# ─────────────────────────────────────────────

@app.route('/api/investimentos', methods=['GET'])
@require_auth
def listar_investimentos(usuario_id):
    mes = request.args.get('mes')
    ano = request.args.get('ano')

    conn = get_db()
    query = 'SELECT * FROM investimentos WHERE usuario_id = ?'
    params = [usuario_id]

    if mes and ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-{mes.zfill(2)}-%")
    elif ano:
        query += " AND data LIKE ?"
        params.append(f"{ano}-%")

    query += ' ORDER BY data DESC, id DESC'
    investimentos = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(i) for i in investimentos])

@app.route('/api/investimentos', methods=['POST'])
@require_auth
def criar_investimento(usuario_id):
    dados = request.get_json()
    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    tipo = dados.get('tipo', 'Outro')
    data = dados.get('data', datetime.now().strftime('%Y-%m-%d'))
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) <= 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO investimentos (descricao, valor, tipo, data, anotacao, usuario_id)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (descricao, float(valor), tipo, data, anotacao, usuario_id)
    )
    inv_id = cursor.lastrowid
    conn.commit()
    inv = conn.execute('SELECT * FROM investimentos WHERE id = ?', (inv_id,)).fetchone()
    conn.close()
    return jsonify(dict(inv)), 201

@app.route('/api/investimentos/<int:id>', methods=['PUT'])
@require_auth
def editar_investimento(usuario_id, id):
    dados = request.get_json()
    descricao = dados.get('descricao', '').strip()
    valor = dados.get('valor')
    tipo = dados.get('tipo', 'Outro')
    data = dados.get('data')
    anotacao = dados.get('anotacao', '').strip()

    if not descricao:
        return jsonify({'erro': 'Descrição é obrigatória'}), 400
    if valor is None or float(valor) <= 0:
        return jsonify({'erro': 'Valor inválido'}), 400

    conn = get_db()
    conn.execute(
        '''UPDATE investimentos SET descricao = ?, valor = ?, tipo = ?, data = ?, anotacao = ? WHERE id = ? AND usuario_id = ?''',
        (descricao, float(valor), tipo, data, anotacao, id, usuario_id)
    )
    conn.commit()
    inv = conn.execute('SELECT * FROM investimentos WHERE id = ?', (id,)).fetchone()
    conn.close()

    if inv is None:
        return jsonify({'erro': 'Investimento não encontrado'}), 404
    return jsonify(dict(inv))

@app.route('/api/investimentos/<int:id>', methods=['DELETE'])
@require_auth
def deletar_investimento(usuario_id, id):
    conn = get_db()
    conn.execute('DELETE FROM investimentos WHERE id = ? AND usuario_id = ?', (id, usuario_id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Investimento removido'}), 200

# ─────────────────────────────────────────────
# API - Caixa (Cash Box)
# ─────────────────────────────────────────────

@app.route('/api/caixa', methods=['GET'])
@require_auth
def obter_caixa(usuario_id):
    conn = get_db()
    config = conn.execute('SELECT saldo_inicial FROM caixa_config WHERE usuario_id = ?', (usuario_id,)).fetchone()
    conn.close()
    return jsonify({'saldo_inicial': config['saldo_inicial'] if config else 0})

@app.route('/api/caixa', methods=['PUT'])
@require_auth
def atualizar_caixa(usuario_id):
    dados = request.get_json()
    saldo_inicial = dados.get('saldo_inicial', 0)

    conn = get_db()
    
    # Try to update, if diff 0 rows inserted, so just insert
    cursor = conn.execute(
        'UPDATE caixa_config SET saldo_inicial = ? WHERE usuario_id = ?',
        (float(saldo_inicial), usuario_id)
    )
    if cursor.rowcount == 0:
        conn.execute('INSERT INTO caixa_config (saldo_inicial, usuario_id) VALUES (?, ?)', (float(saldo_inicial), usuario_id))
        
    conn.commit()
    conn.close()
    return jsonify({'saldo_inicial': float(saldo_inicial)})

# ─────────────────────────────────────────────
# API - Resumo Mensal
# ─────────────────────────────────────────────

@app.route('/api/resumo', methods=['GET'])
@require_auth
def resumo_mensal(usuario_id):
    mes = request.args.get('mes', datetime.now().strftime('%m'))
    ano = request.args.get('ano', datetime.now().strftime('%Y'))

    conn = get_db()

    total_gastos = conn.execute(
        '''SELECT COALESCE(SUM(valor), 0) as total FROM gastos WHERE data LIKE ? AND usuario_id = ?''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)
    ).fetchone()

    total_receitas = conn.execute(
        '''SELECT COALESCE(SUM(valor), 0) as total FROM receitas WHERE data LIKE ? AND usuario_id = ?''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)
    ).fetchone()

    por_categoria = conn.execute(
        '''SELECT c.id, c.nome, c.cor, COALESCE(SUM(g.valor), 0) as total
           FROM categorias c
           LEFT JOIN gastos g ON g.categoria_id = c.id
             AND g.data LIKE ? AND g.usuario_id = ?
           WHERE c.usuario_id = ?
           GROUP BY c.id HAVING COALESCE(SUM(g.valor), 0) > 0 ORDER BY total DESC''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id, usuario_id)
    ).fetchall()

    contagem = conn.execute(
        '''SELECT COUNT(*) as quantidade FROM gastos WHERE data LIKE ? AND usuario_id = ?''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)
    ).fetchone()

    total_investimentos = conn.execute(
        '''SELECT COALESCE(SUM(valor), 0) as total FROM investimentos WHERE data LIKE ? AND usuario_id = ?''',
        (f"{ano}-{mes.zfill(2)}-%", usuario_id)
    ).fetchone()

    receitas_val = total_receitas['total']
    gastos_val = total_gastos['total']
    investimentos_val = total_investimentos['total']

    config = conn.execute('SELECT saldo_inicial FROM caixa_config WHERE usuario_id = ?', (usuario_id,)).fetchone()
    saldo_inicial = config['saldo_inicial'] if config else 0

    mes_int = int(mes)
    ano_int = int(ano)
    if mes_int == 1:
        prev_mes = 12
        prev_ano = ano_int - 1
    else:
        prev_mes = mes_int - 1
        prev_ano = ano_int
    limite_anterior = f'{prev_ano}-{str(prev_mes).zfill(2)}-31'

    prev_receitas = conn.execute(
        '''SELECT COALESCE(SUM(valor), 0) as total FROM receitas WHERE data <= ? AND usuario_id = ?''',
        (limite_anterior, usuario_id)
    ).fetchone()['total']

    prev_gastos = conn.execute(
        '''SELECT COALESCE(SUM(valor), 0) as total FROM gastos WHERE data <= ? AND usuario_id = ?''',
        (limite_anterior, usuario_id)
    ).fetchone()['total']

    caixa = saldo_inicial + prev_receitas - prev_gastos
    total_disponivel = caixa + receitas_val - gastos_val
    saldo = receitas_val - gastos_val - investimentos_val

    conn.close()

    return jsonify({
        'mes': mes,
        'ano': ano,
        'total_gastos': gastos_val,
        'total_receitas': receitas_val,
        'total_investimentos': investimentos_val,
        'saldo': saldo,
        'caixa': caixa,
        'total_disponivel': total_disponivel,
        'saldo_inicial': saldo_inicial,
        'quantidade': contagem['quantidade'],
        'por_categoria': [dict(c) for c in por_categoria]
    })


# ─────────────────────────────────────────────
# API - Conversão de Moedas (pública)
# ─────────────────────────────────────────────

@app.route('/api/conversao', methods=['GET'])
def converter_moeda():
    valor = request.args.get('valor', 0, type=float)
    de = request.args.get('de', 'BRL').upper()
    para = request.args.get('para', 'USD').upper()

    try:
        resp = http_requests.get(f'{EXCHANGE_API_URL}/{de}', timeout=5)
        dados = resp.json()

        if dados.get('result') != 'success':
            return jsonify({'erro': 'Erro ao consultar taxa de câmbio'}), 502

        taxa = dados['rates'].get(para)
        if taxa is None:
            return jsonify({'erro': f'Moeda {para} não encontrada'}), 400

        convertido = round(valor * taxa, 2)

        return jsonify({
            'valor_original': valor,
            'moeda_origem': de,
            'moeda_destino': para,
            'taxa': taxa,
            'valor_convertido': convertido
        })
    except http_requests.RequestException:
        return jsonify({'erro': 'Falha na conexão com API de câmbio'}), 502


# ─────────────────────────────────────────────
# Inicialização
# ─────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("="*50)
    print("  Organizador de Custos - Servidor Iniciado")
    print("  Acesse: http://localhost:5000")
    print("="*50)
    app.run(debug=True, port=5000)
