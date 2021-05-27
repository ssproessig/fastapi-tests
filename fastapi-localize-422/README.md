# Localization of 422 error messages

## Basic Service
A REST service that allows

- `POST`ing `Foo`s:
  ```
  curl http://localhost:8000/foos -X POST -d "{\"name\":\"Name1\"}"
  ```
- `GET`ting list of `Foo`s:
  ```
  curl http://localhost:8000/foos
  [{"name":"Name1","tags":[],"id":"d2c8f9f2-cab7-41f9-a1c4-91e4584c71f3"}]
  ```

If you `POST` broken data, `pydantic` will create an error message that is returned by `fastapi`
as `422 Unprocessable Entity`:

```
C:\Users\ssp>curl http://localhost:8000/foos -s -X POST -d "{\"nam\":null}" | jq .
```
```json
{
  "detail": [
    {
      "loc": [
        "body",
        "name"
      ],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}

```

```
C:\Users\ssp>curl http://localhost:8000/foos -s -X POST -d "{\"name\":null}" | jq .
```

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "name"
      ],
      "msg": "none is not an allowed value",
      "type": "type_error.none.not_allowed"
    }
  ]
}

```

```
C:\Users\ssp>curl http://localhost:8000/foos -s -X POST -d "{\"name\":\"x\",\"tags\":[null]}" | jq .
```

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "tags",
        0
      ],
      "msg": "none is not an allowed value",
      "type": "type_error.none.not_allowed"
    }
  ]
}

```

```
C:\Users\ssp>curl http://localhost:8000/foos -s -X POST -d "{\"name\":\"01234567890\",\"tags\":[null]}" | jq .
```

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "name"
      ],
      "msg": "ensure this value has at most 10 characters",
      "type": "value_error.any_str.max_length",
      "ctx": {
        "limit_value": 10
      }
    },
    {
      "loc": [
        "body",
        "tags",
        0
      ],
      "msg": "none is not an allowed value",
      "type": "type_error.none.not_allowed"
    }
  ]
}
```

## Task: localize the response
If we want to display this error message in the GUI, we can't easily use the GUI frameworks
localization means for it, as the `msg` already has its placeholders replaced with the actual faulty
values. Hence, we need a way how the invoker of the API can already tell the FastAPI application in
which language the error SHALL be returned.

## Solution
Make the API user request the language her request shall be processed. There is already an HTTP
header for that: [`Accept-Language`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)
