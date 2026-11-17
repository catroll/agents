# read_image fails with "model does not declare image input"

## Signal

```
read_image -> Error: cannot read "<path>" as an image: model "deepseek-v4-flash"
does not declare image input; switch to an image-capable model to read images
```

`file <path>` still reports a valid JPEG/PNG, so the file is fine.

## Meaning

The running model has no vision channel. No path change, format conversion, or
retry helps; the guard is model capability, not file access.

## Check

When the task depends on pixels (scanned reports, WeChat screenshots, 评估报告
photos), look for a text source first (`grep` the diary / notes for the same
facts). If none exists, say the image was not read.

## Do instead

- Answer from the text record and name what could not be read.
- Ask the user to transcribe the few fields that matter, or
- switch to an image-capable model before loading the file.

Do not install OCR tooling as a workaround for this error, and do not diagnose
the file as corrupt.

## Negative result

`python3 -c "from PIL import Image; ..."` opening the file succeeds; the failure
is at the model boundary, not in the image.
