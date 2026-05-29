install:
	sudo apt-get install zstd && curl -fsSL https://ollama.com/install.sh | sh

pull:
	ollama pull qwen3.5:2b

run:
	ollama run qwen3.5:2b  --think=false

stop:
	ollama stop qwen3.5:2b