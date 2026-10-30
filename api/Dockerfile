FROM python:3.11-slim
WORKDIR /srv
ENV PIP_NO_CACHE_DIR=1 DATA_DIR=/srv/data
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY data ./data
COPY api/app ./app
EXPOSE 8000
HEALTHCHECK --interval=5s --timeout=5s --retries=20 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
