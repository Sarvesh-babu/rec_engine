"""Retail industry pack: schema extensions and feature/result-type rules.

No industry-specific assumptions live outside this package — the core
pipeline only calls into packs through the registry interface.
"""
from .pack import RetailPack

PACK = RetailPack()
