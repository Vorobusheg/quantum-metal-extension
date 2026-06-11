# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class RectangleFillet(QComponent):
    """A single configurable square.

    Inherits QComponent class.

    The class will add default_options class Dict to QComponent class before calling make.

    .. image::
        Rectangle.png

    .. meta::
        Rectangle

    Default Options:
        * width: '500um'
        * height: '300um'
        * subtract: 'False'
        * fillet: '0um'
        * helper: 'False'
    """

    default_options = Dict(width='500um',
                           height='300um',
                           subtract='False',
                           fillet='0um',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A single configurable square"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.

        # create the geometry
        rect = draw.rectangle(p.width, p.height, p.pos_x, p.pos_y).buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        rect = draw.rotate(rect, p.orientation)
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'rectangle': rect},
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)