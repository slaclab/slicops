"""Value in the UI

:copyright: Copyright (c) 2025 The Board of Trustees of the Leland Stanford Junior University, through SLAC National Accelerator Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy).  All Rights Reserved.
:license: http://github.com/slaclab/slicops/LICENSE
"""

from pykern import pkconfig, pkresource, pkyaml
from pykern.pkcollections import PKDict
from pykern.pkdebug import pkdc, pkdexc, pkdlog, pkdp
import pykern.pkinspect


class Base:

    def __init_subclass(cls, py_type, constraints=None, ui=None):
        cls.py_type = py_type
        cls.default_constraints = constraints
        cls.default_ui = ui
        n = cls.__name__
        if cls.__module__ != Base.__module__:
            n = f"{pykern.pkinspect.submodule_name(cls)}.{n}"
        if n in _registry:
            raise NameError("duplicate field class={n}")
        _registry[n] = cls

    def __init__(self, value):
        self.ui = copy.deepcopy(cls.default_ui)
        self.constraints = copy.deepcopy(cls.default_constraints)

    def new(self, value=None, constraints=None, ui=None):
        self.__class__(self.value)
        if ui:
            self.ui.pkupdate(ui)
        if constraints:
            self.constraints.pkupdate(constraints)

    def validate_value(self, value):
        # check constraints (min/max)
        return self.py_type(value)


how will py_type be used?

class Button(Base, py_type=str, ui=PKDict(widget="button")):
    pass


class Float(Base, py_type=float, ui=PKDict(widget="float")):
    pass


class Integer(Base, py_type=int, ui=PKDict(widget="integer")):
    pass


class Enum(Base, py_type=enum.Enum, ui=PKDict(widget="select")):
    pass


class String(Base, py_type=str, ui=PKDict(widget="text")):
    pass
