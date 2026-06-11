# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class CpwCoupPinFillet(QComponent):
    """A CPW pin with a single side fillet

    Inherits `QComponent` class.

    Description:
        A CPW pin with a single side fillet.

    Default Options:
        * width: '10um' -- The width of the 'cpw' terminating to ground
        * gap: '6um' -- The gap of the 'cpw'
        * fillet: '6um' -- The length of dielectric from the end of the cpw center trace to the ground.
        * cpw_length: '30um' -- The extra length of CPW to draw
    """

    default_options = Dict(width= '10um',
                           gap= '6um',
                           fillet= '6um',
                           cpw_length= '30um',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """CPW fillet pin"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry
        fillet_gap = p.fillet*(p.gap*2 + p.width)/p.width
        
        gap_box = draw.rectangle(p.cpw_length + p.gap, p.width+2*p.gap,
                                (p.cpw_length + p.gap)/2, 0)
        gap_box_bottom = draw.rectangle(p.cpw_length/2, p.width+2*p.gap,
                                p.cpw_length/4, 0)
        cpw_box = draw.rectangle(p.cpw_length, p.width,
                                p.cpw_length/2, 0)
        cpw_box_bottom = draw.rectangle(p.gap, p.width,
                                p.gap/2, 0)
        
        cpw_box_fillet = cpw_box.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        cpw_box_fillet = cpw_box_fillet.union(cpw_box_bottom)
        
        gap_box_fillet = gap_box.buffer(fillet_gap).buffer(-fillet_gap).buffer(-fillet_gap).buffer(fillet_gap)
        gap_box_fillet = gap_box_fillet.union(gap_box_bottom)
        
        cpw_box_fillet = draw.translate(draw.rotate(cpw_box_fillet,p.orientation, origin=(0,0)),p.pos_x, p.pos_y)
        gap_box_fillet = draw.translate(draw.rotate(gap_box_fillet,p.orientation, origin=(0,0)),p.pos_x, p.pos_y)

        gap_box_rot_trans = draw.translate(draw.rotate(gap_box,p.orientation, origin=(0,0)),p.pos_x, p.pos_y)
        
        pin_coords = [list(list(gap_box_rot_trans.exterior.coords)[-1]), list(list(gap_box_rot_trans.exterior.coords)[-2])]
        # print(list(cpw_main_rect_rot_trans.exterior.coords))
        # print(pin_coords, len(pin_coords))
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'trace_pin': cpw_box_fillet},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        self.add_qgeometry('poly', {'gap_pin': gap_box_fillet},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                          subtract=True)
        # FIX POINTS,
        self.add_pin('in',
                     points=np.array(pin_coords),
                     width=p.width,
                     input_as_norm=False)