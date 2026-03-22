"""
Custom exceptions for the EPA system
"""


class EPAException(Exception):
    """Base exception for EPA system"""

    pass


class LatticeException(EPAException):
    """Exception related to Ontological Lattice operations"""

    pass


class AssemblyException(EPAException):
    """Exception related to prompt assembly"""

    pass


class SafetyException(EPAException):
    """Exception related to safety validation"""

    pass


class TraceException(EPAException):
    """Exception related to traceability and audit trails"""

    pass
