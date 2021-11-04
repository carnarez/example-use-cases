API_URI="$API_PROTOCOL://$API_HOST"
if [ $API_PROTOCOL == "http" ]; then API_URI="$API_URI:$API_PORT"; fi
sed -i "s|API_URI|$API_URI|g" /var/www/http/index.html

thttpd -D -l /dev/null -d /var/www/http
