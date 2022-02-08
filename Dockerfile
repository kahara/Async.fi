FROM caddy@sha256:7da0f90273e1961d9c38d26809f84d4ef3cdc9b4fc330a9cab22015d7c9e8228

COPY Caddyfile /etc/caddy/Caddyfile
COPY public/ /var/www/html/
