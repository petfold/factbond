"""factbond: bonded assertions and information insurance for factual
claims. The first code (2026-09-19) is the assertion primitive's
consumer-facing edge — `contracts/Assertions.sol` and `factbond.assertions`;
the design lives in `docs/`."""

__version__ = "0.1.0"

from .assertions import AssertionsClient, BUCKETS, abi  # noqa: E402,F401

__all__ = ["AssertionsClient", "BUCKETS", "abi", "__version__"]
