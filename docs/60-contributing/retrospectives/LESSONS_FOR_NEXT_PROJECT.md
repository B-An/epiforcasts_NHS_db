# OOP Design Synthesis: Lessons for Your Next Project

> This document applies the book's exercise insights to your codebase and extracts lessons you can use immediately.

---

## The Book's Framework Applied to Your Code

The book asked you to:
1. **Identify the prominent object** ✓ → CacheManager
2. **Enumerate its attributes** ✓ → paths, ttl_hours, derived paths
3. **Distinguish primitives from classes** ✓ → int vs. Path objects
4. **Find hidden behaviors** ✓ → file existence is implicit state
5. **List methods and relationships** ✓ → validators, loaders, producers
6. **Consider inheritance vs. composition** ✓ → composition wins
7. **Sketch a class diagram** ✓ → Created three diagrams

---

## Your Prominent Object: CacheManager

### What Makes It Prominent?

```
Every other component depends on it:
  inference_daemon.py ────┐
  run_inference.py ────────→ CacheManager ←─── app_fast.py
  app.py ──────────────────┘
```

It's the **bottleneck** where producers meet consumers.

### Its Attributes (Complete Inventory)

| Attribute | Type | Mutability | Purpose |
|-----------|------|-----------|---------|
| `posteriors_path` | `Path` | Immutable | Location of raw MCMC posteriors |
| `cache_dir` | `Path` | Immutable | Root directory for all cache files |
| `ttl_hours` | `int` | Immutable | Staleness threshold (for warnings) |
| `summary_stats_path` | `Path` | Derived (immutable) | Where pre-computed stats live |
| `icb_samples_path` | `Path` | Derived (immutable) | Where individual sample arrays live |
| `health_check_path` | `Path` | Derived (immutable) | Where metadata snapshot lives |

**Key insight:** All attributes are **immutable after initialization**. Once the object is created, it never changes shape. This makes it **predictable** and **thread-safe** (if needed).

### Its Behaviors (Method Inventory)

#### Category 1: Validators (State Checkers)
```python
is_valid()              # Both posterior AND stats present?
is_posterior_available() # NetCDF file exists?
is_cache_warm()         # Stats computed?
is_stale()              # Older than TTL?
```

**When to use:** Before any operation that depends on cache readiness.

```python
# Real usage in app_fast.py
if not cache.is_valid():
    st.stop()  # Don't proceed
```

#### Category 2: Producers (Computing New Data)
```python
warm_cache()            # Pre-compute stats from posterior, save to disk
```

**When to use:** After a new posterior is written, before UI is accessed.

```python
# Real usage in inference_daemon.py
model, trace = fit_pressure_model(df)
# ... save posterior ...
cache.warm_cache()  # Pre-compute summaries
```

#### Category 3: Loaders (Retrieving Data)
```python
load_posteriors()       # Load from NetCDF
load_summary_stats()    # Load from JSON
load_samples(icb_idx)   # Load from NPY
```

**When to use:** In UI code that needs data to display.

```python
# Real usage in app_fast.py
idata = load_posteriors(cache)  # Full posterior
stats = load_summary_stats(cache)  # Quick summaries
```

#### Category 4: Introspection (Reporting Health)
```python
get_health_check()      # Structured health snapshot
get_status_report()     # Human-readable summary
clear_cache()           # Delete computed files
```

**When to use:** Debugging, monitoring, maintenance tasks.

---

## Design Pattern #1: The Gatekeeper

### What It Is
An object that stands between a producer and consumer, ensuring **preconditions are met** before data flows.

### In Your Code
```python
# app_fast.py: Don't proceed without validation
if not cache.is_valid():
    st.stop()

# This GUARANTEES:
# 1. Posterior file exists
# 2. Summary stats are computed
# 3. No MCMC will run in the UI
```

### Why It Works
- **Single point of control**: All data access goes through CacheManager
- **Explicit validation**: No silent failures
- **Clear failure messages**: User knows exactly what to do

### How to Apply This in Your Next Project

