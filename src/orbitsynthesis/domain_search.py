"""Public obstruction-guided domain-search API.

The semantic rule compiler, object reference search, and bit-parallel
refinement live in separate modules so exactness and optimization can be
audited independently.
"""
from .domain_search_types import (
    DomainNogood, DomainSearchResult, DomainSearchStats, PointedClassRules,
    SeedRule,
)
from .domain_search_object import CompiledNogoodDomainSearch, maximal_domains_nogood
from .domain_search_bitset import BitsetNogoodDomainSearch, maximal_domains_bitset_nogood

__all__ = [
    "BitsetNogoodDomainSearch",
    "CompiledNogoodDomainSearch",
    "DomainNogood",
    "DomainSearchResult",
    "DomainSearchStats",
    "PointedClassRules",
    "SeedRule",
    "maximal_domains_bitset_nogood",
    "maximal_domains_nogood",
]
