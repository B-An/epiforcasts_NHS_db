# Code Examples: OOP Design in Action

This document highlights specific code locations and how they demonstrate OOP principles.

---

## 1. CacheManager: The Gatekeeper Object

### File: [cache_manager.py](cache_manager.py#L1)

**The class definition and initialization** ([L23-L47](cache_manager.py#L23-L47)):

```python
class CacheManager:
    """Manages cached posteriors and summary statistics."""
    
    def __init__(
        self,
        posteriors_path: Path | str = "posteriors.nc",
        cache_dir: Path | str = ".cache",
        ttl_hours: int = 24,
    ):
        # Attributes: composition of Path objects
        self.posteriors_path = Path(posteriors_path)
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        
        # Derived paths (immutable after init)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.summary_stats_path = self.cache_dir / "summary_stats.json"
        self.icb_samples_path = self.cache_dir / "icb_samples"
        self.health_check_path = self.cache_dir / "health_check.json"
```

**Key OOP Insight:**
- ✓ Immutable initialization: All paths are set once and never modified
- ✓ Composition: Uses Path objects internally, doesn't inherit from them
- ✓ Encapsulation: Derived paths are private implementation details

---

### Validation Methods (State Queries)

**Checking if system is ready** ([L49-L76](cache_manager.py#L49-L76)):

```python
def is_valid(self) -> bool:
    """Check if cache is valid and complete."""
    if not self.is_posterior_available():
        logger.warning(f"Posterior file missing: {self.posteriors_path}")
        return False
    
    if not self.is_cache_warm():
        logger.warning("Summary statistics cache not warmed")
        return False
    
    return True
```

**Key OOP Insight:**
- ✓ Explicit validation pattern: Don't silently proceed with invalid state
- ✓ Fail-fast: Return boolean to let caller decide
- ✓ Logging: Each method documents why validation failed

**Where this is used** ([app_fast.py#L120-L128](app_fast.py#L120-L128)):

```python
# Validate cache is ready (no MCMC runs guaranteed here)
if not cache.is_valid():
    st.error(
        f"❌ Cache not ready\n\n"
        f"**Status:** Posterior {'✓' if cache.is_posterior_available() else '✗'} | "
        f"Cache {'✓' if cache.is_cache_warm() else '✗'}\n\n"
        f"**Run:** `python inference_daemon.py --once`"
    )
    st.stop()  # Don't proceed if invalid
```

**Key OOP Insight:**
- ✓ Precondition checking: UI refuses to run if preconditions aren't met
- ✓ User-friendly errors: Tells exactly what's wrong and how to fix it
- ✓ Defensive programming: `st.stop()` prevents silent failures

---

### Cache Warming: Pre-computation

**Warm cache method** ([cache_manager.py#L77-L145](cache_manager.py#L77-L145)):

```python
def warm_cache(self) -> bool:
    """Pre-compute and cache summary statistics."""
    if not self.is_posterior_available():
        logger.error(f"Cannot warm cache; posterior missing")
        return False
    
    try:
        logger.info(f"Warming cache from {self.posteriors_path}…")
        
        idata = az.from_netcdf(str(self.posteriors_path))
        icbs = idata.attrs.get("icbs", [])
        
        summary_stats = {}
        for icb_idx, icb_name in enumerate(icbs):
            logger.debug(f"Computing statistics for {icb_name}…")
            
            samples = self._extract_samples(idata, icb_idx)
            stats = {
                "icb_name": icb_name,
                "mean": float(np.mean(samples)),
                "median": float(np.median(samples)),
                "std": float(np.std(samples)),
                "quantiles": {
                    "q05": float(np.percentile(samples, 5)),
                    # ... more quantiles ...
                },
                "probabilities": {
                    "p_above_baseline": float(np.mean(samples > 0.0)),
                    # ... more probabilities ...
                },
            }
            summary_stats[icb_name] = stats
        
        # Save to disk
        with open(self.summary_stats_path, "w") as f:
            json.dump(summary_stats, f, indent=2)
        
        logger.info(f"✓ Cache warmed: {len(summary_stats)} ICBs")
        return True
    
    except Exception as e:
        logger.error(f"Cache warming failed: {e}", exc_info=True)
        return False
```

**Key OOP Insight:**
- ✓ Separation of concerns: Computing stats is **one** method
- ✓ Defensive: Try-except handles errors gracefully
- ✓ Logging: Each step is documented for debugging
- ✓ Idempotent: Safe to call repeatedly (overwrites JSON files)
- ✓ Behavior vs data: `_extract_samples()` is a helper method, not exposed

---

### Health and Introspection

**Status reporting method** ([cache_manager.py#L225-L258](cache_manager.py#L225-L258)):

```python
def get_status_report(self) -> str:
    """Get human-readable cache status."""
    lines = [
        "Cache Status Report",
        "=" * 50,
    ]
    
    # Posterior file
    if self.posteriors_path.exists():
        size_mb = self.posteriors_path.stat().st_size / (1024**2)
        mtime = datetime.fromtimestamp(self.posteriors_path.stat().st_mtime)
        lines.append(f"✓ Posteriors: {self.posteriors_path} ({size_mb:.1f} MB)")
        lines.append(f"  Updated: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  Stale: {self.is_stale()}")
    else:
        lines.append(f"✗ Posteriors: MISSING")
    
    # Cache warmth
    if self.is_cache_warm():
        lines.append(f"✓ Summary stats: {self.summary_stats_path}")
    else:
        lines.append(f"✗ Summary stats: NOT WARMED")
    
    lines.append("=" * 50)
    return "\n".join(lines)
```

**Key OOP Insight:**
- ✓ Introspection: Object can report its own health
- ✓ Composition: Uses `is_stale()`, `is_cache_warm()` methods internally
- ✓ String building: Separates format from logic

---

## 2. Bayesian Model: Domain Logic Encapsulation

### File: [bayesian_pressure_model.py](bayesian_pressure_model.py)

**Model definition** ([bayesian_pressure_model.py#L20-L47](bayesian_pressure_model.py#L20-L47)):

```python
def fit_pressure_model(df, *, fast: bool | None = None):
    """Bayesian latent pressure on bed occupancy."""
    
    if fast is None:
        fast = _FAST
    
    icb_codes = df["icb"].astype("category").cat.codes.values
    beds = df["bed_occupancy"].values
    
    if fast:
        draws, tune = 400, 400
    else:
        draws, tune = 1000, 1000
    
    with pm.Model() as model:
        mu_national = pm.Normal("mu_national", 0, 1)
        sigma_icb = pm.Exponential("sigma_icb", 1)
        icb_effect = pm.Normal(
            "icb_effect",
            0,
            1,
            shape=len(np.unique(icb_codes)),
        )
        
        latent_pressure = mu_national + icb_effect[icb_codes] * sigma_icb
        sigma_obs = pm.Exponential("sigma_obs", 5)
        
        pm.Normal(
            "bed_obs",
            mu=85 + latent_pressure * 6,
            sigma=sigma_obs,
            observed=beds,
        )
        
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=1,
            cores=1,
            target_accept=0.9,
            progressbar=False,
        )
    
    return model, trace
```

**Key OOP Insight:**
- ✓ Encapsulation: All Bayesian logic in one function
- ✓ Contract: Takes `(df, fast)` → returns `(model, trace)`
- ✓ Immutability: `fast` parameter determines behavior completely
- ✓ Composition: Doesn't inherit from `pm.Model`; returns it
- ✓ Algorithm flexibility: `fast=True` for UI (400 draws), `False` for precision

**Usage from inference daemon** ([run_inference.py#L38-L70](run_inference.py#L38-L70)):

```python
def fit_pressure_model(df: pd.DataFrame, *, fast: bool = True):
    """Fit Bayesian latent pressure model."""
    
    icb_codes = df["icb"].astype("category").cat.codes.values
    beds = df["bed_occupancy"].values
    
    draws = 400 if fast else 1000
    tune = 400 if fast else 1000
    
    print(f"Sampling with draws={draws}, tune={tune}, fast={fast}")
    
    with pm.Model() as model:
        # [model specification...]
        
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=1,
            cores=1,
            target_accept=0.9,
            progressbar=True,
            compute_convergence_checks=True,
        )
    
    idata = az.from_pymc3(trace)
    return model, idata
```

**Key OOP Insight:**
- ✓ Single responsibility: Function only cares about fitting
- ✓ Clear interface: Takes DataFrame, returns (Model, InferenceData)
- ✓ Flexibility: `fast` parameter controls computational cost

---

## 3. Inference Daemon: Producer Pattern

### File: [inference_daemon.py](inference_daemon.py)

**Checking if re-inference is needed** ([inference_daemon.py#L41-L70](inference_daemon.py#L41-L70)):

```python
def should_rerun_inference(
    data_path: Path,
    posterior_path: Path,
    force: bool = False,
) -> bool:
    """Check if inference should be rerun."""
    
    if force:
        return True
    
    if not posterior_path.exists():
        logger.info(f"Posterior file missing: {posterior_path}")
        return True
    
    if not data_path.exists():
        logger.warning(f"Data file missing: {data_path}")
        return False
    
    data_mtime = data_path.stat().st_mtime
    posterior_mtime = posterior_path.stat().st_mtime
    
    if data_mtime > posterior_mtime:
        logger.info(f"Data updated; posterior is stale")
        return True
    
    logger.debug(f"Posterior is current; skipping inference")
    return False
```

**Key OOP Insight:**
- ✓ Intelligent decision-making: Checks multiple conditions
- ✓ Logging: Documents why the decision was made
- ✓ File-based versioning: Uses mtime to detect data updates
- ✓ Optimization: Skip unnecessary recomputation

**Safe inference execution** ([inference_daemon.py#L73-L120](inference_daemon.py#L73-L120)):

```python
def run_inference_safe(
    data_path: Path,
    posterior_path: Path,
    fast: bool = True,
) -> bool:
    """Safely run inference and save results."""
    
    try:
        import numpy as np
        import pymc as pm
        import arviz as az
        
        logger.info(f"Loading data from {data_path}…")
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} rows")
        
        # Fit model
        logger.info("Fitting pressure model…")
        model, trace = fit_pressure_model(df, fast=fast)
        
        # Save posteriors
        logger.info(f"Saving posterior to {posterior_path}…")
        idata = az.from_pymc3(trace)
        idata.to_netcdf(str(posterior_path))
        
        logger.info("✓ Inference complete")
        return True
    
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        return False
```

**Key OOP Insight:**
- ✓ Error handling: Try-except prevents crashes
- ✓ Logging: Every step is documented
- ✓ File serialization: Saves to standard NetCDF format
- ✓ Boolean return: Caller knows if it succeeded

---

## 4. Streamlit UI: Consumer Pattern

### File: [app_fast.py](app_fast.py)

**Initialization and validation** ([app_fast.py#L110-L147](app_fast.py#L110-L147)):

```python
st.set_page_config(layout="wide", page_title="NHS Pressure — Fast View")
st.title("🏥 NHS System Pressure — Current Status (demo)")

# Initialize cache manager
cache = CacheManager(posteriors_path=POSTERIORS_NC)

# Validate cache is ready (no MCMC runs guaranteed here)
if not cache.is_valid():
    st.error(
        f"❌ Cache not ready\n\n"
        f"**Status:** Posterior {'✓' if cache.is_posterior_available() else '✗'} | "
        f"Cache {'✓' if cache.is_cache_warm() else '✗'}\n\n"
        f"**Run:** `python inference_daemon.py --once`"
    )
    st.stop()

# Load from cache (guaranteed zero computation)
@st.cache_resource(show_spinner="Loading cached posteriors…")
def load_posteriors(cache_manager: CacheManager):
    """Load posteriors from cache (no MCMC, guaranteed)."""
    return cache_manager.load_posteriors()

idata = load_posteriors(cache)
```

**Key OOP Insight:**
- ✓ **Defensive design**: Refuses to proceed if preconditions fail
- ✓ **Caching pattern**: `@st.cache_resource` avoids reloading
- ✓ **User feedback**: Error message tells exactly what to do
- ✓ **Zero computation guarantee**: If `is_valid()` is true, no MCMC will run

**Data extraction and display** ([app_fast.py#L30-L60](app_fast.py#L30-L60)):

```python
def _pressure_index_samples(idata: az.InferenceData, icb_idx: int) -> np.ndarray:
    """Extract posterior samples for a given ICB."""
    post = idata.posterior
    mu = post["mu_national"].values
    eff = post["icb_effect"].values
    sig = post["sigma_icb"].values
    combined = mu + eff[..., icb_idx] * sig
    return combined.astype(float).ravel()

def _credible_triplet(samples: np.ndarray, mass: float = 0.9) -> tuple[float, float, float]:
    """Equal-tailed interval."""
    alpha = (1.0 - mass) / 2.0
    lo, mid, hi = [
        float(x)
        for x in np.percentile(samples, [100.0 * alpha, 50.0, 100.0 * (1.0 - alpha)])
    ]
    return lo, mid, hi
```

**Key OOP Insight:**
- ✓ **Method extraction**: Each visualization component has its own method
- ✓ **Single responsibility**: `_pressure_index_samples()` does one thing
- ✓ **Type hints**: Clear contracts (input/output types)
- ✓ **Composition**: Helper functions build larger visualization

---

## 5. Object Relationships Summary

### The Dependency Graph

```
1. Offline Producer (inference_daemon.py)
   ├─ calls: fit_pressure_model(df)
   ├─ reads: synthetic_nhs_pressure.csv
   └─ writes to: CacheManager.warm_cache()

2. Gatekeeper (CacheManager)
   ├─ validates: is_valid(), is_cache_warm()
   ├─ manages: posteriors.nc, summary_stats.json, icb_samples/*.npy
   └─ serves: load_posteriors(), load_summary_stats()

3. Online Consumer (app_fast.py)
   ├─ checks: cache.is_valid()
   ├─ reads from: CacheManager
   └─ guarantees: zero MCMC computation
```

### Key Design Decisions and Why

| Decision | Why | Code Location |
|----------|-----|----------------|
| CacheManager is a separate class | Centralizes state management; easy to test | [cache_manager.py#L23](cache_manager.py#L23) |
| `is_valid()` must pass before UI runs | Prevents hidden MCMC during user requests | [app_fast.py#L120](app_fast.py#L120) |
| Immutable paths in `__init__` | No surprise path changes during execution | [cache_manager.py#L32-L38](cache_manager.py#L32-L38) |
| `warm_cache()` is idempotent | Safe to call multiple times or on a schedule | [cache_manager.py#L77](cache_manager.py#L77) |
| Bayesian model returns tuple | Doesn't force subclassing; clean separation | [bayesian_pressure_model.py#L47](bayesian_pressure_model.py#L47) |
| Streamlit caching decorators | Speed up UI without reloading data | [app_fast.py#L101-L103](app_fast.py#L101-L103) |

---

## Reflection: How This Demonstrates Good OOP

### ✓ Composition Over Inheritance
- CacheManager **uses** Path objects; doesn't inherit
- Bayesian model returns (Model, InferenceData); doesn't subclass
- Streamlit UI **uses** CacheManager; doesn't inherit

### ✓ Single Responsibility
- CacheManager: cache management and validation
- fit_pressure_model(): Bayesian inference only
- inference_daemon.py: Scheduling and orchestration
- app_fast.py: UI rendering only

### ✓ Clear Contracts
- `is_valid()` → bool (precondition checker)
- `warm_cache()` → bool (producer)
- `load_posteriors()` → InferenceData (consumer)
- `fit_pressure_model(df, fast)` → (Model, InferenceData) (domain logic)

### ✓ Defensive Programming
```python
# Don't proceed if preconditions aren't met
if not cache.is_valid():
    st.stop()
```

### ✓ Explicit State Management
```python
# Don't hide state; make it queryable
cache.is_cache_warm()
cache.is_stale()
cache.get_status_report()
```

---

## The Lesson

This codebase is an excellent example of **practical OOP**: not about inheritance hierarchies, but about:

1. **Clear objects with single responsibilities**
2. **Explicit validation before use**
3. **Composition to combine concerns**
4. **Immutable initialization**
5. **File-based serialization for persistence**

Each object knows its job, validates its preconditions, and talks to others through clear interfaces.
