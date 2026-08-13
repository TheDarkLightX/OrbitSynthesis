"""Public parameter-core synthesis API.

The implementation is split into closure, pointed-kernel, and frontier modules
so each proof/algorithm layer can be audited independently.
"""
from .parameter_closure import (
    ParameterCoreInfo, closure_with_parameters, eligible_core_isomorphisms,
    generated_at_observation, parameter_core, parameter_core_catalog,
)
from .pointed_kernel import (
    CompiledParameterizedKernel, PointedClass, maximal_domains_for_allowed_parameters,
    naive_local_domain_feasible, parameterized_strategy_for_allowed_parameters,
    parameterized_strategy_pointed, parameterized_strategy_reference, pointed_classes,
)
from .parameter_frontier import (
    ParameterDomainFrontier, ParameterDomainPoint, maximal_parameterized_domains,
    minimum_parameter_solutions, parameter_budget_frontier, parameter_domain_frontier,
)
__all__ = [name for name in globals() if not name.startswith('_')]
