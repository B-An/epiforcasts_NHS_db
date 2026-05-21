# Object-Oriented Design Analysis: NHS Pressure Model

> Applying the book's exercise to reflect on this real project's architecture

## Part 1: Understanding the Prominent Objects

### The Most Important Object: **CacheManager**

If I were to identify the "most prominent object" in this design, it's **`CacheManager`**. Here's why:

```python
class CacheManager:
    """Manages cached posteriors and summary statistics."""
    
    def __init__(self, posteriors_path, cache_dir, ttl_hours):
        self.posteriors_path = Path(posteriors_path)
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.summary_stats_path = self.cache_dir / "summary_stats.json"
        self.icb_samples_path = self.cache_dir / "icb_samples"
        self.health_check_path = self.cache_dir / "health_check.json"
```

**Why is this the dominant object?**

It acts as a **gatekeeper** and **orchestrator** for the entire system. Almost every other component depends on it or interacts with it:
- The inference daemon writes to it
- Both UIs read exclusively from it
- It validates whether the system is ready to serve

---

## Part 2: CacheManager's Attributes

Let me identify what attributes this object has:

### Primitive Attributes (Basic Types)
- **`ttl_hours`** (int) — Time-to-live threshold for staleness warnings
- **Derived paths** (Path objects, which are also primitives):
  - `posteriors_path` — NetCDF file with Bayesian posteriors
  - `summary_stats_path` — Pre-computed JSON statistics
  - `icb_samples_path` — Directory of individual ICB sample arrays (NPY files)
  - `health_check_path` — JSON metadata about cache state

### What Do These Attributes Represent?

Looking deeper, some of these attributes are **not** just data—they encode **state information**:

```python
# These are really "is it working?" questions in disguise:
self.posteriors_path.exists()        # Does the posterior exist?
self.summary_stats_path.exists()     # Have we warmed the cache?
(datetime.now() - mtime) > ttl       # Is it stale?
```

**Key insight:** What appears to be simple file paths are actually **implicit behavior queries**. The class provides explicit methods to ask these questions:

```python
def is_valid(self) -> bool:
    """Checks: is posterior available? Is cache warm?"""
    
def is_stale(self) -> bool:
    """Checks: is posterior older than TTL?"""
    
def is_cache_warm(self) -> bool:
    """Checks: do summary stats exist?"""
```

---

## Part 3: Behaviors and Methods

### Validation Methods (Assessing Readiness)

```python
# These are all "state checkers" — they ask "are we ready?"
is_valid()              → bool  (is posterior AND summary_stats present?)
is_posterior_available() → bool (does NetCDF exist?)
is_cache_warm()         → bool  (do we have pre-computed stats?)
is_stale()              → bool  (is posterior older than TTL hours?)
```

**Pattern observation:** CacheManager follows a **validation pattern**. It doesn't enforce state; it lets you **query** state and make decisions.

### Data Production Methods (Computing Results)

```python
warm_cache()            → bool  # Pre-compute statistics for all ICBs
load_posteriors()       → InferenceData  # Load the full posterior
load_summary_stats()    → dict  # Load pre-computed summaries
load_samples(icb_idx)   → np.ndarray  # Fast load individual ICB samples
```

**Pattern observation:** These methods transition data from "expensive to compute" (posteriors) to "instant to access" (JSON, NPY files).

### Introspection Methods (Understanding Health)

```python
get_health_check()      → dict  # Diagnostic snapshot
get_status_report()     → str   # Human-readable summary
```

---

## Part 4: Object Relationships and Composition

Let me map out the **relationships** between objects:

### Direct Composition: CacheManager and Its Collaborators

```
CacheManager
├── depends on: Path (filesystem interaction)
├── reads/writes: arviz.InferenceData (NetCDF format)
├── reads/writes: json (summary_stats.json)
├── reads/writes: numpy arrays (samples/*.npy)
└── manages lifecycle of all above
```

### Dependency Chain (Inference → Cache → UI)

```
Offline Process (inference_daemon.py)
  ↓ writes posteriors + calls warm_cache()
CacheManager (cache_manager.py)
  ↓ validates + serves
app_fast.py (Streamlit UI)
  ↓ (guaranteed zero MCMC computation)
User Dashboard
```

### Key Insight: This is a **Producer-Consumer** Pattern

- **Producer**: `inference_daemon.py` + `run_inference.py` produce posteriors
- **Intermediary**: `CacheManager` buffers and validates
- **Consumer**: `app_fast.py` (read-only) and `app.py` (interactive) consume

The design ensures **no surprises**:
- If `cache.is_valid()` returns True, the UI **guarantees** no MCMC will run
- This is enforced by explicit validation before any load attempt

---

## Part 5: The Bayesian Model Object

### Secondary Prominent Object: The Pressure Model

