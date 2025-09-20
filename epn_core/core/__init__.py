"""Core package for EPN.

This package intentionally avoids importing implementation modules at
package import time to prevent circular import problems during test
collection. Import specific modules directly when needed, e.g.:

    from epn_core.core.node import NodeConfig

"""

__all__ = [
    'node',
    'layer',
    'pipeline',
    'nodes',
    'factory',
]
