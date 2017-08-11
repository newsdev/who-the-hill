FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY ./ /usr/src/app/
RUN pip install --upgrade -r /usr/src/app/requirements.txt
EXPOSE 5000

CMD python /usr/src/app/app.py