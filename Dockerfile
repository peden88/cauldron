FROM python:3.12-slim

WORKDIR /srv

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
	CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/ready', timeout=3)" || exit 1

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
