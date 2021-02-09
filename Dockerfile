FROM python:3.9

WORKDIR /bartender
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .

ENTRYPOINT ["python"]

CMD ["bot.py"]