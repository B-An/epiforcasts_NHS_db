# PyTensor / PyMC: C++ compiler (faster sampling)

## What the warning means

If you see:

```text
g++ not detected! PyTensor will be unable to compile C-implementations and will default to Python.
Performance may be severely degraded.
```

PyMC’s backend (**PyTensor**) is using **slow pure-Python** implementations because it cannot find a **C++ toolchain** (`g++` on MinGW-style installs, or MSVC `cl.exe` when using the Visual Studio toolchain).

**Fixing this is the main way to speed up** gradient evaluation and NUTS steps on CPU.

---

## Resolution A (recommended): Conda-forge compiler via Pixi

This project’s `pixi.toml` includes **`cxx-compiler`** from **conda-forge**, which installs a platform-appropriate toolchain (including **`g++`** on Windows via the MinGW stack).

1. **Install / refresh the environment**

   ```bash
   pixi install
   ```

2. **Run everything inside Pixi** so `PATH` includes the compiler:

   ```bash
   pixi shell
   python -c "import shutil; print('g++:', shutil.which('g++'))"
   pixi run run-dashboard
   ```

   Or without an interactive shell:

   ```bash
   pixi run streamlit run app.py
   ```

3. **Re-run your model** — the `g++` warning should disappear (or be reduced), and draws per second should improve.

**Trade-off:** The compiler packages add install size; they are optional for correctness but **strongly recommended** for performance.

---

## Resolution B (Windows): Microsoft C++ Build Tools

If you prefer the **MSVC** toolchain (or Pixi still does not see a compiler):

1. Install **[Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)** (free).
2. In the installer, select **“Desktop development with C++”** (includes MSVC, Windows SDK).
3. Open a **“x64 Native Tools Command Prompt”** or restart the terminal so `cl.exe` is on `PATH`, **or** use Pixi/conda as in Resolution A so PyTensor picks up `g++` from conda.

PyTensor generally works with **either** MinGW `g++` (from conda) **or** MSVC when configured correctly; the conda route is usually simpler for PyMC users.

---

## Resolution C (Linux / macOS)

- **Linux:** `sudo apt install build-essential` (Debian/Ubuntu) or your distro’s `gcc` / `g++` package, **or** rely on `pixi install` + `cxx-compiler`.
- **macOS:** `xcode-select --install` for Apple’s command-line tools, **or** `cxx-compiler` via Pixi.

---

## Verify

From the project directory, inside **`pixi shell`**:

```bash
python -c "import shutil; print('g++:', shutil.which('g++')); print('cl: ', shutil.which('cl'))"
```

You want at least one of `g++` or `cl` to be non-`None` before running PyMC.

Then run a short fit; the PyTensor warning about `g++` should not appear, and step times (e.g. `s/draw`) should drop versus the pure-Python fallback.

---

## If you must suppress the warning only (not recommended)

This **does not** restore speed — it only hides the message. Prefer installing a compiler (above).

---

## Assumptions and limits

- **Cloud / CI:** Use a Docker image or build agent image that includes `build-essential` (Linux) or MSVC + SDK (Windows), or install `cxx-compiler` in the same Pixi/conda env as PyMC.
- **Apple Silicon:** Use native arm64 Python and compilers; avoid Rosetta-only mixed toolchains for fewer surprises.
