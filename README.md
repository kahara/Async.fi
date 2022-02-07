# async.fi main site

## Local development

```console
sudo snap install hugo
hugo server -D # http://localhost:1313/
hugo new posts/postname.md
```

## Deploying

```
sudo snap install hugo
hugo
docker-compose build --no-cache
docker-compose up -d
```
