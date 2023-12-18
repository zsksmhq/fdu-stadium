if ! [ -f "/data/crontab" ]
then
    cp /etc/crontab /data
    crontab /data/crontab 
fi
cron -f 