When you have:
- **Expensive computation** (MCMC, model fitting)
- **Multiple consumers** (dashboards, reports, APIs)
- **Need for speed** (can't recompute on every request)

**Create a gatekeeper object that:**
1. Validates preconditions
2. Manages lifecycle
3. Serves pre-computed results

---

## Design Pattern #2: Producer-Consumer with Intermediate Cache

### The Flow
```
[Offline Producer] ──→ [Cache Manager] ──→ [Online Consumers]
(inference_daemon)    (validation)       (app_fast.py)
  (expensive work)     (buffering)         (instant access)
```

### Why This Separation?

| Layer | Concern | Time | Guarantees |
|-------|---------|------|-----------|
| Producer | Fit models correctly | Minutes/hours | Correct results |
| Cache | Keep data organized | Seconds | Data available |
| Consumer | Show results fast | Milliseconds | Zero MCMC |

**Key:** Each layer has **different performance requirements**. Don't force them into one.

### In Your Code
- **Producer**: `inference_daemon.py` (runs hourly, fits model)
- **Cache**: `CacheManager` (validates, warms, serves)
- **Consumer**: `app_fast.py` (loads, displays, instant)

### How to Apply This in Your Next Project

If you need to:
- Compute expensive results once
- Serve them to many users/dashboards
- Guarantee fast response times

**Separate into three layers:**
1. **Producer service**: Compute on a schedule (cron, daemon, queue)
2. **Cache coordinator**: Manage and validate results
3. **Consumer APIs/UIs**: Read-only access to pre-computed data

---

## Design Pattern #3: Composition Over Inheritance

### The Decision Point

**Don't do this:**
```python
class CacheManager(Path):  # ✗ Bad: mixes concerns
    pass
```

**Do this instead:**
```python
class CacheManager:  # ✓ Good: clear separation
    def __init__(self, posteriors_path: Path):
        self.posteriors_path = Path(posteriors_path)
```

### Why?
- **CacheManager's job**: Validate, coordinate, cache
- **Path's job**: Filesystem operations
- **Mixing them**: Confusing, hard to test, hard to extend

### Real Example in Your Code
```python
# CacheManager USES Path objects, doesn't inherit
self.posteriors_path = Path(posteriors_path)
self.cache_dir = Path(cache_dir)
self.summary_stats_path = self.cache_dir / "summary_stats.json"

# CacheManager USES arviz and json, doesn't inherit
idata = az.from_netcdf(str(self.posteriors_path))
with open(self.summary_stats_path, "w") as f:
    json.dump(summary_stats, f)
```

### How to Apply This in Your Next Project

When you want to **reuse functionality**, ask:

**Option A (Inheritance):**
```python
class MyModel(ExistingModel):  # "Is my object a kind of ExistingModel?"
    pass
```
→ Use only if the answer is **YES**.

**Option B (Composition):**
```python
class MyModel:  # "Does my object USE ExistingModel?"
    def __init__(self):
        self.model = ExistingModel()
```
→ Use if the answer is **NO** (most of the time).

**Decision rule:** 
- **Inheritance** = "is-a" relationship (rare)
- **Composition** = "has-a" or "uses-a" relationship (common)

Your code **correctly uses composition** throughout.

---

## Design Pattern #4: Immutable Configuration

### In Your Code
```python
def __init__(self, posteriors_path, cache_dir, ttl_hours):
    self.posteriors_path = Path(posteriors_path)
    self.cache_dir = Path(cache_dir)
    self.ttl_hours = ttl_hours
    # Once set, these NEVER change
```

### Why It Matters
- **Predictability**: If paths don't change, behavior is predictable
- **Thread safety**: No locks needed if data is immutable
- **Debugging**: "Where did this path come from?" has one answer

### How to Apply This in Your Next Project

When creating objects:

**Good (immutable):**
```python
class Config:
    def __init__(self, db_url, api_key, timeout):
        self.db_url = db_url        # Never changes
        self.api_key = api_key      # Never changes
        self.timeout = timeout      # Never changes
```

**Bad (mutable state):**
```python
config = Config()
config.db_url = "postgres://..."  # Changed later ✗
config.timeout = 30               # Changed later ✗
# Now behavior depends on when properties were set
```

---

## Design Pattern #5: Explicit Validation (Fail-Fast)

### In Your Code
```python
# app_fast.py: Check before proceeding
if not cache.is_valid():
    st.error("Cache not ready")
    st.stop()  # Stop execution

# Only here are we guaranteed safe
idata = load_posteriors(cache)
```

### Why It Works
1. **Explicit**: The check is visible in the code
2. **Defensive**: Refuses to proceed with invalid state
3. **Clear errors**: User knows exactly what's wrong

### How to Apply This in Your Next Project

**Pattern:**
```python
# 1. Check preconditions
if not preconditions_met():
    handle_error()
    return

# 2. Only safe work below this line
do_expensive_work()
```

**Example:**
```python
def process_data(df):
    # Explicit validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if not all(col in df.columns for col in ["id", "value"]):
        raise ValueError("Missing required columns")
    
    # Now we KNOW df is valid; safe to proceed
    result = df.groupby("id")["value"].sum()
    return result
```

---

## The Biggest Lesson: Separation of Concerns

### Your System Separates Into Three Tiers

```
OFFLINE TIER (inference_daemon.py)
  ├─ Reads: synthetic_nhs_pressure.csv
  ├─ Computes: PyMC MCMC sampling (expensive)
  ├─ Writes: posteriors.nc
  └─ Time: Minutes/hours (OK to be slow)

COORDINATION TIER (cache_manager.py)
  ├─ Manages: File organization
  ├─ Validates: Is everything ready?
  ├─ Pre-computes: Summary stats
  └─ Time: Seconds (fast enough)

ONLINE TIER (app_fast.py)
  ├─ Reads: JSON summaries, NPY samples
  ├─ Displays: Dashboard
  ├─ Guarantees: Zero MCMC
  └─ Time: Milliseconds (instant)
```

**Why this works:**
- Each tier has realistic performance constraints
- Each tier can evolve independently
- Each tier has one clear job

---

## Red Flags That You're Mixing Concerns

🚩 "The UI sometimes does MCMC" → Too much in one place
🚩 "I don't know where the data comes from" → Unclear boundaries
🚩 "Changing the UI broke the cache" → Too much coupling
🚩 "I have to reload everything to test" → No separation
🚩 "The model and the API are in the same class" → Mixing domains

**Your code:** None of these red flags! ✓

---

## Reflection Questions for Your Next Project

Use these to analyze your projects through an OOP lens:

### 1. Identify Prominent Objects
- What objects appear in multiple files?
- What object coordinates the whole system?
- → This is likely a "prominent object" worth designing carefully

### 2. Enumerate Attributes
- What data does this object hold?
- Are attributes primitives or objects?
- Do any attributes **encode state** (like file existence)?

### 3. Inventory Methods
- What questions can this object answer? (validators)
- What can this object produce? (producers)
- What does this object report about itself? (introspection)

### 4. Consider Relationships
- Does object A depend on B?
- Would inheritance make sense?
- → If "no", use composition

### 5. Sketch Diagrams
- Draw boxes for objects
- Draw arrows for dependencies
- Draw boxes for data flows
- → Does it look clean or tangled?

---

## Actionable Checklist for Your Next Project

When designing an object, ask:

- [ ] **Does it have one clear job?** (Single responsibility)
- [ ] **Are preconditions explicit?** (Validation methods)
- [ ] **Are attributes immutable?** (Set once, never changed)
- [ ] **Does it use composition wisely?** (Has-a, not is-a)
- [ ] **Can I describe it in one sentence?** (Clear purpose)
- [ ] **Would I test this separately?** (Testable unit)
- [ ] **Does it fail explicitly or silently?** (Fail-fast)
- [ ] **Can I explain it to someone else?** (Understandable)

Your **CacheManager** passes all these checks. ✓

---

## Summary: What This Codebase Teaches

1. **Good OOP is not about inheritance**
   - Your code uses composition everywhere
   - You inherit almost nothing
   - That's perfectly fine (and often better)

2. **Prominent objects deserve careful design**
   - CacheManager is the hub
   - It has clear attributes and methods
   - It validates its own preconditions

3. **Separate concerns ruthlessly**
   - Offline computation ≠ online serving
   - Cache management ≠ Bayesian modeling
   - UI rendering ≠ data loading

4. **Make preconditions explicit**
   - `is_valid()` before proceeding
   - `st.stop()` on failure
   - Clear error messages

5. **Composition beats inheritance**
   - Use objects as collaborators
   - Don't force inheritance when composition works
   - Makes code easier to test and modify

---

## Your Next Steps

### Immediate
1. Read [../../20-architecture/oop/OOP_DESIGN_ANALYSIS.md](../../20-architecture/oop/OOP_DESIGN_ANALYSIS.md) for deep analysis
2. Read [../../20-architecture/oop/CODE_EXAMPLES_OOP.md](../../20-architecture/oop/CODE_EXAMPLES_OOP.md) for concrete code references
3. Study the three Mermaid diagrams in VS Code

### When Starting Your Next Project
1. **Identify** the prominent object(s)
2. **List** their attributes and methods
3. **Decide** on composition vs. inheritance
4. **Sketch** a class diagram
5. **Implement** with validation first

### Long-term
- Apply the **gatekeeper pattern** when you have expensive computation
- Use **producer-consumer** pattern for distributed systems
- Default to **composition** over inheritance
- Make **preconditions explicit**
- Separate **concerns** ruthlessly

---

## Final Reflection

> "The goal is not to design a system (although you're certainly welcome to do so if inclination meets both ambition and available time). The goal is to think about object-oriented design."

You've done exactly this. Your codebase is a textbook example of:
- Clear object identification
- Thoughtful attribute design
- Explicit behavior inventory
- Smart composition decisions
- Careful separation of concerns

**This is practical OOP.** Not academic, but real: code that works, is easy to understand, and easy to modify.

Use these principles in your next project.
