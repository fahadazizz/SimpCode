# Detailed Installation Guide

This guide covers systematic ways to install SimpCode across different environments and configurations.

---

## Method 1: Automated Script (Recommended)

Our `install.sh` script is designed for production-grade environments where you want `simp` to be available globally without polluting your system Python.

```bash
curl -sSL https://raw.githubusercontent.com/fahadazizz/simpcode/main/install.sh | bash
```

### What happens under the hood?
1.  **Discovery**: Finds an appropriate location for the binary (Default: `~/.local/share/simpcode`).
2.  **Clone**: Checks out the latest stable version of the source code.
3.  **Venv Creation**: Creates a dedicated virtual environment to isolate dependencies like `rich`, `click`, and `pydantic`.
4.  **Dependency Resolution**: Installs all required packages into the isolated environment.
5.  **Symlink**: Creates a pointer from your system `PATH` (e.g., `/usr/local/bin/simp`) to the executable in the virtual environment.

---

##  Method 2: Manual Developer Installation

If you intend to contribute to SimpCode or want total control over the installation path:

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/fahadazizz/simpcode.git
    cd simpcode
    ```

2.  **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install in Editable Mode**:
    This allows you to change the source code and see the impact immediately in the `simp` command.
    ```bash
    pip install -e .
    ```

---

## Method 3: Dockerized Environment

For environments where you cannot install Python locally, or for CI/CD pipelines.

1.  **Build the Image**:
    ```bash
    docker build -t simpcode:latest .
    ```

2.  **Run with Volume Mapping**:
    You must map your local repository into the container so SimpCode can see it.
    ```bash
    docker run -it -v $(pwd):/app -v ~/.simpcode:/root/.simpcode simpcode:latest chat
    ```

---

## Verifying Installation

To ensure everything is working correctly, check the version and help text:

```bash
simp --version
simp --help
```

### Troubleshooting
- **`command not found: simp`**: Your shell's `PATH` variable might not include the installation directory. Add `export PATH="$HOME/.local/bin:$PATH"` to your `.zshrc` or `.bashrc`.
- **`ModuleNotFoundError`**: Ensure you are not running `simp` from a shell that has a conflicting virtual environment active.
- **SSL Errors**: If using the curl script, ensure `ca-certificates` are up to date on your OS.
