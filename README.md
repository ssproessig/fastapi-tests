# fastapi-tests
## Building and running the container itself
```
$  docker build . -t fastapi-tests:latest

$  docker run -it  --rm -p 8000:8000 fastapi-tests:latest
```

## Using docker-compose to start up OAuth 2 integration
In order to use Keycloak as _Authorization Server_ you can use `docker-compose` to manage all required containers. Remember to build the `fastapi-tests` container first.

```
$ docker-compose up
...
$ docker-compose down
```
