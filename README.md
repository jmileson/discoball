# Discoball

A teaching project for analysts working with a supported data platform.

The goal is not to turn analysts into data engineers. It is to help them approach analytical problems effectively, recognize and communicate data issues, and collaborate with a data engineering platform team. Python and DuckDB provide a practical environment for developing those habits and extending analytical work within the platform's guardrails.

The project uses [uv](https://docs.astral.sh/uv/) to manage Python, dependencies, and a **project-local virtual environment** (`.venv`). This keeps this project's packages separate from other projects and your system Python.

## Setup: Windows + VS Code

These instructions use **PowerShell**, including the terminal built into VS Code. You do not need to install Python separately: uv can install the version this project needs.

### 1. Install the tools

- Install [Git for Windows](https://git-scm.com/downloads/win).
- Install [Git LFS](https://git-lfs.com/) if it is not already included with your Git installation. The CSV data in `olist/` is stored using Git LFS.
- Install [Visual Studio Code](https://code.visualstudio.com/).
- Install [DBeaver Community](https://dbeaver.io/download/), a desktop application for exploring databases and running SQL. Choose the installer for your operating system and follow your organization's approved installation process. You do not need the paid edition or a separate DuckDB server. The first DuckDB connection may need an internet connection to download its driver.
- Install uv by running the official installer in PowerShell:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  This downloads and runs the uv installer. If your organization restricts script execution or software installation, follow your IT team's approved installation process instead.

Close and reopen PowerShell (and VS Code if it was open) so the updated `PATH` takes effect. Check the installations:

```powershell
git --version
git lfs version
git lfs install
uv --version
```

### 2. Clone and open the project

Copy the repository's clone URL from its hosting page, then run the following, replacing `<repository-url>` with that URL:

```powershell
git clone <repository-url> discoball
cd discoball
git lfs pull
code .
```

If `code` is not recognized, open VS Code and use **File → Open Folder** to open the `discoball` folder instead. Open the project folder itself, not its parent or just an individual Python file.

Check that the data downloaded: in VS Code, open `olist/orders.csv`. You should see a comma-separated header followed by many rows of order records.

If the first line is `version https://git-lfs.github.com/spec/v1`, you have a Git LFS placeholder rather than the data. Make sure Git LFS is installed, then run these commands from the project folder:

```powershell
git lfs install
git lfs pull
```

Reopen `olist/orders.csv` and check again. If the file is still a placeholder or is missing, keep the error message and ask the project maintainer for help before continuing.

### 3. Create the local environment

In VS Code, choose **Terminal → New Terminal** and make sure the terminal is PowerShell and is in the `discoball` folder (the one containing `pyproject.toml`). If it opens a different shell, use the terminal dropdown → **Select Default Profile → PowerShell**, then open a new terminal. Run:

```powershell
uv sync
```

This command:

- Downloads the Python version specified in `.python-version`, if needed.
- Creates `.venv` inside the project folder.
- Installs the project and its dependencies from `uv.lock`, including development tools such as IPython.

The first run needs an internet connection and may take a little time. `.venv` is local to your machine and is ignored by Git; do not copy or commit it.

### 4. Tell VS Code which Python to use

1. Open **Extensions** (`Ctrl+Shift+X`) and install the recommended extensions: **Python** by Microsoft (`ms-python.python`), **Ruff** by Astral (`charliermarsh.ruff`), and **ty** by Astral (`astral-sh.ty`). Find them with the `@recommended` filter.
2. Open the Command Palette (`Ctrl+Shift+P`).
3. Run **Python: Select Interpreter**.
4. Select the interpreter inside this project's `.venv`. On Windows its path is:

   ```text
   .venv\Scripts\python.exe
   ```

   If it is not listed, choose **Enter interpreter path… → Find…** and select that file.

VS Code's Python run and debugging tools should now use the same environment as uv. If you open a different project, select that project's interpreter instead.

**Install extensions carefully:** check the exact IDs and publishers above, install only what you need, and keep them updated. See [Extension hygiene](#extension-hygiene) for more guidance.

### 5. Verify the setup

Run these commands in the project terminal:

```powershell
uv run python -c "import sys; print(sys.executable)"
uv run python -c "import duckdb; print(duckdb.sql('SELECT 42 AS answer').fetchall())"
uv run discoball
```

The first command should print a path inside this project's `.venv`. The second should print `[(42,)]`, and the last should print `Hello from discoball!`.

### 6. Load the Olist data

Run the setup script from the project terminal to load the CSV files in `olist/` into the local DuckDB database at `.data/dev.duckdb`:

```powershell
uv run setup
```

You should see the following row counts:

```text
customers: 99442 rows
orders: 99441 rows
order_items: 112650 rows
geolocation: 1000163 rows
order_payments: 103886 rows
order_reviews: 99224 rows
product_categories: 71 rows
products: 32951 rows
sellers: 3095 rows
```

If setup reports missing CSV files or cannot read the data, return to the `olist/orders.csv` check in [step 2](#2-clone-and-open-the-project), then retry `uv run setup`. If it names a different CSV, check that file for the same placeholder text. If the problem continues, share the error with the project maintainer.

The script creates tables only if they do not already exist. Running it again reports the existing row counts; it does not refresh or replace those tables.

**Setup is complete.** Start with Lesson 1 below. You do not need to finish reading the reference sections before beginning.

## Work through the lessons

Each lesson is a Markdown file named `README.md` in its own folder under `src/discoball/`. Open the links below, or find the file in VS Code and use **Open Preview** (`Ctrl+Shift+V`) to read it.

| Start here | What you will practice |
| --- | --- |
| [Lesson 1: Meet your data](src/discoball/lesson_1/README.md) | Connect DBeaver, explore the tables, and distinguish findings from assumptions. |
| [Lesson 2: What counts as bought together?](src/discoball/lesson_2/README.md) | Define a basket, join tables safely, and count category pairs without double-counting. |
| [Lesson 3: Common together, or unusually associated?](src/discoball/lesson_3/README.md) | Interpret support, confidence, and lift alongside the counts behind them. |
| [Lesson 4: Same customer, different question](src/discoball/lesson_4/README.md) | Compare basket affinity with customer-history affinity and recognize what each can answer. |
| [Lesson 4 side quest: From your query to a shared workflow](src/discoball/lesson_4/platform_side_quest.md) | Plan a dependable shared analysis and collaborate with data engineering. |

Read the lessons in order: later lessons build on the definitions and SQL from earlier ones. For each lesson:

1. Read the explanation, then run each SQL block in DBeaver against your local `.data/dev.duckdb` connection. Run PowerShell commands in the VS Code terminal, not the SQL editor.
2. Pause at **Your turn** and other questions. Save your queries as a SQL script and keep a short note of your results, assumptions, and unanswered questions.
3. Check what each result represents before moving on. A query running successfully is not the same as answering the intended question.

Lessons 2–4 use temporary views that exist only in the connection that created them. Keep using the same SQL editor session. If you disconnect, follow the lesson's instructions to recreate its dependencies before continuing.

These lessons use local DuckDB; you do not need a MotherDuck account. The side quest prepares you to discuss shared-platform work without requiring access to one yet.

## Reference guide

Return to these sections when you need them rather than reading them as additional lessons:

- [DuckDB SQL reference](src/discoball/sql_reference.md): query basics, SQL Server comparisons, project conventions, and common analytical pitfalls.

- [Everyday workflow](#everyday-workflow): commands for running Python and managing dependencies.
- [Formatting, linting, and type checking](#formatting-linting-and-type-checking): checks to use when you start changing Python code.
- [What's in the repository?](#whats-in-the-repository): where to find code, data, lessons, and configuration.
- [Extension hygiene](#extension-hygiene): guidance on installing and trusting editor extensions.
- [Troubleshooting](#troubleshooting): common setup problems.
- [macOS / Linux](#macos--linux): differences from the Windows setup.

## Everyday workflow

Open the project folder in VS Code and use its terminal. **You do not need to activate the environment** when using `uv run`: uv automatically uses the project's `.venv`.

| Task                                               | Command                           |
| -------------------------------------------------- | --------------------------------- |
| Install or sync dependencies after pulling changes | `uv sync`                         |
| Run the project's entry point                      | `uv run discoball`                |
| Run a Python file                                  | `uv run python path/to/script.py` |
| Start an interactive Python session                | `uv run python`                   |
| Start IPython (an enhanced interactive shell)      | `uv run ipython`                  |
| Add a project dependency                           | `uv add package-name`             |
| Add a development-only tool                        | `uv add --dev package-name`       |

uv uses `uv.lock` to keep dependency versions consistent and updates it when needed. When intentionally adding dependencies, use `uv add` and commit both `pyproject.toml` and `uv.lock` so everyone gets the same dependency versions. Avoid `pip install` for project dependencies: it does not record them in the project's configuration and lockfile. In CI, `uv sync --locked` can enforce that the lockfile is up to date.

## Formatting, linting, and type checking

Ruff formats Python code and checks for common mistakes. We use its default lint rules plus import sorting. ty checks types using its default rules, with no custom overrides. Both tools are development dependencies installed by `uv sync`.

Run these commands from the project folder:

```powershell
# Apply safe lint fixes, including import sorting.
uv run ruff check --fix .

# Format Python code.
uv run ruff format .

# Check types.
uv run ty check
```

Import sorting is a Ruff **lint fix**, not part of `ruff format`, so run both Ruff commands. Review changes before committing; some issues need manual edits.

To check your work without changing files:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run ty check
```

### In VS Code

The `.vscode/` folder contains recommended extensions and shared Python settings. With the Ruff and ty extensions installed, **explicitly saving a Python file** (`Ctrl+S`) formats it, organizes imports, and applies Ruff's safe lint fixes. These actions do not run on Auto Save. ty provides type diagnostics while you work.

Keep the project's `.venv` selected as your Python interpreter. This workspace selects Ruff as the Python formatter; the command-line checks above remain the shared reference regardless of editor.

## What's in the repository?

| Path              | Purpose                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| `src/discoball/`  | Python code and lesson folders. Start with the lesson links above; `__init__.py` contains the `discoball` entry point. |
| `olist/` | Source CSV data used by setup. |
| `.data/dev.duckdb` | Your local database, created by `uv run setup` and opened in DBeaver. |
| `pyproject.toml`  | Project metadata, supported Python versions, dependencies, and development tools.                         |
| `.python-version` | The Python version uv should use for this project.                                                        |
| `uv.lock`         | Exact dependency resolutions, committed so setups are reproducible.                                       |
| `.venv/`          | Your local Python environment, created by uv and not committed.                                           |
| `.envrc`          | Optional direnv integration for developers who already use it; not required for Windows or VS Code setup. |

## Extension hygiene

Treat extensions like installed software, not just editor themes or settings. Extensions can run code with your user account's permissions and may be able to read project files, access credentials, or make network requests. A Marketplace listing is not a guarantee of safety.

- **Install only what you need.** Start with the three extensions above. Review installed extensions periodically and uninstall ones you no longer use; fewer extensions means less code to trust and maintain.
- **Check the exact extension ID and publisher.** Use the IDs above rather than choosing a similar-looking name or icon. Follow links from the tool's official documentation when unsure. Download counts, reviews, and verified publisher badges are useful signals, not proof that an extension is safe.
- **Keep extensions and VS Code updated.** Updates can fix security vulnerabilities. On managed computers, follow your organization's approved update policy; don't disable updates indefinitely to avoid risk.
- **Pay attention to unusual changes.** Frequent releases alone do not mean an extension is unsafe, but an unexpected burst of updates, a publisher or ownership change, or new requests to sign in, run commands, or access services deserve a closer look. Check the changelog, official repository, and security notices before proceeding. Don't approve prompts you don't understand.
- **Remember that trusted extensions can be compromised.** A publisher's account or release process can be attacked, so a previously safe installation is not a permanent guarantee. If an extension is reported compromised, stop using it, disable or uninstall it, and follow your IT/security team's remediation guidance. Uninstalling alone may not undo exposure; credentials accessible during the affected period may need to be revoked or rotated.
- **Be deliberate about workspace trust.** Leave unfamiliar repositories in Restricted Mode until you have reviewed their source and configuration. Review recommendations in `.vscode/extensions.json` rather than installing them blindly. Workspace Trust reduces some risks, but it is not a sandbox or a substitute for choosing trustworthy extensions.

If an extension behaves unexpectedly—for example, asking you to paste a token or run an unexplained terminal command—pause and ask the project maintainer or IT before continuing.

## Troubleshooting

- **`uv` is not recognized:** restart VS Code and PowerShell after installing it. If it still fails, check the installer's instructions for adding uv to your `PATH`.
- **`ModuleNotFoundError` or imports are underlined in VS Code:** run `uv sync`, then select the project's `.venv` interpreter again. For terminal commands, use `uv run` rather than a system `python`.
- **PowerShell blocks automatic environment activation:** keep using `uv run`; activation is not required. You do not need to change your execution policy.
- **uv cannot find the project:** change into the folder containing `pyproject.toml` before running commands.
- **The lockfile is out of date:** make sure you have pulled both `pyproject.toml` and `uv.lock`. If you intentionally changed dependencies, run `uv lock` and commit the updated lockfile; otherwise ask the project maintainer rather than deleting it.
- **Downloads fail on a work network:** check proxy and certificate requirements with IT. Do not disable TLS verification to work around them.

## macOS / Linux

Install Git, [DBeaver Community](https://dbeaver.io/download/), VS Code (if desired), and uv using the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/). Then clone the repository and run the same `uv sync` and `uv run ...` commands above.

For VS Code, select `.venv/bin/python` instead of the Windows path. Neither environment activation, direnv, nor a particular editor is required.
