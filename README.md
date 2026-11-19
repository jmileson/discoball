# Discoball

A teaching project for analysts learning DuckDB, Python, and how to approach problems from a data engineering perspective.

The project uses [uv](https://docs.astral.sh/uv/) to manage Python, dependencies, and a **project-local virtual environment** (`.venv`). This keeps this project's packages separate from other projects and your system Python.

## Setup: Windows + VS Code

These instructions use **PowerShell**, including the terminal built into VS Code. You do not need to install Python separately: uv can install the version this project needs.

### 1. Install the tools

- Install [Git for Windows](https://git-scm.com/downloads/win).
- Install [Visual Studio Code](https://code.visualstudio.com/).
- Install uv by running the official installer in PowerShell:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  This downloads and runs the uv installer. If your organization restricts script execution or software installation, follow your IT team's approved installation process instead.

Close and reopen PowerShell (and VS Code if it was open) so the updated `PATH` takes effect. Check the installations:

```powershell
git --version
uv --version
```

### 2. Clone and open the project

Copy the repository's clone URL from its hosting page, then run the following, replacing `<repository-url>` with that URL:

```powershell
git clone <repository-url> discoball
cd discoball
code .
```

If `code` is not recognized, open VS Code and use **File → Open Folder** to open the `discoball` folder instead. Open the project folder itself, not its parent or just an individual Python file.

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

**Setup is complete.** The sections below are reference material; you don't need to work through them now.

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
| `src/discoball/`  | The project's Python code. `__init__.py` currently contains the `discoball` entry point.                  |
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

Install Git, VS Code (if desired), and uv using the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/). Then clone the repository and run the same `uv sync` and `uv run ...` commands above.

For VS Code, select `.venv/bin/python` instead of the Windows path. Neither environment activation, direnv, nor a particular editor is required.
