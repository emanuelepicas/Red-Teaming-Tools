#!/bin/bash

systemctl stop nginx.service

if [[ -d "/var/www/html/website/site_builder_2" ]]; then
    rm -rf /var/www/html/website/site_builder_2
fi

mv /tmp/site_builder_2 /var/www/html/website

echo "restarting"

systemctl start nginx.service
