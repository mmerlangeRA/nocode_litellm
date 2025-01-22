# nocode_litellm

## Description

This backend provides APIs for LLM and RAG application. It's a work in progress using :

- FastAPI
- langchain

## Local installation and development

### Virtual env

pyenv install 3.11
pyenv local 3.11
python3.11 -m venv venv
source venv/bin/activate

### Install dependencies

pip install -r requirements.txt

### Start server

You need to select a profile. For instance if you use "local", you need to have a settings-local.yaml file as described in settings/settings.py. Example provided in settings-example.yaml

```bash
export LLM_PROFILES=local
python -m uvicorn server.main:app --reload --port 8001 --host 0.0.0.0


```

## Docker installation

docker-compose up -d

NB : set settings-local.yaml accordingly for chroma settings !

About chromadb:

- Please note that chromadb files (used for RAG) are saved as Volume in chroma-data folder.
- Feel free to change the path.
- Copying folder content should work.

## Documentation

APIs are fully available at site-url/docs

### Generation

```bash
export LLM_PROFILES=local
python -m scripts.extract_openapi server.main:app --out docs/openapi.json
```
