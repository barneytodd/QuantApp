#!/bin/sh

TEMPLATE=/usr/share/nginx/html/config/runtime.template.json
TARGET=/usr/share/nginx/html/config/runtime.json

echo "Generating runtime config file..."

mkdir -p /usr/share/nginx/html/config/

sed \
  -e "s|__REACT_APP_BACKEND_PORT__|${REACT_APP_BACKEND_PORT}|g" \
  $TEMPLATE > $TARGET

echo "Runtime config generated:"
cat $TARGET

exec "$@"
