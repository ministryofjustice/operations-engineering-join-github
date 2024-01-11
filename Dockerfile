FROM python:3.12.0-alpine3.18

RUN addgroup -S appgroup && adduser -S appuser -G appgroup -u 1051

RUN apk add --no-cache --no-progress build-base \
  && apk update \
  && apk upgrade --no-cache --available

WORKDIR /home/operations-engineering-poc-landing-page

COPY requirements.txt requirements.txt
COPY landing_page_app landing_page_app
COPY operations_engineering_landing_page.py operations_engineering_landing_page.py

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

HEALTHCHECK --interval=5m --timeout=3s \
  CMD ["curl", "-f", "http://localhost/"]

USER 1051

EXPOSE 4567

ENTRYPOINT gunicorn operations_engineering_landing_page:app \
  --bind 0.0.0.0:4567 \
  --timeout 120