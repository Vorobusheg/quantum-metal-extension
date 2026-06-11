# -*- coding: utf-8 -*-

"""File contains dictionary for JunctionTopDown and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class JunctionManhattan(QComponent):
    """A Manhattan Junction for xmon with optional patching.

    Inherits `QComponent` class.

    Description:
        A Manhattan Junction for xmon with optional patching.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w_line : '500nm' -- Width of line going towards the junction
        * w_undercut : '200nm' -- Width of the undercut
        * width_jxn : '350nm' -- Width of the junction from the line coming from top
        * height_jxn : '350nm' -- Width of the junction from the line coming from the side
        * main_pad_size_top : '2um' -- Size of the pad on the top
        * main_pad_size_side : '2um' -- Size of the pad on the side
        * helper: 'False'
    """

    default_options = Dict(w1='200nm',
                           w2='100nm',
                           l1='3um',
                           l1_extra='300nm',
                           l2='3um',
                           d_bridge='180nm',
                           t_extra='30nm',
                           w_extra='175nm',
                           w_conn='2um',
                           l_conn='10um',
                           l_cut='600nm',
                           l_nocut='25nm',
                           l_cut2='200nm',
                           w_extra_2='None',
                           layer_1='2',
                           layer_2='3',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A Junction for top down deposition"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        h2 = p.w1 + p.d_bridge
        
        if p.w_extra_2 == 'None':
            p.w_extra_2 = p.w2

        # Creating the boxes first
        box = draw.Polygon([(0.,0.),(0.,p.w_conn),(p.l_conn, p.w_conn),(p.l_conn,0),(0,0)])
        box_l = draw.translate(box, -p.l_conn,0)
        box_r = draw.translate(box, p.l1+p.l2,0)

        #Creating the lines
        line_bottom = draw.Polygon([(0,0),(0,p.w1),(-p.l1-p.l1_extra,p.w1),(-p.l1-p.l1_extra,0),(0,0)])
        line_bottom = draw.translate(line_bottom, p.l1+p.l2,0)

        line_top = draw.Polygon([(0,p.w_conn), (p.l2 + p.w2, p.w_conn),
                                 (p.l2 + p.w2, h2 + p.t_extra), (p.l2 + p.w2 + p.w_extra, h2 + p.t_extra),
                                 (p.l2 + p.w2 + p.w_extra, h2), (p.l2 - p.w_extra, h2),
                                 (p.l2 - p.w_extra, h2 + p.t_extra), (p.l2, h2 + p.t_extra),
                                 (p.l2, p.w_conn - p.w_extra_2), (0, p.w_conn - p.w_extra_2), (0, p.w_conn)])

        lines = draw.union([line_bottom, line_top])
        boxes = draw.union([box_l, box_r])
        lines_and_box = draw.union([lines, boxes])
        # Create the cut region
        cut_region = draw.subtract(draw.union([lines.buffer(p.l_cut, cap_style=2, join_style=2), boxes.buffer(p.l_cut2, cap_style=2, join_style=2)]), lines_and_box.buffer(p.l_nocut, cap_style=2, join_style=2))

        lines_and_box = draw.translate(lines_and_box, p.pos_x+p.l_conn, p.pos_y)
        cut_region = draw.translate(cut_region, p.pos_x+p.l_conn, p.pos_y)

        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'lines_and_box': lines_and_box},
                           helper=p.helper,
                           layer=p.layer_1,
                           chip=p.chip)
        self.add_qgeometry('poly', {'cut_region': cut_region},
                           helper=p.helper,
                           layer=p.layer_2,
                           chip=p.chip)