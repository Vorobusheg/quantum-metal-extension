# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class CpwClawExtraGround(QComponent):
    """A CPW with a claw and extra ground drawn with it

    Inherits `QComponent` class.

    Description:
        A CPW with a claw and extra ground drawn with it.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um') Also, the position and orientation would be made wrt the end of the cpw, not the claw or the center

        * cpw_width: 'cpw_width' -- width of CPW
        * cpw_gap: 'cpw_gap' -- gap of CPW
        * extra_ground_side: '50um' -- Extra ground plane drawn on each side
        * length_cpw: '200um' -- Extra length of CPW after the claw
        * h_claw: '100um' -- Height of the claw
        * d_claw: '30um' -- Depth of the claw, i.e. how much it protrudes out
        * thickness_claw: '5um' -- Thickness of the claw
        * fillet: '0' -- Fillet to be used
        * helper: 'False'
    """

    default_options = Dict(cpw_width='cpw_width',
                           cpw_gap='cpw_gap',
                           extra_ground_side='50um',
                           length_cpw='200um',
                           h_claw='100um',
                           d_claw='30um',
                           thickness_claw='5um',
                           fillet='0um',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """CPW Claw connector"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        extra_gnd_rect = draw.rectangle(p.length_cpw, 2*(p.cpw_gap + p.extra_ground_side) + p.cpw_width,
                                   p.length_cpw/2, 0)
        cpw_gap_rect = draw.rectangle(p.length_cpw, 2*p.cpw_gap + p.cpw_width,
                                   p.length_cpw/2, 0)
        cpw_main_rect = draw.rectangle(p.length_cpw + p.cpw_gap, p.cpw_width,
                                   p.length_cpw/2 + p.cpw_gap/2, 0)
        cpw_plus_ground = draw.union([draw.subtract(extra_gnd_rect, cpw_gap_rect), cpw_main_rect])

        claw_poly = draw.Polygon([(0,p.h_claw/2 + p.thickness_claw),
                                  (p.d_claw + p.thickness_claw,p.h_claw/2 + p.thickness_claw),
                                  (p.d_claw + p.thickness_claw,p.h_claw/2),
                                  (p.thickness_claw,p.h_claw/2),
                                  (p.thickness_claw,-p.h_claw/2),
                                  (p.thickness_claw + p.d_claw, -p.h_claw/2),
                                  (p.thickness_claw + p.d_claw, -p.h_claw/2 - p.thickness_claw),
                                  (0, -p.h_claw/2 - p.thickness_claw),
                                  (0,p.h_claw/2 + p.thickness_claw),
                                 ])
        claw_poly = draw.translate(claw_poly, p.length_cpw + p.cpw_gap)
        
        cpw_with_claw = draw.union([cpw_plus_ground, claw_poly])
        cpw_with_claw = cpw_with_claw.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)

        extra_gnd_rect_fix = draw.rectangle(p.length_cpw/2, 2*(p.cpw_gap + p.extra_ground_side) + p.cpw_width,
                                   p.length_cpw/4, 0)
        cpw_with_claw = cpw_with_claw.union(extra_gnd_rect_fix.intersection(cpw_plus_ground))
        
        cpw_with_claw = draw.rotate(cpw_with_claw, p.orientation, origin=(0,0))
        cpw_with_claw = draw.translate(cpw_with_claw, p.pos_x, p.pos_y)

        cpw_main_rect_rot_trans = draw.rotate(cpw_main_rect, p.orientation, origin=(0,0))
        cpw_main_rect_rot_trans = draw.translate(cpw_main_rect_rot_trans, p.pos_x, p.pos_y)

        pin_coords = [list(list(cpw_main_rect_rot_trans.exterior.coords)[-1]), list(list(cpw_main_rect_rot_trans.exterior.coords)[-2])]
        # print(list(cpw_main_rect_rot_trans.exterior.coords))
        # print(pin_coords, len(pin_coords))
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'cpw_with_claw': cpw_with_claw},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        # FIX POINTS,
        self.add_pin('reso_in',
                     points=np.array(pin_coords),
                     width=p.cpw_width,
                     input_as_norm=False)