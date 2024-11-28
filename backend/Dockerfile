FROM python:3.13-alpine

WORKDIR /app

RUN addgroup -S app && adduser -S app -G app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

RUN chown -R app:app /app
USER app

ENTRYPOINT ["/app/entrypoint.sh"]