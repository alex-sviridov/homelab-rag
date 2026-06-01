install:
	sudo apt-get install zstd && curl -fsSL https://ollama.com/install.sh | sh

llm-pull:
	ollama pull qwen3.5:2b

llm-start:
	ollama run qwen3.5:2b  --think=false > /dev/null 2>&1 &

llm-stop:
	ollama stop qwen3.5:2b