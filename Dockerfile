FROM python:3-buster

WORKDIR /usr/src/app

RUN apt update
RUN apt upgrade -y
RUN apt install wget -y
RUN apt install firefox-esr -y

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz
RUN tar -xvzf geckodriver*
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin/

RUN apt install chromium -y
RUN wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
RUN unzip chromedriver_linux64.zip
RUN chmod +x chromedriver
RUN mv chromedriver /usr/local/bin/

COPY requirements.txt ./
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN mkdir images

COPY . .
EXPOSE 8080

ENTRYPOINT ["python3","-u","./main.py" ]