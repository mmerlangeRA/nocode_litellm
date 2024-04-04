# nocode_litellm

## install and start

### Virtual env

pyenv install 3.11
pyenv local 3.11
python3.11 -m venv venv
source venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Start server

export LLM_PROFILES=local
python -m uvicorn server.main:app --reload --port 8001

## generate documentation

export LLM_PROFILES=local
python -m scripts.extract_openapi server.main:app --out docs/openapi.json

## Main concepts

Routes call services. A route should call one service.

* A service :
  * has an id a description and watches consumptions
  * uses tools to perform its tasks


## Todo
* chromadb in production ?
* RAG

## dumping database

brew install supabase/tap/supabase
brew install postgresql
supabase login

brew install supabase-pgdump
supabase-pgdump -h aws-0-eu-central-1.pooler.supabase.com -p 5432 -U postgres.lpiddfefyyiitpnjwjrh -d postgres > dump.sql

read https://colab.research.google.com/github/mansueli/Supa-Migrate/blob/main/Migrate_Postgres_Supabase.ipynb

/opt/homebrew/Cellar/postgresql@15/15.6_1/bin/pg_dump  -h aws-0-eu-central-1.pooler.supabase.com -p 5432 -U postgres.lpiddfefyyiitpnjwjrh -d postgres > dump.sql

pg_dump -h db.lpiddfefyyiitpnjwjrh.supabase.co -p 5432 -U YOUR_DB_USER -W -d YOUR_DB_NAME > supabase_dump.sql

postgres://postgres.lpiddfefyyiitpnjwjrh:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:5432/postgres

docker build -t nocode_litellm:latest .
docker run -d -p 8001:8001 nocode_litellm:latest


