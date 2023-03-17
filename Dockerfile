FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip3 install -U -r requirements.txt

CMD [ "python3", "bot.py" ]