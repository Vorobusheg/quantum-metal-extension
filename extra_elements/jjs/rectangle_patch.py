# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class RectanglePatch(QComponent):
    """A single configurable rectangle to be used as a patch.

    Inherits QComponent class.

    The class will add default_options class Dict to QComponent class before calling make.

    Default Options:
        * width: '500um'
        * height: '300um'
        * undercut: '500nm'
        * layer_patch : '2' -- Layer name for the rectangle patch
        * layer_undercut : '3' -- Layer name for the undercut
        * helper: 'False'
    """

    default_options = Dict(width='500um',
                           height='300um',
                           height_extra='-1um',
                           undercut='500nm',
                           layer_patch='2',
                           layer_undercut='3',
                           datatype_patch='0',
                           datatype_undercut='0',
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

        if(p.height_extra < 0): p.height_extra = p.height
        
        # create the geometry
        rect = draw.Polygon([(p.width/2, p.height/2), (p.width/2, -p.height/2), (-p.width/2, -p.height_extra/2), (-p.width/2, p.height_extra/2)])
        if 'fillet' in p:
            rect = rect.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        undercut = rect.buffer(p.undercut)

        polys = [rect, undercut]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        
        [rect, undercut] = polys
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'patch': rect},
                           helper=p.helper,
                           layer=p.layer_patch,
                           chip=p.chip,
                          datatype=0 if 'datatype_patch' not in p else p.datatype_patch)
        self.add_qgeometry('poly', {'undercut': undercut},
                           helper=p.helper,
                           layer=p.layer_undercut,
                           chip=p.chip,
                          datatype=0 if 'datatype_undercut' not in p else p.datatype_undercut)
        