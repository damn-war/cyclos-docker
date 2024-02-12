FROM python:3.11.4

WORKDIR /usr/src/app

COPY ./ad-notification/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./ad-notification/src/* /usr/src/app

CMD [ "python", "/usr/src/app/ad_notification.py"]
