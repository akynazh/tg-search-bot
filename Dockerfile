FROM python:3.10

WORKDIR /app

COPY . .

RUN pip3 install -U -r requirements.txt

CMD [ "python3", "bot.py" ]