While **CacheManager** is the system's coordinator, the **Bayesian pressure model** is the domain object:

```python
def fit_pressure_model(df: pd.DataFrame, *, fast: bool = True):
    """
    Returns: (pm.Model, arviz.InferenceData)
    
    Model structure:
    - mu_national: scalar national latent ~ Normal(0, 1)
    - icb_effect: per-ICB deviations ~ Normal(0, 1)
    - sigma_icb: scaling factor ~ Exponential(1)
    - latent_pressure = mu_national + icb_effect[icb_codes] * sigma_icb
    - observation: bed_occupancy ~ Normal(85 + latent_pressure * 6, sigma_obs)
    """
```

**Attributes of the Pressure Model:**
- **Fixed hyperparameters**: intercept (85), slope (6), priors
- **Learned parameters**: `mu_national`, `icb_effect`, `sigma_icb`, `sigma_obs`
- **Data**: `icb_codes`, `beds` (observed bed occupancy)

**Behaviors:**
- Specify the probabilistic structure (`pm.Normal`, `pm.Exponential`)
- Sample from posterior via NUTS sampler
- Return diagnostics (ESS, Rhat, etc.) in InferenceData

---

## Part 6: Data-Centric Design

### The DataFrame as Domain Model

```python
df = pd.read_csv("synthetic_nhs_pressure.csv")
# Columns: icb, week, bed_occupancy, ... [many features]
# Index: rows per (ICB, week) combination
```

**Key relationships:**

| Component | How It Uses the DataFrame |
|-----------|--------------------------|
| `fit_pressure_model()` | Extracts `icb` codes and `bed_occupancy` values |
| `CacheManager.warm_cache()` | Reads metadata (ICB list) from posterior; creates summary stats |
| `app_fast.py` | Doesn't load the CSV at all—uses only cached results |

**Insight:** The **DataFrame is not persisted in the design**. It exists to:
1. Fit the model (offline in `run_inference.py`)
2. Then gets **summarized** into the cache
3. The original CSV is never loaded in the UI (perfect separation)

---

## Part 7: Design Patterns in Action

### Pattern 1: Resource Gatekeeper (CacheManager)

**Purpose:** Centralize state management and validation

```python
# Before accessing posteriors, check readiness
cache = CacheManager()
if not cache.is_valid():
    raise FileNotFoundError("Run inference first")

idata = cache.load_posteriors()  # Now safe
```

**Benefit:** One place to enforce preconditions; prevents silent failures or invalid states.

---

### Pattern 2: Lazy Computation + Caching

**Purpose:** Separate "expensive first-time computation" from "fast repeated access"

```python
# First time (offline): warm_cache() pre-computes and saves JSON/NPY
cache.warm_cache()  # ~seconds, runs once

# Every time (UI): load from disk (instant)
stats = cache.load_summary_stats()  # ~milliseconds
```

**Benefit:** Fast, predictable UI performance. Shifts cost to offline process.

---

### Pattern 3: Composition Over Inheritance

**Example:** CacheManager doesn't inherit from anything; it **uses** Path, arviz, json, numpy

```python
# Good: composition
class CacheManager:
    def __init__(self, posteriors_path):
        self.posteriors_path = Path(posteriors_path)  # USE Path
        self.cache_dir = Path(cache_dir)              # USE Path
```

**Why?** Keeps concerns separate:
- CacheManager is about **logic** (validation, warming, health checks)
- Path is about **filesystem operations**

If we inherited from Path, we'd mix those concerns and get a weird hybrid object.

---

### Pattern 4: Validation Before Use (Fail-Fast)

**Example:** `app_fast.py` stops immediately if cache is invalid

```python
cache = CacheManager(posteriors_path=POSTERIORS_NC)

if not cache.is_valid():
    st.error("Cache not ready")
    st.stop()  # Don't proceed

# Only here do we know we're safe
idata = load_posteriors(cache)
```

**Benefit:** Explicit validation prevents hidden failures like:
- "Why is the model fitting during my dashboard request?"
- "Why are results stale?"

---

## Part 8: Relationships Between Objects (Detailed)

### Object Interaction Map

