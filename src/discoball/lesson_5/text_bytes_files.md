# Side quest 2: Text, bytes, and files

A filename, a category label, a CSV document, and a downloaded file are not all the
same kind of data. In this side quest, you will manipulate text, understand its
relationship to bytes, and use parsers rather than inventing a file format reader.

Allow 60–90 minutes. Complete [Containers](containers.md) first. Use the lesson's
`practice.py` for small experiments. The worked example writes only synthetic data
to `src/discoball/lesson_5/outputs/`, never into the source `olist/` directory.

## 1. Strings are text values, not editable character arrays

```python
label = "  Health_Beauty  "
cleaned = label.strip()
print(label)
print(cleaned.replace("_", " ").lower())
print(cleaned.startswith("Health"))
print(cleaned[:6])
```

A string is immutable. Methods such as `strip`, `replace`, and `lower` return a
result; they do not edit `label`. Assign the result when you want to keep it.
Slicing follows the same start-inclusive, end-exclusive convention as lists.

Do not normalize identifiers merely because it makes them look nicer. Two distinct
source keys can collapse to the same cleaned label. Keep analytical identity and
display labels separate.

For caseless text comparison, `casefold()` is more comprehensive than `lower()`
for some Unicode characters. Neither automatically removes accents or implements
a complete business matching policy.

**Your turn:** inspect `label` after calling `label.strip()` without assignment.
Explain why it is unchanged. Where should cleaning occur if you also need to
preserve the original value for investigation?

## 2. Split and join deliberately

```python
parts = "orders,products,customers".split(",")
print(parts)
print(" | ".join(parts))
```

`split` creates a list. `join` uses a separator string to combine text elements.
`join` does not automatically convert integers into strings. For mixed values,
convert explicitly where that conversion makes sense.

These are useful text tools, not a general CSV parser. A CSV field can contain a
comma inside quotes; splitting every line on commas would corrupt that field.

## 3. Distinguish characters from encoded bytes

```python
text = "Café"
payload = text.encode("utf-8")
print(len(text))
print(payload)
print(len(payload))
print(payload.decode("utf-8"))
```

Expect four Unicode code points in this string and five UTF-8 bytes. The `é` uses
two bytes in UTF-8. A string's length counts code points, not necessarily visible
characters in every language: a displayed symbol can contain multiple code points.

- `str` represents Unicode text.
- `bytes` represents an immutable sequence of byte values, each from 0 to 255.
- **Encoding** converts text to bytes.
- **Decoding** interprets bytes using an encoding to obtain text.

A bytes representation often begins with `b` when displayed. Indexing bytes gives
an integer byte value; indexing a string gives a one-character string. A string
method is not automatically interchangeable with a bytes method or argument.

Try `payload.decode("ascii")`. It raises `UnicodeDecodeError` because ASCII cannot
interpret this UTF-8 sequence. Recover using the known UTF-8 encoding. Do not
reflexively use `errors="ignore"`: that can silently delete meaningful data.
Some wrong encodings produce garbled text without an exception, so successful
decoding alone is not proof that the chosen encoding is correct.

Use bytes for binary files, compressed content, raw network payloads, or exact
byte-level checks. Decode known text at the boundary and use strings for ordinary
text manipulation. CSV and JSON text usually do not need a manual binary step.

## 4. Choose a file mode and manage its lifetime

| Mode | Purpose | Caution |
| --- | --- | --- |
| `"r"` | Read text; the default | File must exist. Specify the encoding. |
| `"w"` | Write text | Creates or truncates the file immediately. |
| `"a"` | Append text | Does not ensure the appended text preserves a structured format. |
| `"x"` | Create a new text file | Fails if the path already exists. |
| `"rb"` / `"wb"` | Read/write bytes | Do not supply a text encoding. `wb` truncates too. |

`Path` manages a location; opening it creates a file handle. A `with` block closes
that handle even if an error occurs. Reading does not imply loading the whole
file: you can iterate over a text file line by line.

```python
from discoball.const import OLIST_DIR

with (OLIST_DIR / "orders.csv").open(encoding="utf-8") as source:
    for position, line in enumerate(source, start=1):
        print(position, line.rstrip("\r\n"))
        if position == 3:
            break
```

This reads three physical lines, not a general three-record CSV sample: quoted
CSV fields can span lines. Use the CSV parser for records. Also, `strip()` removes
all surrounding whitespace, which may be meaningful; removing only newline
characters can be more appropriate for plain-text inspection.

## 5. Read and write CSV with its parser

Run [examples/text_files.py](examples/text_files.py):

```powershell
uv run python -m discoball.lesson_5.examples.text_files
```

It creates `category_review.csv` and `category_review.json` in the lesson's
`outputs/` folder. The example explicitly replaces these two generated files on
reruns. Keep your own important work elsewhere. The folder is ignored by Git,
not protected from deletion, leakage, or accidental overwriting.

Inspect the code and the CSV file. One label contains a comma, so the writer quotes
it correctly. `csv.DictReader` supplies a dictionary per record, keyed by header
name. `csv.reader` instead supplies a list of fields per record.

For CSV text files, open with `encoding="utf-8", newline=""` so the CSV module
controls newline handling. Writing uses `DictWriter`, an explicit field list,
`writeheader()`, and `writerows(...)`.

The reader returns text fields in this example, even for `basket_count`. The
example intentionally converts a count with `int(...)` before calculation. An
empty field is normally an empty string, not automatically Python `None` or SQL
`NULL`. Decide how empty and invalid values should be handled.

**Your turn:** change one synthetic count to `"unknown"` and rerun. Locate the
conversion error, restore the valid value, and run successfully. Do not change
real Olist data to test failure handling.

CSV files opened in a spreadsheet can also be interpreted as formulas. CSV quoting
is not a security control against that interpretation. Follow the approved export
policy when distributing untrusted text to spreadsheet users.

## 6. Read and write JSON deliberately

| Operation | File handle | String in memory |
| --- | --- | --- |
| Parse JSON into Python values | `json.load(source)` | `json.loads(text)` |
| Serialize Python values as JSON | `json.dump(value, target)` | `json.dumps(value)` |

The final `s` stands for a string-oriented operation, not a plural collection.

```python
import json

text = '{"category": "A", "basket_count": 4, "approved": false}'
record = json.loads(text)
print(record["basket_count"] + 1)
print(record["approved"] is False)
print(json.dumps(record, indent=2))
```

JSON objects become dictionaries, arrays become lists, strings remain strings,
and `true`, `false`, and `null` become `True`, `False`, and `None`. Numeric JSON
values normally become Python integers or floats. In contrast to the CSV example,
the JSON count is already an integer.

Parsing JSON establishes syntax, not your business schema. A parsed record can
still be missing fields or contain inappropriate types. Dates, `Decimal` values,
and custom objects are not automatically supported by the default encoder.
Tuples serialize as arrays and read back as lists, so not every Python type
round-trips unchanged.

`ensure_ascii=False` keeps characters such as `é` readable in the written JSON;
the text file's encoding still determines how those characters become bytes.

Do not append independent `json.dump` calls to one file and expect a valid JSON
document. Write one complete document, or explicitly choose another format such
as newline-delimited JSON with a matching reader. This exercise writes one array.

## Finish with a format choice

Compare the generated CSV and JSON. Explain which types each parser returns, how
commas in labels are preserved, and where type validation is still needed. Choose
a format for a human review extract and one for a nested application payload,
noting the receiving tool's requirements rather than declaring one format best.

Continue to [Numbers and calculations](numbers.md), or return to
[Lesson 5](README.md).
