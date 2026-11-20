# Lesson 5 side quest: Try an idea with IPython

Sometimes you want to try one expression, inspect a value, or ask what a function
does without saving and running a whole script for every experiment.

IPython gives you an interactive Python session for that work. In this side quest,
you will use it to investigate small ideas, then save useful steps in a script.

Allow about 30–45 minutes. Work through Lesson 5's functions and imports first.
IPython is already included in the project environment; you do not need Jupyter,
a browser, or another VS Code extension.

## 1. Open an interactive session

In the VS Code terminal, from the repository root, run:

```powershell
uv sync
uv run ipython
```

After some startup text, you should see a prompt like:

```text
In [1]:
```

You are now inside IPython, not PowerShell. Enter Python at this prompt. Do not
enter the `uv run ...` commands from the lessons here; those belong in your shell.

The input number increases as you submit commands. Your numbers may differ from
the examples. Do not type the `In [...]` or `Out[...]` labels yourself.

## 2. Evaluate a small expression

Enter these lines one at a time, pressing Enter after each:

```python
basket_count = 100
pair_count = 4
pair_count / basket_count
```

IPython should display a result like:

```text
Out[3]: 0.04
```

Assignment gives a value a name but usually does not display it. An expression
entered on its own displays its result. In a normal script, you would use
`print(...)` to display that expression's value.

Try:

```python
support = pair_count / basket_count
support
print(f"Support: {support:.1%}")
```

The variable still contains a proportion. Formatting displays it as a percentage;
it does not change the stored value.

**Your turn:** predict the result of `100 * support`, then try it. Explain why
multiplying that result by 100 again would be a mistake.

## 3. Inspect values and discover help

You do not need to remember every available operation. Start by inspecting what
you already have:

```python
type(pair_count)
type(support)
```

You should see `int` and `float` as the respective types.

Now create a list:

```python
required_files = ["orders.csv", "order_items.csv", "products.csv"]
len(required_files)
```

Try these interactive tools:

- Type `required_f`, then press **Tab** to complete the name. If there are several
  possible matches, IPython may offer choices.
- Type `required_files.` and press **Tab** to explore available attributes and
  methods. Completion is a way to discover names, not a reason to call unfamiliar
  operations without checking what they do.
- Enter `len?` to view help for `len`. If help opens in a pager, press `q` to close
  it and return to the prompt.
- Press the **Up arrow** to retrieve earlier input. Edit it before pressing Enter
  if you want to try a variation.

The `?` help notation is an **IPython feature**, not ordinary Python syntax. Do not
copy `len?` into `practice.py`. In a script, ordinary Python's `help(len)` is an
alternative when you need help output.

**Your turn:** find out what `str.startswith` does. How does that relate to the
Git LFS check in Lesson 5?

## 4. Import a familiar operation

Enter:

```python
from discoball.const import OLIST_DIR
from discoball.lesson_5.inspect_inputs import describe_file

description = describe_file(OLIST_DIR / "orders.csv")
print(description)
```

You should see the filename, byte size, and header, as you did in the lesson.
Importing this function did not run the entire file-inspection workflow. You
chose when to call the function and which file to pass to it.

Now enter `description` on its own. IPython displays a representation of the
string, which may show quotes and `\n` characters. `print(description)` displays
its text with actual line breaks. These are two presentations of the same value.

Try `describe_file?` to inspect the function's signature and any available help.
The signature tells you the intended parameter and return types; type hints do not
validate the contents of the file for you.

**Your turn:** inspect `products.csv` using the same function. Save the returned
text under a different variable name. Can you still display the earlier result?

## 5. Notice what the session remembers

An interactive session retains variables and imports between inputs. That makes
experimentation convenient, but it can hide dependencies.

Enter this sequence, even if you already have variables with these names:

```python
basket_count = 100
pair_count = 4
support = pair_count / basket_count
pair_count = 8
support
```

The result is still `0.04`. Changing `pair_count` did not rerun the earlier
calculation. To update the result, execute the calculation again:

```python
support = pair_count / basket_count
support
```

Now the result is `0.08`.

This is one form of **hidden state**: a result depends on what happened earlier in
the session, not just the line you are currently looking at. A colleague—or you
tomorrow—may not have run the same earlier steps.

The session also retains imported code. Editing `inspect_inputs.py` on disk does
not automatically update a function you already imported. For now, exit and start
a fresh IPython session when you want to be sure you are using saved changes.
Re-enter the imports and inputs you need. You do not need to learn module reloading
to complete this lesson.

## 6. Recover and return to the terminal

If an operation is running and you need to interrupt it, press **Ctrl+C**. If a
partly entered command or completion is getting in your way, Ctrl+C will usually
cancel the current input. It does not undo earlier assignments or file changes.

A Python exception does not normally close IPython. Read the error, correct the
input, and try again. The session may still hold values from before the failure;
do not assume an error reset everything.

To leave IPython, enter:

```python
exit()
```

You should return to the PowerShell prompt. Starting IPython again creates a new
session: your previous variables are no longer defined. Command history may still
be available, but history is not the same as live variables.

**Your turn:** exit, start IPython again, and enter `support` without defining it.
Expect a `NameError`. Define the inputs and calculate it again, then exit.

## 7. Turn an experiment into a reproducible script

Open `src/discoball/lesson_5/practice.py`, the practice file you created in Lesson
5. Save a small complete workflow containing the imports, inputs, calculation,
and display steps you want to keep. For example:

```python
from discoball.const import OLIST_DIR
from discoball.lesson_5.inspect_inputs import describe_file

required_files = ["orders.csv", "products.csv"]
for name in required_files:
    print(describe_file(OLIST_DIR / name))
```

Save the file. After exiting IPython, run it from PowerShell:

```powershell
uv run python -m discoball.lesson_5.practice
```

This launches a fresh Python process. If the script works only because a variable
existed in your earlier IPython session, it is missing a step. Add that step to the
script rather than relying on your memory of the session.

Do not paste prompt labels, displayed results, or IPython-only help commands into
the file.

## What about Jupyter notebooks?

You may encounter Jupyter notebooks, which combine explanatory text, code, and
results in cells. They can be useful for narrative analysis, especially when you
want to discuss charts and intermediate findings alongside code.

They also use a persistent session, often called a **kernel**. Executing cells in
a different order can create the same hidden-state problems you just explored.
Notebook files, kernel selection, and sharing results introduce additional
workflow decisions.

For now, use scripts and IPython. You do not need to install or configure Jupyter
for this project sequence. If notebooks become useful for a specific deliverable,
they deserve a separate introduction rather than an extra setup hurdle here.

## Take the useful habit with you

You have completed the side quest when you can:

- Tell whether your terminal is at a shell prompt or an IPython prompt.
- Evaluate an expression and inspect its value and type.
- Find help without copying IPython-only syntax into a script.
- Explain why session state can make an experiment hard to reproduce.
- Move useful steps into a script that runs in a fresh process.

**Your interactive session helps you discover the steps. Your saved script should
contain the steps needed to reproduce the result.**

Return to [Lesson 5](README.md) or continue to
[Lesson 6](../lesson_6/README.md) when you are ready.
