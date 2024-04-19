FROM caddy@sha256:ca031cd33c788ebe467c94348400e5bf263178f9619f3993af8373f18681b8fd

COPY Caddyfile /etc/caddy/Caddyfile
COPY public/ /var/www/html/
