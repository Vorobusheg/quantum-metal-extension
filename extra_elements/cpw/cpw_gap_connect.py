# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class CPWGapConnect(QComponent):
    """A CPW Gap connect

    Inherits `QComponent` class.

    Description:
        A CPW gap connect

    Default Options:
        * cpw_width: '10um' -- The width of the 'cpw' terminating to ground
        * cpw_gap: '6um' -- The gap of the 'cpw'
        * cpw_length: '30um' -- The extra length of CPW to draw on each side
        * capacitor_gap: '2um' -- Gap for the capacitor. If larger than cpw_width, makes a direct gap capacitor, else makes a single finger capacitor
        * capacitor_length: '20um' -- Length of capacitor. If gap capacitor, this is the spacing, else is the overlap
    """

    default_options = Dict(cpw_width='10um',
                           cpw_gap='6um',
                           cpw_length='30um',
                           capacitor_gap='2um',
                           capacitor_length='20um',
                           fillet='2um',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """CPW gap connect"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        full_cpw_len = 2*p.cpw_length+p.capacitor_length+(0 if p.capacitor_gap>=p.cpw_width else p.capacitor_gap)
        cpw = draw.rectangle(full_cpw_len, p.cpw_width, full_cpw_len/2, 0.)
        cpw_box = draw.rectangle(full_cpw_len, p.cpw_width+2*p.cpw_gap, full_cpw_len/2, 0.)

        pin_in = draw.LineString([(full_cpw_len/2,0), (0,0)])
        pin_out = draw.LineString([(full_cpw_len/2,0), (full_cpw_len,0)])

        if p.capacitor_gap >= p.cpw_width:
            cap_etch = draw.rectangle(full_cpw_len, p.cpw_width, full_cpw_len/2, 0.)
        else:
            cap_etch = draw.LineString([(p.cpw_length, -p.cpw_width/2),
                                        (p.cpw_length, 0),
                                        (p.cpw_length+p.capacitor_length, 0),
                                        (p.cpw_length+p.capacitor_length, p.cpw_width/2),
                                       ]).buffer(p.capacitor_gap/2, cap_style='square', join_style='mitre')
            if 'fillet' in p:
                cap_etch = cap_etch.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        cpw = draw.subtract(cpw,cap_etch)
        
        polys = [cpw, cpw_box, pin_in, pin_out]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [cpw, cpw_box, pin_in, pin_out] = polys
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'cpw': cpw},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        self.add_qgeometry('poly', {'cpw_box': cpw_box},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                          subtract=True)
        # FIX POINTS,
        self.add_pin('in',
                     points=np.array(pin_in.coords),
                     width=p.cpw_width,
                     input_as_norm=True)
        self.add_pin('out',
                     points=np.array(pin_out.coords),
                     width=p.cpw_width,
                     input_as_norm=True)