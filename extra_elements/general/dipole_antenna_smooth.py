# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class DipoleAntennaSmooth(QComponent):
    """Dipole Antenna

    Inherits `QComponent` class.

    Description:
       Dipole Antenna.

    Default Options:
        * width: '2um' -- The width of antenna
        * length: '100um' -- Length of antenna
        * pad_width: '10um' -- Width of the pad
        * fillet: '2um' -- The length of dielectric from the end of the cpw center trace to the ground.
    """

    default_options = Dict(width= '2um',
                           length= '100um',
                           fillet= '2um',
                           pad_width= '10um',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """Dipole Antenna"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry
        
        box = draw.rectangle(p.length, p.width, p.length/2, 0)
        box_bottom = draw.rectangle(p.length/2, p.width, p.length/4, 0)
        pad = draw.rectangle(p.pad_width, p.pad_width, p.length, 0).buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)

        box_pad = box.union(pad).buffer(p.fillet).buffer(-p.fillet).buffer(-p.width*0.45).buffer(p.width*0.45).union(box)

        box_pad = draw.translate(draw.rotate(box_pad, p.orientation, origin=(0,0)), p.pos_x, p.pos_y)
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'antenna': box_pad},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)