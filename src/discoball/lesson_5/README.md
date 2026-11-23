# Lesson 5: Your first analyst workflow in Python

So far, you have asked a database questions using SQL. Now you will start learning
Python: a language you can use to organize work, inspect files, run checks, and
connect tools together.

You do not need to replace your SQL knowledge. You are adding another tool. Before
using it for a whole analysis, you will practice a few basic programming ideas.

We are deliberately keeping the business question while changing tools. In Lessons
6 and 7, you will work directly with the familiar files and rebuild basket affinity
with Polars. In Lesson 8, Python will also run saved SQL and compare the results.
That gives you options for exploring and prototyping when a platform does not yet
provide what you need—not a requirement to move every analysis out of SQL.

This lesson takes a smaller step: write, run, understand, and modify a program that
inspects the inputs. File inspection does not answer the cross-sell question; it gives
you a manageable workflow in which to learn the programming skills the rebuild needs.

As a working estimate, allow two or three sessions of about 45–60 minutes, with
breaks at the checkpoints. Taking more sessions is normal when programming is new.
Complete [Lesson 4](../lesson_4/README.md) first. No previous programming experience
is required. You will not modify the database or need MotherDuck access.

By the end, you will be able to:

- Save and run a small Python program.
- Explain values, variables, types, and expressions.
- Make a decision with `if` and repeat work with `for`.
- Define and call a function.
- Use an imported tool to inspect a file.
- Read an error message and make a small correction.

## Part A: Write and run small programs

### 1. Know which tool receives your instructions

You now have several places where you can type. They do different jobs:

| Place | What belongs there | Example |
| --- | --- | --- |
| DBeaver SQL editor | SQL for the database | `SELECT count(*) FROM orders;` |
| VS Code Python file | Python source code you save | `print("Hello")` |
| VS Code terminal (PowerShell) | Commands that launch programs | `uv run python ...` |

A **program** or **script** is a saved sequence of instructions. A Python file uses
`.py` as its filename extension. Saving the file does not run it; running it does
not automatically save unsaved changes.

Open the project folder in VS Code. Open **Terminal → New Terminal** and check that
you are in the folder containing `pyproject.toml`. Run:

```powershell
uv sync
uv run python -c "print('Hello from Python')"
```

The terminal command launches Python through the project's environment. `-c` means
“execute the following text as Python.” You should see:

```text
Hello from Python
```

You do not need to activate `.venv` separately when using `uv run`.

### 2. Save your own practice file

In VS Code's file explorer, open `src/discoball/lesson_5/` and create a file named
`practice.py` alongside this lesson's `README.md` and `inspect_inputs.py`. This is
your practice file; it is fine to add it to the lesson folder. You do not need to
commit or push your work to complete the lesson. Keep credentials and private data
out of your code.

Type these two lines into that file:

```python
print("Starting my first script")
print("I can run Python from this project")
```

Save it with `Ctrl+S`. From the repository root, run:

```powershell
uv run python -m discoball.lesson_5.practice
```

Both messages should appear in the terminal in the order you wrote them.

`print` is a **function**: a named operation. Parentheses call it, and the text
between the quotes is the input you pass to it, called an **argument**. The quote
marks delimit the string; they are not printed as part of the message.

**Your turn:** add a third message, save, and run again. Then change the first
message. Which messages appear when you run the whole file again?

For the practice sections below, replace the contents of this same practice file
with each complete example unless told otherwise. Save and run it with the same
terminal command. Do not paste the Markdown fence markers into the file.

### 3. Follow execution from top to bottom

Python normally executes the statements in a script in order. Later, conditions,
loops, and function calls will let you control which instructions run.

```python
print("First")
print("Second")
print("Third")
```

Predict the output before running it. This habit—**predict, run, compare**—helps
you understand code rather than just copy it.

Blank lines make code easier to read. A `#` starts a comment that continues to the
end of the line:

```python
# Explain why a decision was made, not just what the next line says.
print("Inspect inputs before starting the analysis")
```

Python comments use `#`, not SQL's `--`. You generally do not need semicolons at
the end of Python statements.

