# Investigation: Ollama Connectivity Issue

## Status
- **Issue**: Aria website shows Ollama as "offline".
- **Findings**:
    - `curl http://192.168.1.106:11434/api/tags` **SUCCESS**. Ollama is up and reachable.
    - `curl http://localhost:8000/api/status/ollama` **FAILED** (returns "offline").
    - **Code Bug**: `src/api/main.py` uses `f"http://{OLLAMA_URL}"` in `SERVICE_URLS` default value, but `OLLAMA_URL` is not defined in the local scope. This should raise `NameError`.
    - **API Behavior**: The API swallows exceptions during status checks, masking the real error (which is likely the `NameError` re-occurring or a connection error if the variable *is* inexplicably defined).

## Plan
1.  **Fix `src/api/main.py`**:
    - Properly initialize `OLLAMA_URL` from `os.getenv`.
    - Fix the `SERVICE_URLS` definition.
    - Add error logging to `/status` endpoint to print exceptions to stdout.
2.  **Restart API**:
    - `docker restart aria-api`.
3.  **Verify**:
    - Check `/status/ollama` again.

## Technical Details
### Current Broken Code
```python
"ollama": (os.getenv("OLLAMA_URL", f"http://{OLLAMA_URL}"), "/api/tags"),
```
`OLLAMA_URL` (variable) is undefined in recent context.

### Proposed Fix
```python
OLLAMA_URL_DEFAULT = "http://host.docker.internal:11434"
OLLAMA_URL = os.getenv("OLLAMA_URL", OLLAMA_URL_DEFAULT)

SERVICE_URLS = {
    ...
    "ollama": (OLLAMA_URL, "/api/tags"),
    ...
}
```
