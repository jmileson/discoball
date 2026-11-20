# Side quest 5: Objects are data with useful behavior

You already use objects: strings, lists, dictionaries, and paths. You do not need
an elaborate object-oriented design to find them useful.

In this side quest, you will give a small analytical record a name and behavior,
then connect it to CSV and JSON. Allow 60–90 minutes. Complete
[Functions](functions.md) first.

## 1. Start with an object you know

```python
from discoball.const import OLIST_DIR

path = OLIST_DIR / "orders.csv"
print(path.name)
print(path.is_file())
```

`path` refers to an object representing a filesystem path. An **attribute** is a
named value associated with an object, accessed with a dot. `.name` gives the
filename. A **method** is behavior accessed through an object: `.is_file()` checks
whether that path points to an existing file.

Accessing an attribute and calling a method are different operations. Parentheses
matter: `path.is_file` refers to the method; `path.is_file()` invokes it.

A **class** defines a kind of object; an **instance** is a particular object of
that kind. You can use many classes without defining your own. You do not need
inheritance to understand or benefit from this idea.

## 2. Give a record named fields with a dataclass

Use this complete example in `practice.py`:

```python
from dataclasses import dataclass


@dataclass
class CategoryReview:
    category: str
    basket_count: int

    def describe(self) -> str:
        return f"{self.category}: {self.basket_count:,} baskets"


review = CategoryReview(category="A", basket_count=4)
print(review.category)
print(review.describe())
print(review)
```

The class names a record shape. The `@dataclass` line asks Python's standard
library to supply routine record behavior, including initialization and a readable
representation. Recognize this one helper; you do not need to learn how to write
decorators today.

Calling `CategoryReview(...)` creates an instance. `category` and `basket_count`
are its fields. The method's `self` parameter refers to the instance on which the
method was called. When you write `review.describe()`, Python supplies `review`
as `self`; you do not pass it again.

This object combines **data** and a small piece of **behavior**. It is not a
replacement for a dataframe holding hundreds of thousands of analytical rows.
Use ordinary records where they make a small workflow clearer.

**Your turn:** create a second instance. Change the first instance's count and
check that the second count is unchanged. Explain which data `self` uses in each
call.

## 3. Understand mutability and validation separately

An ordinary dataclass is mutable: `review.basket_count = 5` is permitted.
`@dataclass(frozen=True)` instead blocks ordinary field reassignment. It is a useful
signal of intent, not recursive immutability: a list stored in a frozen record
can still be mutated.

Type hints do not automatically validate construction. `CategoryReview("A", -4)`
is allowed by the class above. Passing an inappropriate type can also get through
construction and fail later. Validate external data deliberately rather than
assuming the class annotation made it safe.

Mutable field defaults need the same care as function defaults. If each instance
needs its own list, use a factory:

```python
from dataclasses import dataclass, field


@dataclass
class ReviewNotes:
    notes: list[str] = field(default_factory=list)


first = ReviewNotes()
second = ReviewNotes()
first.notes.append("Check coverage")
print(first.notes)
print(second.notes)
```

Expect one populated list and one empty list. `list` is passed as a factory to be
called for each instance. Dataclasses reject many unsuitable mutable defaults,
but understanding the ownership problem is still important.

## 4. Compare two alternatives without treating them as synonyms

| Tool | Runtime value | Useful when |
| --- | --- | --- |
| `dataclass` | An instance with named fields and optional methods | A small domain record with behavior |
| `NamedTuple` | A tuple subclass with named fields | A compact fixed record that also supports tuple operations |
| `TypedDict` | An ordinary dictionary | You want type-checking help for an existing dictionary shape |

### NamedTuple: names with tuple behavior

```python
from typing import NamedTuple


class CategoryPair(NamedTuple):
    category_a: str
    category_b: str


pair = CategoryPair("A", "B")
a, b = pair
print(pair.category_a)
print(a, b)
```

You can access fields by name or unpack them. `pair.category_a = "C"` fails
because fields cannot be reassigned. As with an ordinary tuple, mutable objects
inside fields remain mutable. A tuple of suitable immutable values can be a
useful key; not every named tuple is automatically a usable dictionary key.

### TypedDict: describe a dictionary, not a new runtime object

```python
from typing import TypedDict


class ReviewPayload(TypedDict):
    category: str
    basket_count: int


payload: ReviewPayload = {"category": "A", "basket_count": 4}
print(type(payload))
print(payload["category"])
```

Expect `dict`, not a custom `ReviewPayload` runtime type. This declaration helps
editors and type checkers identify missing keys or incorrect values in typed code.
It does not validate a dictionary parsed from JSON, prevent mutation, or make
`isinstance(payload, ReviewPayload)` a valid runtime check.

For this lesson, use dataclasses for the worked record, and recognize the other
two tools. You do not need to redesign every dictionary as a class.

## 5. Parse, validate, then construct

Read [examples/objects.py](examples/objects.py). Its `parse_review(raw)` function
accepts an unknown value from an external parser and checks it explicitly:

1. Is it a dictionary?
2. Does it contain non-blank category text?
3. Can a CSV count string be converted to an integer?
4. Is the resulting count a non-negative integer, not a boolean or fraction?
5. Only then, construct a `CategoryReview`.

The exact-type check for the count is intentional: in Python, `bool` is a subclass
of `int`, but `True` is not a sensible basket count. Do not generalize this into a
rule that every field needs an exact-type check; choose validation for the contract.

CSV supplies strings in this example; JSON supplies integer counts. Both readers
can therefore feed the same validation boundary. A parsed JSON document must also
have the expected outer list shape; parsing alone does not establish that.

**Your turn:** import `parse_review` in your practice file and try a normal record,
a missing category, a negative count, a fractional number, and a boolean count.
Predict which are accepted before running them. Read the failure message, correct
the input, and rerun; do not suppress every exception to make the loop finish.

## 6. Serialize deliberately

Run the worked example:

```powershell
uv run python -m discoball.lesson_5.examples.objects
```

It creates or replaces the same two synthetic output files from the text/files
side quest, parses both, and checks that their validated records agree. No Olist
source data is changed.

The default JSON writer does not serialize a dataclass instance directly. The
example uses `dataclasses.asdict(review)` to obtain a field dictionary, then
`json.dumps(...)` to produce text. This works because these fields contain simple
JSON-compatible values. A date or `Decimal` would still need an explicit policy.

Reading that JSON back returns a dictionary, not a reconstructed dataclass. Use
your validation and construction step again. Serialization preserves an agreed
representation, not arbitrary Python object identity or behavior.

## Finish with a representation choice

For each task, choose a dictionary, dataclass, named tuple, or dataframe and explain
why:

- Receiving a small JSON payload from another system.
- Representing one validated review record with a description method.
- Holding a pair of category keys.
- Calculating counts across 100,000 order-item records.

State what validation you still need. Choosing a type annotation or class does not
remove responsibility for checking external data.

Return to [Lesson 5](README.md), or continue to [Lesson 6](../lesson_6/README.md).
You now have additional tools to understand Python workflows, not a requirement
to use every feature in every analysis.
