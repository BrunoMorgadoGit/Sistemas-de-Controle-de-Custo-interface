# Organizador de Custos — Interface e Backend (Flask SSR)

Aplicação Flask com renderização server-side (Jinja2) para controle financeiro pessoal: gastos, receitas, investimentos, categorias e saldo de caixa.

## Visão geral

- Backend: Flask + Jinja2 (server-side rendering)
- Banco: Supabase / PostgreSQL (configurado via `DATABASE_URL` no `.env`)
- ORM: Flask-SQLAlchemy; migrações com Flask-Migrate/Alembic
- Autenticação: sessões Flask (login por Email / registro)
- Frontend: templates Jinja2 em `templates/`, assets em `static/` (JS modular e CSS responsivo)

## Requisitos

- Python 3.11+ (virtualenv recomendado)
- Windows / macOS / Linux

## Instalação rápida

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um virtualenv:

PowerShell (Windows):

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

Bash / macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
```

1. Instale dependências:

```bash
pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env` (opcional) para sobrescrever valores padrão:

```
SECRET_KEY=uma_chave_secreta
DATABASE_FILE=/caminho/para/banco.db  # por padrão usa ./banco.db
```

As configurações estão em `app/config/settings.py`.

## Migrações (Flask‑Migrate / Alembic)

Uso básico com o CLI `flask` (defina `FLASK_APP` apontando para `server.py`):

PowerShell:

```powershell
$Env:FLASK_APP = "server.py"
flask db init        # somente se ainda não existir a pasta migrations
flask db migrate -m "mensagem"
flask db upgrade
```

Bash / macOS:

```bash
export FLASK_APP=server.py
flask db init
flask db migrate -m "mensagem"
flask db upgrade
```

Nota: o projeto já contém integração com Flask‑Migrate e um listener que habilita `PRAGMA foreign_keys = ON` para cada conexão SQLite.

## Executando a aplicação (desenvolvimento)

O entrypoint é `server.py`. Para executar em modo de desenvolvimento:

```bash
python server.py
```

Depois acesse: <http://localhost:5000>

Também é possível usar `flask run` desde que `FLASK_APP` esteja definido para `server.py`.

## Estrutura de templates importantes

- `templates/base.html` — layout base com sidebar e blocos Jinja (`content`, `extra_head`, `extra_scripts`, `extra_data`)
- `templates/dashboard.html` — cards e gráfico (Chart.js carregado apenas aqui)
- `templates/gastos.html`, `receitas.html`, `investimentos.html`, `categorias.html`, `ferramentas.html` — páginas separadas para cada domínio
- `templates/login.html` — autenticação

## Assets e comportamento do frontend

- `static/app.js` foi modularizado (funções: `initChart()`, `initCaixaToggle()`, `initConversor()`, `setupGlobalToast()`, `initSidebar()`) e executa cada módulo apenas quando os elementos necessários estão na página.
- `static/style.css` agora inclui layout de sidebar e melhorias de responsividade: formulários full-width, tabelas com scroll horizontal em viewports estreitos e grids que se adaptam.

## Rotas principais (SSR)

- `GET /login` — página de login
- `POST /register` — criar conta
- `GET /` — dashboard (requer sessão)
- `GET /gastos`, `GET /receitas`, `GET /investimentos`, `GET /categorias`, `GET /ferramentas` — páginas dedicadas
- `POST /gastos`, `POST /receitas`, `POST /investimentos` — criar/editar (formulários)
- `POST /categorias` — criar categoria
- `POST /caixa` — atualizar saldo inicial
- `GET /api/conversao` — API de conversão de moedas (JSON)
