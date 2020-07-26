# fastapi-tests
## Building and running the container itself
```
$  docker build . -t fastapi-tests:latest

$  docker run -it  --rm -p 8000:8000 fastapi-tests:latest
```

