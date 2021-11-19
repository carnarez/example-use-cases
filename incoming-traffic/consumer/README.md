Consumer example code snippet, to be extended with OCR logic for instance. Currently
listening to messages posted on the `snapshots` feed hosted by
[`Redis Streams`](https://redis.io/topics/streams-intro).

To get an image from the received string:

```python
jpg = base64.b64decode(payload["capture"].encode("ascii"))
```

or

```python
jpg = base64.b64decode(b'{payload["capture"]}')
```