### 4. Give values names with variables

Replace your practice file with:

```python
basket_count = 100
pair_count = 4
support = pair_count / basket_count

print(basket_count)
print(pair_count)
print(support)
```

A **value** is a piece of data such as `100`. A **variable** is a name referring to
a value. Assignment uses `=`. Python evaluates the expression on the right and
assigns its result to the name on the left.

`pair_count / basket_count` is an **expression**: something Python evaluates to
produce a value. Here, `/` performs division, producing `0.04`.

Assignment is not an equation that keeps updating itself. Try:

```python
basket_count = 100
pair_count = 4
support = pair_count / basket_count
pair_count = 8

print(support)
```

The output is still `0.04`. You changed `pair_count`, but you did not execute the
support calculation again. Add `support = pair_count / basket_count` after the
change and rerun. Now the result is `0.08`.

**Your turn:** explain why this differs from an Excel formula that recalculates
when a referenced cell changes. What happens if you move the support calculation
above the line that first defines `pair_count`?

Variables must exist before you use them. Python is case-sensitive: `pair_count`
and `Pair_Count` are different names. Use descriptive lower_snake_case names,
without spaces, and avoid using function names such as `print` for your variables.

### 5. Recognize types before combining values

Different kinds of values have different behavior:

| Type | Example | Meaning |
| --- | --- | --- |
| `str` | `"delivered"` | Text, also called a string |
| `int` | `100` | Whole number |
| `float` | `0.04` | Floating-point number |
| `bool` | `True` | A true/false value |
| `NoneType` | `None` | A value commonly used to represent absence |

Inspect types with the built-in `type` function:

```python
count = 100
count_as_text = "100"
print(type(count))
print(type(count_as_text))
print(count + 20)
print(count_as_text + "20")
```

The last two results are `120` and `10020`. Adding numbers performs arithmetic;
adding strings concatenates their text. A number inside quotes is still text.

Try `print(count_as_text + 20)`. Python raises a `TypeError` rather than guessing
whether you want arithmetic or text concatenation. You can explicitly convert
valid numeric text with `int(count_as_text)`. Conversion can fail too:
`int("delivered")` is not meaningful.

Single and double quotes both delimit Python strings. Unlike SQL, double quotes
do not identify column names here. `True`, `False`, and `None` have capitals and
are not quoted.

**Your turn:** calculate `100 * support` and label it as a percentage. Do not change
the stored support to a percentage and then multiply it again later.

Python floats can contain small approximation errors, much like floating-point
calculations in SQL. We will compare computed rates with a tolerance later rather
than assume every decimal is represented exactly.

### 6. Make output readable

Instead of printing numbers with no context, use a formatted string:

```python
basket_count = 100
pair_count = 4
support = pair_count / basket_count

print(f"Unformatted baskets: {basket_count}")
print(f"Eligible baskets: {basket_count:,}")
print(f"Pair support: {support:.1%}")
```

The `f` before the opening quote allows expressions inside `{...}`. `:,` adds
thousands separators. `:.1%` displays a proportion as a percentage with one decimal
place. These change the displayed text, not the underlying variable.

Expect `Eligible baskets: 100` and `Pair support: 4.0%`.

**Checkpoint:** take a break if useful. Before continuing, confirm that you can
save and rerun the file, explain assignment, and distinguish a number from numeric
text. Do not worry about memorizing every formatting symbol.

## Part B: Decisions, repetition, and reusable steps

### 7. Compare values and choose what happens

SQL uses `=` for equality. Python uses `==`. Assignment and comparison are
different operations:

```python
pair_count = 4
pair_count_is_four = pair_count == 4
print(pair_count_is_four)

passes_count_cutoff = pair_count >= 10
print(passes_count_cutoff)

if passes_count_cutoff:
    print("Passes this illustrative count cutoff")
else:
    print("Too few shared baskets for this shortlist")

print("The check has finished")
```

`>=` means “greater than or equal to.” The comparison produces a boolean. `if`
runs its indented block when the condition is true; `else` supplies an alternative.
The final unindented line runs after either branch.

