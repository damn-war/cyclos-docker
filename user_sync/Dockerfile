FROM python:3.11.4

WORKDIR /usr/src/app

COPY ./user_sync/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./user_sync/src/* /usr/src/app

CMD [ "python", "/usr/src/app/sync_users.py"]
