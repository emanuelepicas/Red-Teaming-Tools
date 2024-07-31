#!/bin/bash

systemctl stop nginx.service

if [[ -d "/var/www/html/website/site_builder_1" ]]; then
    rm -rf /var/www/html/website/site_builder_1
fi

mv /tmp/site_builder_1 /var/www/html/website

echo "restarting"

systemctl start nginx.service
