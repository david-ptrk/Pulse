"""
random_module.py

Pulse standard library module for random number generation.
Provides core random functions, sequence operations, statistical
distributions, and seed control for reproducible results.
"""

from __future__ import annotations
import random
from src.values import PulseModule, PulseNumber, PulseString, PulseNull, PulseBoolean, PulseList
from src.function import PulseNativeFunction

def make(interp) -> PulseModule:
    """Build and return the Pulse 'random' module."""
    
    def _check_number(val, name: str) -> float:
        """Raise if val is not a PulseNumber, then return its raw float value."""
        if not isinstance(val, PulseNumber):
            interp._raise(f"{name} must be a number, got '{val.type_name()}'")
        return val.value
    
    def _check_int(val, name: str) -> int:
        """Raise is val is not a whole PulseNumber, then return its raw int value."""
        v = _check_number(val, name)
        if v != int(v):
            interp._raise(f"{name} must be an integer, got {v}")
        return int(v)
    
    # Core
    def _random() -> PulseNumber:
        """Return a random float in [0.0,1.0)."""
        return  PulseNumber(random.random())
    
    def _random_int(a, b) -> PulseNumber:
        """Return a random integer N such that a <= N <= b."""
        ia = _check_int(a, "randint() 'a'")
        ib = _check_int(b, "randint() 'b'")
        if ia > ib:
            interp._raise(f"randint() 'a' ({ia}) must be <= 'b' ({ib})")
        return PulseNumber(random.randint(ia, ib))
    
    def _uniform(a, b) -> PulseNumber:
        """Return a random float N such that a <= N <= b."""
        fa = _check_number(a, "uniform() 'a'")
        fb = _check_number(b, "uniform() 'b'")
        return PulseNumber(random.uniform(fa, fb))
    
    # Sequences
    def _choice(seq) -> any:
        """Return a random element from a non-empty list."""
        if not isinstance(seq, PulseList):
            interp._raise(f"choice() argument must be a list, got '{seq.type_name()}'")
        if not seq.elements:
            interp._raise("choice() argument is an empty list")
        return random.choice(seq.elements)
    
    def _choices(seq, k=None) -> PulseList:
        """Return k random elements from list with replacement."""
        if not isinstance(seq, PulseList):
            interp._raise(f"choices() argument must be a list, got '{seq.type_name()}'")
        count = _check_int(k, "choices() 'k' must be non-negative")
        if count < 0:
            interp._raise("choices() 'k' must be non-negative")
        return PulseList(random.choices(seq.elements, k=count))
    
    def _sample(seq, k) -> PulseList:
        """Return k unique random elements from list (no replacement)."""
        if not isinstance(seq, PulseList):
            interp._raise(f"sample() argument must be a list, got '{seq.type_name()}'")
        count = _check_int(k, "sample() 'k'")
        if count < 0:
            interp._raise("sample() 'k' must be non-negative")
        if count > len(seq.elements):
            interp._raise(f"sample() 'k' ({count}) is larger than population size ({len(seq.elements)})")
        return PulseList(random.sample(seq.elements, count))
    
    def _shuffle(seq) -> PulseNull:
        """Shuffle list in place."""
        if not isinstance(seq, PulseList):
            interp._raise(f"shuffle() argument must be a list, got '{seq.type_name()}'")
        random.shuffle(seq.elements)
        return PulseNull()
    
    # Distributions
    def _gauss(mu, sigma) -> PulseNumber:
        """Gaussian distribution with mean mu and std deviation sigma."""
        fmu = _check_number(mu, "gauss() 'mu'")
        fsigma = _check_number(sigma, "gauss() 'sigma'")
        return PulseNumber(random.gauss(fmu, fsigma))
    
    def _normalvariate(mu, sigma) -> PulseNumber:
        """Normal distribution (thread-sade alternative to gauss)."""
        fmu = _check_number(mu, "normalvariate() 'mu'")
        fsigma = _check_number(sigma, "normalvariate() 'sigma'")
        return PulseNumber(random.normalvariate(fmu, fsigma))
    
    def _expovariate(lam) -> PulseNumber:
        """Exponential distribution with rate lambda."""
        fl = _check_number(lam, "expovariate() 'lambda'")
        if fl <= 0:
            interp._raise("expovariate() 'lambda' must be positive")
        return PulseNumber(random.expovariate(fl))
    
    def _triangular(low=None, high=None, mode=None) -> PulseNumber:
        """Triangular distribution."""
        fl = _check_number(low, "triangular() 'low'") if low is not None else 0.0
        fh = _check_number(high, "triangular() 'high'") if high is not None else 1.0
        fm = _check_number(mode, "triangular() 'mode'") if mode is not None else None
        return PulseNumber(random.triangular(fl, fh, fm))
    
    # Seed
    def _seed(s=None) -> PulseNull:
        """Seed the random number generator for reproducibility."""
        if s is None:
            random.seed()
        elif isinstance(s, PulseNumber):
            random.seed(int(s.value))
        elif isinstance(s, PulseString):
            random.seed(s.value)
        else:
            interp._raise(f"seed() argument must be a number or string, got '{s.type_name()}'")
        return PulseNull()
    
    def _get_state() -> PulseString:
        """Return the current RNG state as a string (for debugging)."""
        return PulseString(str(random.getstate()))
    
    # Range helpers
    def _randrange(start, stop=None, step=None) -> PulseNumber:
        """Return a random integer from range(start, stop, step)."""
        istart = _check_int(start, "randrange() 'start'")
        if stop is None:
            return PulseNumber(random.randrange(istart))
        istop = _check_int(stop, "randrange() 'stop'")
        if step is None:
            return PulseNumber(random.randrange(istart, istop))
        istep = _check_int(step, "randrange() 'step'")
        if istep == 0:
            interp._raise("randrange() 'step' cannot be zero")
        return PulseNumber(random.randrange(istart, istop, istep))
    
    
    return PulseModule("random", {
        "random": PulseNativeFunction("random", _random),
        "randint": PulseNativeFunction("randint", _random_int),
        "uniform": PulseNativeFunction("uniform", _uniform),
        "randrange": PulseNativeFunction("randrange", _randrange),
        "choice": PulseNativeFunction("choice", _choice),
        "choices": PulseNativeFunction("choices", _choices),
        "sample": PulseNativeFunction("sample", _sample),
        "shuffle": PulseNativeFunction("shuffle", _shuffle),
        "gauss": PulseNativeFunction("gauss", _gauss),
        "normalvariate": PulseNativeFunction("normalvariate", _normalvariate),
        "expovariate": PulseNativeFunction("expovariate", _expovariate),
        "triangular": PulseNativeFunction("triangular", _triangular),
        "seed": PulseNativeFunction("seed", _seed),
        "get_state": PulseNativeFunction("get_state", _get_state),
    })