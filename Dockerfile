FROM python:3.8

# install crontab
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get install -y libgl1 && \
    apt-get autoremove -y && \
    apt-get clean -y &&\
    rm -rf /var/lib/apt/lists/*

COPY . workspace
WORKDIR /workspace

RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple  && \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    playwright install chromium && \ 
    playwright install-deps && \
    mkdir -p "/data" && \ 
    chmod +x /workspace/scripts_docker/run.sh && \
    rm -f /etc/localtime && \
    ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

CMD ["sh", "/workspace/scripts_docker/run.sh"]
