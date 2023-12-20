FROM python:3.11-slim-bookworm

COPY . /app
RUN pip install -r /app/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 5000
CMD ["flask","run","--host=0.0.0.0"]