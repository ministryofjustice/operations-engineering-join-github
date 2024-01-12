FROM python:3.12.0-alpine3.18

LABEL maintainer="operations-engineering <operations-engineering@digital.justice.gov.uk>"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup -u 1051

RUN apk add --no-cache --no-progress \
  build-base \
  curl \
  && apk update \
  && apk upgrade --no-cache --available

WORKDIR /home/operations-engineering-jon-github

COPY requirements.txt requirements.txt
COPY join_github_app join_github_app
COPY operations_engineering_join_github.py operations_engineering_join_github.py

RUN pip3 install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

USER 1051

EXPOSE 4567

HEALTHCHECK --interval=60s --timeout=30s CMD curl -I -XGET http://localhost:4567 || exit 1

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:4567", "operations_engineering_join_github:app()"]
