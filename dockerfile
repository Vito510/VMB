FROM python:3.10-alpine
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN apk update && \
    apk add --no-cache ffmpeg
CMD ["python", "./Vito's Music Bot.py"]