FROM python:3.8

# install crontab
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get autoremove -y && \
    apt-get clean -y &&\
    rm -rf /var/lib/apt/lists/*

COPY . workspace
WORKDIR workspace

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    playwright install chromium

RUN mkdir -p "/data" && \
    ln -s /etc/crontab docker/data
