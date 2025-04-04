
FROM python:3.12

WORKDIR /project

ADD . /project/backend

RUN pip install -r /project/backend/requirements.txt

ENV APP_CONFIG_PATH=/project/backend/config.yml

CMD ["fastapi", "dev", "--host", "0.0.0.0", "/project/backend/src/service.py"]

EXPOSE 8000