Python uses indentation to define blocks. The colon introduces the block; the
following lines use four spaces. Use spaces consistently and let VS Code help.
This is syntax, not just the formatting preference it was in SQL.

**Your turn:** predict the output for counts of 4, 10, and 20, then test each one.
Why is “passes the cutoff” not the same as “a commercially useful pairing”?

Common comparisons include `==`, `!=`, `<`, `<=`, `>`, and `>=`. For ordinary
scalar booleans, combine conditions with `and`, `or`, and `not`; use parentheses to
make grouping clear. Polars column expressions will use a different notation in
Lesson 6.

### 8. Keep several values in a list

```python
required_files = ["orders.csv", "order_items.csv", "products.csv"]
print(required_files)
print(len(required_files))
print(required_files[0])
```

A **list** stores an ordered collection. Square brackets create the list; commas
separate its elements. `len(...)` returns its length. Indexing with `[0]` retrieves
the first element: Python positions begin at zero.

For this list, valid non-negative positions are 0, 1, and 2. Position 3 raises an
`IndexError`. A list is a Python collection, not a database table or dataframe.

**Your turn:** add `customers.csv`, then predict the length and the value at
position 3. How would you change the order in which files are listed?

### 9. Repeat a step with a loop

Replace the file with:

```python
required_files = ["orders.csv", "order_items.csv", "products.csv"]

for name in required_files:
    print(f"Need to inspect: {name}")

print("Finished listing inputs")
```

A **loop** repeats a block. On each iteration, Python assigns the next element to
`name`, then executes the indented body. The name `name` is your choice, not a
special keyword; `for` and `in` are Python keywords.

Trace it:

| Iteration | Value assigned to `name` | What gets printed |
| --- | --- | --- |
| 1 | `"orders.csv"` | Need to inspect: orders.csv |
| 2 | `"order_items.csv"` | Need to inspect: order_items.csv |
| 3 | `"products.csv"` | Need to inspect: products.csv |

The final message is outside the loop and prints once. If it were indented into
the loop, it would print three times. If the list were empty, the loop body would
not run, but the final message would still appear.

**Your turn:** test those two changes separately. Restore the three-element list
and the original indentation afterward.

We are looping over a handful of files, not over every record in those files.
Later, Polars will handle tabular operations without a Python loop for each row.

### 10. Give a reusable operation a function name

You have called built-in functions such as `print` and `len`. You can define your
own:

```python
def describe_count(label, count):
    return f"{label}: {count:,}"


message = describe_count("Eligible baskets", 100)
print(message)
print(describe_count("Shared baskets", 4))
```

`def` defines the function. The indented body is saved as an operation; it does
not execute just because Python reaches the definition. Parentheses after its
name **call** the function.

`label` and `count` are **parameters**: names for the inputs inside the function.
`"Eligible baskets"` and `100` are **arguments**: the actual values passed by the
caller. Parameter names are local to that call; they do not automatically create
variables with those names elsewhere in your program.

`return` ends the call and supplies a result. The first call returns text, which
is assigned to `message`. `print(message)` displays it.

**Return and print are different.** If this function printed its message instead
of returning it, the caller would receive `None` unless it had another explicit
return. Returning a value lets later code display it, save it, or test it.

**Your turn:** add another call for a different count without copying the function
body. Then explain the difference between `describe_count` and
`describe_count("Shared baskets", 4)`.

The supplied workflow uses type hints, such as `path: Path` and `-> str`. They
document intended inputs and outputs and help the editor check your code. They
do not automatically convert or enforce values at runtime.

**Checkpoint:** explain how a loop and a function differ. A loop repeats work;
a function names reusable work. You can call a function inside a loop.

## Part C: Inspect real project inputs

### 11. Import tools instead of writing everything yourself

Now replace your practice file with:

```python
from discoball.const import OLIST_DIR

input_path = OLIST_DIR / "orders.csv"
print(input_path)
print(input_path.name)
print(input_path.is_file())
```

