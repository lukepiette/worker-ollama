FROM ollama/ollama:0.6.2

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --no-cache-dir -r /requirements.txt

COPY handler.py /handler.py
COPY test_input.json /test_input.json
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV OLLAMA_KEEP_ALIVE=-1 \
    OLLAMA_HOST=127.0.0.1:11434

ENTRYPOINT []
CMD ["/start.sh"]
