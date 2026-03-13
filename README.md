# Organizador de Custos — Flask SSR

Aplicação Flask com renderização server-side (Jinja2) para controle financeiro pessoal: gastos, receitas, investimentos, categorias e saldo de caixa.

## Stack atual

- Backend: Flask 3 + Blueprints
- ORM e migrações: Flask-SQLAlchemy + Flask-Migrate/Alembic
- Banco de dados: Supabase PostgreSQL com `psycopg2-binary`
- Segurança: sessão Flask, CSRF (`Flask-WTF`) e rate limiting (`Flask-Limiter`)
- Frontend: templates Jinja2 em `templates/` e assets em `static/`

## Requisitos

- Python 3.11+ ou superior
- pip
- Banco acessível via `DATABASE_URL`

## Instalação

1. Clone o repositório e entre no diretório.
2. Crie e ative um ambiente virtual.

PowerShell:

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Variáveis de ambiente

Crie um arquivo `.env` com os valores mínimos:

```env
SECRET_KEY=sua_chave_forte
DATABASE_URL=sua_url_do_banco
FLASK_ENV=development
FLASK_DEBUG=1
CORS_ORIGINS=sua_origem_frontend (ex: http://localhost:5000)
```

Observações:

- `SECRET_KEY` ausente gera chave aleatória e invalida sessões a cada restart.
- `DATABASE_URL` deve apontar para o banco em uso.
- `CORS_ORIGINS` aceita múltiplas origens separadas por vírgula.

## Migrações

Com `FLASK_APP=server.py`:

PowerShell:

```powershell
$Env:FLASK_APP = "server.py"
flask db migrate -m "mensagem"
flask db upgrade
```

macOS/Linux:

```bash
export FLASK_APP=server.py
flask db migrate -m "mensagem"
flask db upgrade
```

Se for o primeiro setup e não existir `migrations/`, rode `flask db init` uma vez.

## Executando em desenvolvimento

```bash
python server.py
```

A aplicação sobe em `http://localhost:5000`.

## Segurança aplicada no projeto

- Proteção CSRF ativa para rotas de formulário.
- Rate limit padrão global e limites específicos em autenticação.
- Cookies de sessão com `HttpOnly`, `SameSite=Lax` e `Secure` em produção.
- Headers de segurança adicionados em `after_request`.

## Rotas principais

- `GET /login` e `POST /login`
- `POST /register`
- `POST /logout`
- `GET /` (dashboard)
- `GET/POST /gastos`
- `GET/POST /receitas`
- `GET/POST /investimentos`
- `GET/POST /categorias`
- `POST /caixa`
- `GET /api/conversao` (requer sessão)

## Estrutura resumida

- `app/controllers/`: regras de negócio por domínio
- `app/routes/`: endpoints e integração HTTP
- `app/models/`: entidades e mapeamento ORM
- `app/middlewares/`: validação de sessão
- `templates/` e `static/`: camada de apresentação
