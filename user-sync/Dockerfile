FROM python:3.11.4

WORKDIR /usr/src/app

COPY ./user-sync/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./user-sync/src/* /usr/src/app

CMD [ "python", "/usr/src/app/sync_users.py"]
