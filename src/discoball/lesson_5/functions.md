# Side quest 4: Functions with clear inputs

A reusable check needs more than a name. Its caller needs to know what inputs it
accepts, what it returns, and what it might change or reject.

Allow 60–90 minutes. Complete [Numbers and calculations](numbers.md) first. Use
`practice.py` for the small examples. The full worked example is
[examples/functions.py](examples/functions.py).

## 1. Separate parameters from arguments

```python
def passes_threshold(pair_baskets, minimum):
    return pair_baskets >= minimum


print(passes_threshold(12, 10))
print(passes_threshold(pair_baskets=12, minimum=20))
```

`pair_baskets` and `minimum` are parameters in the definition. The supplied values
are arguments in a call. Positional arguments match by position; keyword arguments
match by name. The examples return `True` and `False`.

Keyword arguments make two otherwise anonymous numbers easier to interpret. Once
you supply a keyword argument, you cannot follow it with an ordinary positional
argument. Supplying the same parameter twice is also an error.

**Your turn:** deliberately call the function with a misspelled keyword. Read the
`TypeError`, then correct it. Why is silently ignoring an unknown setting risky?

## 2. Give defaults intentionally

```python
def passes_threshold(pair_baskets, *, minimum=10):
    return pair_baskets >= minimum


print(passes_threshold(12))
print(passes_threshold(12, minimum=20))
```

The default allows the caller to omit `minimum`. The bare `*` makes following
parameters keyword-only: `passes_threshold(12, 20)` now fails. This can improve
readability for options whose meaning is not obvious from a number alone.

A default is still a choice, not an agreed business definition. Document why the
threshold exists and let the analytical workflow state the choice explicitly when
it matters.

## 3. Return useful values and make failures visible

A function can return a value, mutate an object, perform a side effect such as
writing a file, or do a combination. Make those behaviors clear.

```python
def population_summary(pair_baskets, population):
    if population <= 0:
        raise ValueError("Population must be positive.")
    return pair_baskets, pair_baskets / population


count, rate = population_summary(4, 100)
print(count, rate)
```

Returning two comma-separated values creates a tuple, which the caller unpacks.
A returned result is not automatically printed. A function that reaches its end
without a return value returns `None`.

The example rejects a non-positive denominator but does not check every possible
invalid input. Decide the contract you need. Return an empty collection when “no
qualifying records” is a legitimate result; raise an error when a required
assumption fails. Those are not interchangeable cases.

Parameters are local names, but their objects may be shared with the caller. If
you append to a passed list, the caller sees that mutation. Type hints do not
prevent it. Revisit [Containers](containers.md#3-understand-shared-references-before-copying)
if that distinction is unclear.

## 4. Avoid shared mutable defaults

This function has a trap. Run the whole example once in a fresh practice process:

```python
def add_note(note, notes=[]):
    notes.append(note)
    return notes


print(add_note("Check coverage"))
print(add_note("Check categories"))
```

The second output contains both notes. The default list was created **once when
the definition executed**, not freshly on every call. Both omitted-argument calls
used that same list.

A safer pattern for this meaning is:

```python
def add_note(note, notes=None):
    if notes is None:
        notes = []
    notes.append(note)
    return notes


print(add_note("Check coverage"))
print(add_note("Check categories"))
```

Now each omitted argument gets a fresh list created inside its call. `None` means
“no list supplied” here. Use `is None`, not `if not notes`: an explicitly supplied
empty list is a valid list that the caller may expect to receive the note.

If a caller supplies an existing list, this function **still mutates it**. If you
promise not to modify caller-owned data, make a copy or return a new list instead.
`None` solves the shared-default problem, not every ownership problem.

**Your turn:** pass one explicit list into two calls. Predict its contents, then
check them. Explain why that sharing is different from an accidental default.

Defaults are evaluated at definition time even when immutable: a current timestamp
used as a default would not update itself on every call. Use a deliberate pattern
for values that need to be computed per invocation. If `None` is itself a meaningful
explicit input, a separate sentinel may be needed; that is beyond this exercise.

## 5. Recognize *args and **kwargs

```python
def format_notes(*notes, separator="; "):
    return separator.join(notes)


def describe_settings(**settings):
    return ", ".join(f"{key}={value}" for key, value in settings.items())


print(format_notes("Historical data", "Check coverage", separator=" | "))
print(describe_settings(minimum=10, category_minimum=50))
```

In a definition:

- `*notes` collects extra positional arguments into a tuple.
- `**settings` collects extra keyword arguments into a dictionary.

`args` and `kwargs` are conventional names, not required names. The star notation
is what determines the behavior.

These patterns are useful for genuinely variable inputs and forwarding calls.
Prefer explicit parameters when a function has a small known set of settings:
accepting arbitrary keywords can hide misspellings and weaken editor assistance.

## 6. Unpack collections into a call

The same stars work in the other direction at the call site:

```python
def passes_threshold(pair_baskets, *, minimum=10):
    return pair_baskets >= minimum


def format_notes(*notes):
    return "; ".join(notes)


messages = ["Historical data", "Not a causal estimate"]
options = {"minimum": 20}
print(format_notes(*messages))
print(passes_threshold(12, **options))
```

`*messages` supplies its elements as separate positional arguments. `**options`
supplies entries as named arguments; keys must be strings and must fit the called
function's signature unless it accepts arbitrary keywords.

**Your turn:** change the option key to `minumum`. Confirm that the explicit
function catches the mistake. Why would an unrestricted `**settings` function not
necessarily catch it?

## Optional: configure and select with small helpers

Run the worked example:

```powershell
uv run python -m discoball.lesson_5.examples.functions
```

`functools.partial(passes_threshold, minimum=20)` produces another callable with
an argument pre-filled. It does not execute the check yet. The default configured
value can still be overridden at call time; it is convenience, not a policy lock.

`sorted(rows, key=itemgetter("count"), reverse=True)` uses `operator.itemgetter`
to obtain a dictionary value for sorting. `operator.attrgetter` does the same for
object attributes; you will encounter those in the next side quest. The module
name is `operator`, singular.

A **callable** is something you can call with parentheses, including a function.
Passing `itemgetter("count")` as `key` supplies an operation for `sorted` to call
on each element. You are not supplying a precomputed count for the whole list.

These are conveniences, not requirements. A short named function is often clearer
than clever functional code. Decorators, caching, and `reduce` are not needed here.

## Finish with a function contract

Pick one check from the earlier lessons and specify:

- Inputs, types, and any units.
- Defaults and why they are appropriate.
- Return value and legitimate empty results.
- Errors for invalid assumptions.
- Whether it changes an object passed by the caller.

Implement a small function and test a normal case, an edge case, and an invalid
case. Keep the test inputs explicit so you can explain the expected result.

Continue to [Objects: data and behavior](objects.md), or return to
[Lesson 5](README.md).
