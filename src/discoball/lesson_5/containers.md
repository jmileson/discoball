# Side quest 1: Organize values with containers

You have several input files, several checks, and several results. How should you
organize them without inventing a separate variable for everything?

Allow 45–60 minutes. Complete Lesson 5's basic lists, loops, and functions first.
Use `practice.py` in the lesson folder for experiments. Replace its contents with
each complete example, save, and run from the repository root:

```powershell
uv run python -m discoball.lesson_5.practice
```

## 1. Choose a structure that communicates intent

| Type | Starting model | Useful for |
| --- | --- | --- |
| `list` | Ordered, changeable collection | Files to process; accumulated results |
| `tuple` | Fixed sequence of references | A small positional result or composite key |
| `dict` | Unique keys mapped to values | Lookups, settings, or named record fields |

These are ordinary Python containers, not dataframe columns. A container can hold
other containers, but nested structures require care.

## 2. Change a list and retrieve its elements

```python
files = ["orders.csv", "products.csv"]
files.append("customers.csv")
print(files[0])
print(files[-1])
print(files[:2])
print("orders.csv" in files)
```

Expect the first filename, the last filename, a new list containing the first two,
and `True`. Positions start at zero; a negative position counts from the end. A
slice such as `[:2]` stops before position 2. `in` tests membership.

`append` changes the list in place and returns `None`. Do not write
`files = files.append(...)`: that replaces your variable with `None`.

**Your turn:** make that mistake deliberately, inspect `files`, then recreate the
original list. Explain the difference between an operation's effect and its return
value.

## 3. Understand shared references before copying

```python
files = ["orders.csv"]
also_files = files
also_files.append("products.csv")
print(files)
print(also_files is files)
```

Both names refer to the same list, so `files` now contains both filenames. `is`
tests object identity; `==` tests equality of values. Assignment did not copy the
list. Changing an existing object is **mutation**; assigning a different object to
a name is **rebinding**.

Compare:

```python
files = ["orders.csv"]
independent = files.copy()
independent.append("products.csv")
print(files)
print(independent)
```

The original list now stays unchanged. This is a **shallow copy**: it copies only
the outer container. Try the nested case:

```python
original = [["orders.csv"]]
copy = original.copy()
copy[0].append("products.csv")
print(original)
```

The inner list is still shared. Both outer containers refer to it. Do not reach
for deep copying automatically; often a simpler structure or explicit reconstruction
makes ownership clearer.

## 4. Use tuples for a fixed shape

```python
pair = ("A", "B")
category_a, category_b = pair
print(category_a)
print(category_b)
counts = {pair: 4}
print(counts[("A", "B")])
```

Unpacking assigns one element to each name. A tuple suits a small fixed positional
structure, but the positions need a clear meaning. `pair[0] = "C"` raises a
`TypeError`: you cannot replace an element of a tuple. A single-element tuple
needs a comma, such as `("A",)`; parentheses alone merely group an expression.

Immutability is not recursive. A tuple may contain a list, and that list can still
change. A tuple works as a dictionary key only if all its elements are hashable;
a tuple containing a list is not. Our pair of strings is suitable.

**Your turn:** try changing an element, then construct a new tuple with a different
value instead. Why is this different from mutating the original?

## 5. Use a dictionary for named lookups

```python
counts = {"A": 20, "B": 10}
counts["C"] = 3
counts["A"] = 21
print(counts["A"])
print(counts.get("D"))
print("B" in counts)
for category, count in counts.items():
    print(category, count)
```

Keys are unique. Assigning `counts["A"]` again replaces its value; it does not add
another A record. `in` checks keys, not values. `.items()` supplies key-value pairs
that the loop unpacks. Dictionaries preserve insertion order, but they do not sort
keys or values automatically.

`counts["D"]` raises `KeyError` for a missing key. `.get("D")` returns `None` by
default. `.get("D", 0)` supplies zero instead, which is appropriate only if missing
really means zero for this task. A convenient default must not hide missing data.

## 6. Pair iteration with positions or another sequence

```python
files = ["orders.csv", "products.csv"]
for position, filename in enumerate(files, start=1):
    print(position, filename)
```

`enumerate` supplies a counter and each value. Starting at 1 suits human-facing
labels; it does not change the list's zero-based indexes.

```python
names = ["A", "B"]
counts = [20, 10]
for name, count in zip(names, counts, strict=True):
    print(name, count)
```

`zip` pairs corresponding positions. Without `strict=True`, it stops at the
shortest input, potentially dropping unmatched values silently. Use strict mode
when mismatched lengths indicate a mistake.

**Your turn:** add another category name without a count. Observe the error, then
restore matching inputs. What would the non-strict version conceal?

## 7. Build a new container with a comprehension

Start with the explicit loop:

```python
counts = {"A": 20, "B": 10, "C": 3}
shortlist = []
for category, count in counts.items():
    if count >= 10:
        shortlist.append(category)
print(shortlist)
```

A list comprehension expresses that same construction:

```python
counts = {"A": 20, "B": 10, "C": 3}
shortlist = [category for category, count in counts.items() if count >= 10]
labels = {category: category.lower() for category in counts}
print(shortlist)
print(labels)
```

The dictionary comprehension maps each key to a value. Duplicate generated keys
would overwrite earlier entries; check that your transformation preserves identity.

Use comprehensions for short constructions of new collections, not for side effects
such as printing or writing files. Prefer a loop when conditions or error handling
need explanation. Shorter is not automatically clearer.

## Optional: traverse iterables with itertools

An **iterable** supplies values for iteration. Some iterable objects, including
many iterators, are consumed as you traverse them; they are not reusable lists.

- `chain(first, second)` traverses the first iterable, then the second.
- `islice(values, 5)` takes at most five values without first making a full list.
- `pairwise(values)` produces adjacent pairs: 10, 12, 9 becomes (10, 12), (12, 9).

`pairwise` does not produce all unordered basket-category combinations. Also,
`itertools.groupby` groups adjacent runs, not all equal values as SQL `GROUP BY`
does; it is not needed for this exercise.

Read and run [examples/containers.py](examples/containers.py):

```powershell
uv run python -m discoball.lesson_5.examples.containers
```

The example labels its counts as illustrative, not real source statistics.

## Finish with a choice

Describe which structure you would use for a sequence of files, a lookup of counts
by category, and an unordered category-pair key. Explain the ordering rule needed
to make A–B and B–A one key, and identify where shared mutable values could cause a
surprise.

Continue to [Text, bytes, and files](text_bytes_files.md), or return to
[Lesson 5](README.md).
