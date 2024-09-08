# blog-api

## Getting Started

### Docker

```bash
docker build -t blog-api .

docker volume create blog-api-data

docker run --env-file=.env -p 5000:5000 -v /root/blog-api-data:/uploads blog-api
```