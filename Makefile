.PHONY: install run llm-pull llm-start llm-stop

install:
	sudo apt-get install zstd && curl -fsSL https://ollama.com/install.sh | sh
	ollama pull qwen3.5:2b
	python3 -m venv service/.venv
	service/.venv/bin/pip install --upgrade pip
	service/.venv/bin/pip install -r service/requirements.txt

llm-start:
	ollama run qwen3.5:2b  --think=false > /dev/null 2>&1 &

llm-stop:
	ollama stop qwen3.5:2b

start: llm-start
	@until curl -sf http://localhost:11434/api/ps | grep -q qwen3.5 > /dev/null 2>&1; do sleep 1; done
	service/.venv/bin/fastapi dev service/main.py

stop: llm-stop