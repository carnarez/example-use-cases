Quick consuming code, to be extended with OCR logic for instance.

To get an image from the received string:

```python
jpg = base64.b64decode(payload["capture"].encode("ascii"))
```

or

```python
jpg = base64.b64decode(b'{payload["capture"]}')
```
