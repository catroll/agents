# Setting `PYTHONPATH` in `os.environ` does not change the current `sys.path`

**Signal.** A wrapper builds an environment for its child processes, then
imports a sibling package in-process:

```python
env["PYTHONPATH"] = str(SERVICE_ROOT)
os.environ.update(env)
...
from config.loader import get_email_config   # ModuleNotFoundError: No module named 'config'
```

The child process launched with that `env` imports fine; the parent fails.

**Cause.** `sys.path` is derived from `PYTHONPATH` once, when the interpreter
starts. Assigning to `os.environ` afterwards changes what children inherit, not
the running process's import path.

**Check / fix.** Either insert the directory into the running process:

```python
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))
```

or start the interpreter with the variable already set (`PYTHONPATH=… python …`)
or re-exec. Do not add a second copy of the module elsewhere.

**Negative result.** `os.environ["PYTHONPATH"] = …` plus `importlib.invalidate_caches()`
does not help; the path entry is simply absent. Verify with
`python -c 'import sys; print(sys.path)'` in the same process before blaming the
package.

**Generalisable.** Environment variables that the interpreter consumes at
startup (`PYTHONPATH`, `PYTHONHOME`, locale) cannot be retrofitted into a live
process by mutating `os.environ`; only the child gets them.
