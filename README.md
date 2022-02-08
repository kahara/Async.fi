# async.fi main site

## Local development

```console
sudo snap install hugo
hugo server -D # http://localhost:1313/
hugo new posts/postname.md
```

Test with Caddy:

```
sudo snap install hugo
hugo && docker-compose build --no-cache && docker-compose up
```

## Deploy

```console
docker build --no-cache --tag jonikahara/www-async-fi:latest .
docker push jonikahara/www-async-fi:latest
```

Then, where
[sites.async.fi](https://github.com/kahara/sites.async.fi)
composition is running:

```console
docker-compose pull
docker-compose restart www
```
