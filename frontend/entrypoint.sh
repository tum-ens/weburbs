#!/bin/sh

# Replace the API URL in the config.json file
echo "{ \"VUE_APP_API_URL\": \"${VUE_APP_API_URL}\" };" > /usr/share/nginx/html/config.js

# Start nginx
nginx -g "daemon off;"
