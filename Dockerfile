FROM ollama/ollama:0.6.2

RUN apt-get update && \
    apt-get install -y --no-install-recommends software-properties-common curl ca-certificates && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends python3.11 python3.11-distutils && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN python3.11 -m pip install --no-cache-dir -r /requirements.txt

COPY handler.py /handler.py
COPY test_input.json /test_input.json
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV OLLAMA_KEEP_ALIVE=-1 \
    OLLAMA_HOST=127.0.0.1:11434

ENTRYPOINT []
CMD ["/start.sh"]