```
┌─────────────────────────────────────────────────────────────┐
│                     inference_daemon.py                      │
│  (background: runs at interval, writes posteriors + warms)  │
└──────────────────────┬──────────────────────────────────────┘
                       │ reads CSV
                       ↓
               ┌────────────────┐
               │   DataFrames   │
               │   (pandas)     │
               └────────┬───────┘
                        │ fit_pressure_model()
                        ↓
         ┌──────────────────────────────┐
         │ PyMC Model + Sampling        │
         │ (bayesian_pressure_model.py) │
         └──────────────┬───────────────┘
                        │ arviz.InferenceData
                        ↓
         ┌──────────────────────────────┐
         │   CacheManager               │
         │   (cache_manager.py)         │
         │  - warm_cache()              │
         │  - validate()                │
         │  - load_posteriors()         │
         └──────────────┬───────────────┘
                        │
            ┌───────────┼───────────┐
            ↓           ↓           ↓
     ┌─────────┐  ┌──────────┐  ┌─────────┐
     │posteriors│  │ summary  │  │ samples │
     │.nc      │  │_stats.   │  │ .npy    │
     │(NetCDF) │  │json      │  │(NumPy)  │
     └─────────┘  └──────────┘  └─────────┘
            │           │           │
            └───────────┼───────────┘
                        │
            ┌───────────┴──────────┐
            ↓                      ↓
     ┌────────────┐       ┌──────────────┐
     │ app_fast.py│       │   app.py     │
     │(read-only) │       │(interactive) │
     └────────────┘       └──────────────┘
            ↓                      ↓
     ┌────────────────────────────────┐
     │   User Dashboards (Streamlit)  │
     └────────────────────────────────┘
```

---

## Part 9: Inheritance vs. Composition Decision

### Could We Have Used Inheritance?

**Bad idea:** `class CacheManager(Path)`
- Path is for **filesystem operations**
- CacheManager is for **validation + coordination logic**
- Mixing them creates a confusing, overpowered class

**Good design:** `class CacheManager` **uses** Path objects
- Each class has one responsibility
- CacheManager orchestrates; Path manages files
- Easy to test, easy to extend

---

### Could We Have Used Inheritance for Models?

**Could:** `class PressureModel(pm.Model)`
- **Reason not to:** PyMC models are created dynamically in a context manager:
  ```python
  with pm.Model() as model:  # ← model is context-managed
      pm.Normal(...)
  ```
- Inheriting would be awkward and unusual for PyMC users
- **Better:** Wrap the creation logic in a function that **returns** a model

---

## Part 10: Attributes Analysis Deep Dive

### CacheManager: Attributes and Their Types

| Attribute | Type | Role | Mutable? |
|-----------|------|------|----------|
| `posteriors_path` | Path | Location of NetCDF file | No (set once) |
| `cache_dir` | Path | Directory for cache files | No (set once) |
| `ttl_hours` | int | Staleness threshold | No (set once) |
| `summary_stats_path` | Path | Derived from cache_dir | No (derived) |
| `icb_samples_path` | Path | Derived from cache_dir | No (derived) |
| `health_check_path` | Path | Derived from cache_dir | No (derived) |

**Key insight:** All attributes are **immutable after initialization**. This is excellent for predictability.

### What About "Hidden" Attributes?

CacheManager doesn't store:
- Loaded posteriors (computed on-demand)
- Cached stats (stored on disk, not in memory)

This is **intentional isolation**:
- UI can reload fresh data each time
- Avoids stale-in-memory caches
- Guarantees consistency with disk

---

## Part 11: Methods as Behaviors—A Behavior Inventory

### Behavior Category: Querying State

```python
# "Are we healthy?"
is_valid()                  # Both posteriors and stats present?
is_posterior_available()    # NetCDF exists?
is_cache_warm()            # Stats computed?
is_stale()                 # Older than TTL?
```

**Implementation detail:** These ask the filesystem, they don't store state.

### Behavior Category: Production

```python
# "Compute and store results"
warm_cache()               # Compute all ICB stats, save to JSON/NPY
```

### Behavior Category: Consumption

```python
# "Get data to use"
load_posteriors()          # Load NetCDF → InferenceData
load_summary_stats()       # Load JSON → dict
load_samples()             # Load NPY → ndarray
```

### Behavior Category: Maintenance

```python
# "Keep the system healthy"
clear_cache()              # Delete summary stats (but not posteriors)
get_health_check()         # Read diagnostic snapshot
get_status_report()        # Generate human-readable summary
```

---

## Part 12: Key Relationships Summary

### Objects That "Collaborate" With CacheManager

1. **Filesystem** (via `Path`)
   - CacheManager creates, reads, writes, and checks file existence
   - Relationship: **Strong ownership** (CacheManager decides what goes where)

2. **InferenceData** (via `arviz`)
   - CacheManager loads and passes to consumers
   - Relationship: **Temporary access** (loaded, used, released)

3. **JSON files**
   - Stores summary statistics
   - Relationship: **Serialization** (converts dicts ↔ JSON)

4. **NumPy arrays**
   - Cached ICB samples for fast resampling
   - Relationship: **Performance optimization** (faster than NetCDF for small subsets)

5. **Streamlit apps**
   - Consumer of cached data
   - Relationship: **Data supplier** (CacheManager → app)

6. **Inference daemon**
   - Producer of raw posteriors
   - Relationship: **Data sink** (inference_daemon → CacheManager)

---

## Part 13: Design Strengths in This Codebase

