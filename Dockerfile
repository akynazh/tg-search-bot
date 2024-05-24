FROM python:3.10

ENV TZ Asia/Shanghai

WORKDIR /app

COPY . .

RUN pip3 install -U -r requirements.txt

CMD [ "python3", "bot.py" ]