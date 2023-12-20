if ! [ -f "/data/crontab" ]
then
    touch /data/crontab
    echo "SHELL=/bin/bash" >> /data/crontab
    echo "PATH=/usr/local/bin:/usr/bin:/bin" >> /data/crontab
    echo "# m h  dom mon dow   command" >> /data/crontab
    echo "*/5 * * * * crontab /data/crontab" >> /data/crontab
    echo "#############example#############\n" >> /data/crontab
    echo "# 55 7 * * 5 python /workspace/src/main.py -s 22220000123 -p password -d 15\n"  >> /data/crontab
    echo "##################################"  >> /data/crontab
fi
crontab /data/crontab 
cron -f 