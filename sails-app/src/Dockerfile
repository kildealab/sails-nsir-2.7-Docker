FROM python:2.7

USER root

WORKDIR /app

COPY ./requirements/sails_requirements.txt /app
RUN pip install pip --upgrade
RUN pip install -r sails_requirements.txt

COPY ./ils/ /app

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