An **import** makes a name available from another module. A module is a unit of
Python code, often a `.py` file. Here you reuse the project's existing path
configuration instead of embedding a particular student's username.

`OLIST_DIR` is a `Path` object: a value with operations for filesystem paths. Its
uppercase name signals a project constant by convention; Python does not make it
immutable merely because it is capitalized.

The `/` operator joins a `Path` and a filename here. Its behavior differs from
numerical division because the values have different types. `.name` accesses an
attribute. `.is_file()` calls a **method**, a function associated with the object,
and returns a boolean.

An import does not install a package. `uv sync` installs the project's recorded
dependencies; imports make their names available to a running script. `pathlib`,
which supplies `Path`, comes with Python's standard library.

### 12. Open and close a file deliberately

Extend the practice file so it contains:

```python
from discoball.const import OLIST_DIR

input_path = OLIST_DIR / "orders.csv"

with open(input_path) as source:
    header = source.readline().strip()

print(header)
```

`open` opens the file for reading in this example. `with` manages its lifetime,
closing it when the block ends, including if an error occurs. `source` names the
open file while you use it.

`readline()` reads one line. `.strip()` removes leading and trailing whitespace,
including its final newline. This does not parse the CSV into a table; it reads
text. Do not build a CSV parser by splitting every line on commas: quoted values
can contain commas. You will use Polars to read tabular data in the next lesson.

**Your turn:** explain why seeing a plausible header does not prove that every
row in the file is valid. What is useful about checking the header anyway?

### 13. Read the supplied workflow in small pieces

Open [inspect_inputs.py](inspect_inputs.py). Do not replace it with your practice
examples. Run the supplied module from the repository root:

```powershell
uv run python -m discoball.lesson_5.inspect_inputs
```

As with your practice file, `-m` runs this module by its package name. The dots
follow the folders under `src`: `discoball`, then `lesson_5`, then the filename
without `.py`. Run these commands from the repository root so the instructions
stay consistent.

You should see filenames, byte sizes, and CSV headers for `orders.csv`,
`order_items.csv`, and `products.csv`. No source files are changed. File sizes
may vary with line endings; a size is not a row-count validation.

Find these pieces:

| Code | Role |
| --- | --- |
| `def describe_file(path: Path) -> str:` | Define one file-inspection operation. |
| `if not path.is_file():` | Check for a missing file before trying to open it. |
| `raise FileNotFoundError(...)` | Stop with an explicit explanation. |
| `with open(path) as source:` | Read using a managed file handle. |
| `header.startswith(...)` | Detect the text identifying a Git LFS placeholder. |
| `path.stat().st_size` | Ask the filesystem for the file size in bytes. |
| `return f"..."` | Return a description; `\n` inserts a line break. |
| `def main() -> None:` | Organize the overall workflow; no useful return value is promised. |
| `for name in required_files:` | Call the inspection operation for each requested file. |

Follow the execution of one call to `describe_file`. It either returns a string
or stops with an exception. Then follow the loop across all three files.

At the bottom you will find:

```python
if __name__ == "__main__":
    main()
```

This is a standard entry-point pattern. Running the module calls `main()`;
importing its functions from elsewhere does not automatically run the workflow.
You can recognize and use this pattern without needing to memorize Python's
module machinery today.

### 14. Read errors as information

A **traceback** reports where an unhandled exception occurred and the calls that
led to it. An error is not evidence that you are unsuited to programming. It is
information about what the program could not do.

Try the following controlled experiment in your practice file:

```python
from discoball.const import OLIST_DIR
from discoball.lesson_5.inspect_inputs import describe_file

print(describe_file(OLIST_DIR / "not_a_real_input.csv"))
print("Finished successfully")
```

Expect a `FileNotFoundError` naming the missing input. The final print does not
run: an unhandled exception stops normal execution.

Read the last line of the traceback first. Then locate your script and relevant
line number above it. Absolute paths and line numbers vary between machines.
Change the filename to `orders.csv`, save, and rerun successfully. Do not delete
real files to test error handling.