### ✓ Clear Separation of Concerns
- **Inference logic** lives in `bayesian_pressure_model.py`
- **Caching logic** lives in `cache_manager.py`
- **UI logic** lives in `app_fast.py` and `app.py`

Each file can be understood independently.

### ✓ Defensive Validation
```python
if not cache.is_valid():
    st.error("Cache not ready")
    st.stop()
```

The app **refuses** to run if preconditions aren't met. No hidden MCMC.

### ✓ Offline-First Architecture
- Expensive computation (MCMC) happens **once** offline
- UI reads **only** from fast cache
- Guarantees low latency for dashboard users

### ✓ Idempotent Operations
```python
cache.warm_cache()  # Safe to call repeatedly
                    # (overwrites existing files, no state conflicts)
```

Can be safely included in a background task or cron job.

### ✓ File-Based Serialization
Uses standard formats (NetCDF, JSON, NPY), not proprietary databases.
- Easy to version control summaries
- Easy to inspect with standard tools
- Easy to archive or transfer

---

## Part 14: Design Weaknesses / Considerations

### ⚠ Implicit Dependencies
The **original CSV** (`synthetic_nhs_pressure.csv`) is loaded **only** during inference, not stored in the cache. If you lose it:
- You can't re-warm the cache
- You can't re-fit the model with new parameters

**Mitigation:** Document this; consider storing metadata about the input (row count, date range, etc.) in `health_check.json`.

### ⚠ Single-Chain MCMC (by design)
```python
trace = pm.sample(
    chains=1,  # ← Not standard practice for assurance-grade inference
    ...
)
```

This is acceptable for a **demo** but would need `chains=4` (typical) for production.

**Note:** The code is explicit about this. It's a conscious trade-off (speed vs. diagnostics).

### ⚠ No Explicit Lock on Cache Writes
If two processes call `warm_cache()` simultaneously, they could corrupt JSON files. For a background daemon, this is probably fine; for shared systems, you might add a lock.

---

## Part 15: Object-Oriented Design Takeaways

### The Central Lesson

This codebase demonstrates that **good OOP is not about inheritance hierarchies**. It's about:

1. **Clear responsibilities** — Each object knows its job
2. **Composition** — Objects collaborate through clear interfaces
3. **Validation** — Explicit precondition checks prevent silent errors
4. **Immutability** — Paths and TTLs don't change after initialization
5. **Separation** — Expensive computation is separate from fast consumption

### UML Sketch of Core Relationships

```
┌────────────────────────┐
│  CacheManager          │
├────────────────────────┤
│ - posteriors_path      │
│ - cache_dir            │
│ - ttl_hours            │
├────────────────────────┤
│ + is_valid()           │
│ + warm_cache()         │
│ + load_posteriors()    │
│ + load_summary_stats() │
└────────┬───────────────┘
         │ uses
         ├────────→ Path (filesystem)
         ├────────→ arviz.InferenceData
         ├────────→ JSON (serialization)
         └────────→ NumPy (arrays)

┌──────────────────────────┐
│  fit_pressure_model()    │
├──────────────────────────┤
│ input:  pd.DataFrame     │
│ output: (pm.Model, az)   │
└──────────┬───────────────┘
           │ uses
           ├───────→ PyMC
           ├───────→ NumPy
           └───────→ ArviZ

Interaction:
  inference_daemon.py → fit_pressure_model() → pm.sample()
                     → CacheManager.warm_cache()
                     → app_fast.py reads from CacheManager
```

---

## Reflection Exercise (For You)

Now that we've mapped this system, reflect on your own work:

### Questions to Ask About Your Next Project

1. **What's the prominent object?**
   - In this system: CacheManager
   - In your project: What coordinates the whole flow?

2. **What attributes would it have?**
   - Are they primitives or classes?
   - Are some attributes actually state disguised as data?

3. **What methods (behaviors) would it have?**
   - Validators? (checking state)
   - Producers? (computing new data)
   - Consumers? (using data)
   - Introspection? (reporting health)

4. **Should you inherit, compose, or wrap?**
   - CacheManager doesn't inherit from Path; it **uses** Path
   - fit_pressure_model returns a tuple; it doesn't subclass pm.Model
   - **Default to composition** unless inheritance solves a real problem

5. **What are the object relationships?**
   - Producer → Intermediary → Consumer?
   - Gatekeeper → Resource?
   - Factory → Product?

---

## Summary: What Makes This Design Work?

1. **CacheManager is a boundary object** — It separates the expensive computation layer from the fast consumption layer
2. **Validation is explicit** — No surprises; if `is_valid()` is true, you're safe
3. **Composition is favored** — Each object does one thing well
4. **Immutability is assumed** — Paths and settings don't change during execution
5. **Offline-first** — Expensive work happens separately; the UI is guaranteed fast

This is **practical OOP**—not about academic purity, but about making the system resilient, fast, and easy to understand.
