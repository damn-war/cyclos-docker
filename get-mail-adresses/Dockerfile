FROM python:3.11.4

WORKDIR /usr/src/app

COPY ./get-mail-adresses/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./get-mail-adresses/src/* /usr/src/app

CMD [ "python", "/usr/src/app/get-mail-adresses.py"]