| Error | A first thing to check |
| --- | --- |
| `SyntaxError` | Quotes, parentheses, commas, or a missing colon. The actual mistake may be just before the reported location. |
| `IndentationError` | Block indentation and accidental mixtures of tabs and spaces. |
| `NameError` | Spelling, case, and whether a variable was assigned before use. |
| `TypeError` | Whether the operation makes sense for the supplied types. |
| `FileNotFoundError` | The full requested path and the input-download/setup steps. |
| `ModuleNotFoundError` | The import spelling, project environment, and whether you ran through `uv run`. |

> **Watch out — a failed workflow must not look successful**
>
> Suppressing every exception and printing “done” can hide missing inputs or failed
> calculations. Read the error, correct the cause, and rerun. Later workflows will
> rely on visible failures to distinguish an invalid run from a valid empty result.

## Part D: Make a small change and explain it

### 15. Extend the workflow without changing its purpose

In the supplied script, add `customers.csv` to `required_files`. Predict what
changes, save, and run the module again. Confirm that all four files appear.

Then temporarily add `not_a_real_input.csv`. Run it, identify the exception and
its cause, and remove that entry. Finish with a successful run. No database or
source CSV changes are needed.

Use explicit save in VS Code. The project's formatter can help keep Python
readable. From the terminal, check the shared lesson code with:

```powershell
uv run ruff check src/discoball/lesson_5
uv run ruff format --check src/discoball/lesson_5
```

These checks include your `practice.py` file because it is in the lesson folder.
If they report an issue there, use the filename and line number to find it.
Formatting and linting are useful feedback, not proof that a program answers the
right analytical question.

### 16. Record how the workflow works

Add an implementation section to your existing investigation record. Keep the earlier
business findings; this section explains how you are making the work reproducible.
Record:

```text
What the script is for:
How to run it, and from which folder:
Inputs it expects:
What the output tells us:
Checks it performs:
What those checks do not establish:
How a missing input is reported:
The change I made and how I checked it:
```

> **Interpretation limit — an input check is not a data-quality verdict**
>
> A file existing and not being an LFS placeholder does not prove that it contains
> valid rows, complete history, or suitable data for a business decision. In your
> record, distinguish what the script checked from what remains to be checked.

You have completed the lesson when you can explain the workflow without reading
it aloud line by line: where its inputs come from, why it repeats a function call,
what it returns, what it displays, and when it stops.

**What you can do now:** save and rerun a program, reuse an operation across files,
make a controlled change, and use an error message to investigate a failure. Those
skills let you move beyond executing supplied scripts towards adapting workflows
for your own questions.

For an optional way to explore these ideas interactively, take the
[IPython side quest](ipython_side_quest.md). You will try expressions, inspect
values, and learn why useful experiments still need to become reproducible scripts.
No Jupyter setup is required.

### Optional Python foundations track

For a deeper introduction, follow these side quests in order, or return to them
when a later workflow raises a question. They are not prerequisites for completing
Lesson 6. Allow roughly 45–90 minutes each; split them into separate sessions.

| Side quest | What you will practice |
| --- | --- |
| [1. Containers](containers.md) | Lists, tuples, dictionaries, shared references, iteration, and comprehensions |
| [2. Text, bytes, and files](text_bytes_files.md) | Text manipulation, encodings, safe file handling, CSV, and JSON |
| [3. Numbers and calculations](numbers.md) | Arithmetic, units, approximate comparisons, Decimal, and explicit scenarios |
| [4. Functions with clear inputs](functions.md) | Arguments, defaults, mutation, unpacking, and small callable helpers |
| [5. Objects: data and behavior](objects.md) | Dataclasses, named tuples, typed dictionaries, and validated records |

Each includes a worked module under `lesson_5/examples/`. Run the module command
shown in the side quest from the repository root. File-writing examples create
only synthetic files under `lesson_5/outputs/`, which is ignored by Git. Reruns
replace the named generated files; source Olist files are never overwritten.

Keep your practice file for future experiments. Continue to
[Lesson 6](../lesson_6/README.md) when you are comfortable predicting and explaining
these small programs. You will apply the same habits to tabular data with Polars.
