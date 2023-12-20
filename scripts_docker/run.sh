if ! [ -f "/data/crontab" ]
then
    cp /workspace/scripts_docker/crontab /data/crontab 
    touch /data/log
fi
crontab /data/crontab 
cron -f 