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

python -m uvicorn server.main:app --reload --port 8001

## generate documentation

export LLM_PROFILES=local
python -m scripts.extract_openapi server.main:app --out docs/openapi.json

## Main concepts

Routes call services. A route should call one service.

* A service :
  * has an id a description and watches consumptions
  * uses tools to perform its tasks
