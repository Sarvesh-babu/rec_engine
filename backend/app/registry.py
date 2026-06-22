"""Module registry: maps an industry name to its loaded pack.

Adding a new vertical means adding one entry here -- the core pipeline
never branches on industry name directly.
"""
from app.industry_packs.retail import PACK as RETAIL_PACK

_REGISTRY = {
    "retail": RETAIL_PACK,
}


def get_pack(industry: str):
    try:
        return _REGISTRY[industry]
    except KeyError:
        raise ValueError(f"Unknown industry '{industry}'. Available: {list(_REGISTRY)}")


def available_industries() -> list[str]:
    return list(_REGISTRY)
