# -*- coding: utf-8 -*-

"""File contains dictionary for JunctionTopDown and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class JunctionTopDown(QComponent):
    """A Junction for top down deposition.

    Inherits `QComponent` class.

    Description:
        A Junction for top down deposition.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w1: '200nm' -- the width of the bottom/side line
        * w2: '100nm' -- the width of the top line
        * l1: '5um' -- Length of the bottom/side line
        * l1_extra: '300nm' -- Extra length of bottom/side line
        * l2: '5um' -- Length of the top line
        * d_bridge: '180nm' -- Thickness of the bridge
        * t_extra: '30nm' -- Thickness of extra part of the top line
        * w_extra: '175nm' -- Width of the extra part electrode. 
        * w_conn: '2um' -- Width of the connecting pad
        * l_conn: '10um' -- length of connecting pads on each side
        * l_cut: '600nm' -- Extra distance on each side to make the cut
        * w_extra_2: 'None' -- If None, equal to w2, but usually you should make it such that you don't get an extra loop due to lack of overlap
        * pads_up: 'None' -- If None or 'LR', puts the extending pads on the left and right. If 'UD', puts the extending pads up and down
        * layer_1: '2'
        * layer_2: '3'
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
                           pads_up='None',
                           layer_jxn = '2',
                           layer_undercut = '3',
                           datatype_main='0',
                           datatype_undercut='0',
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
        if 'pads_up' not in self.options or p.pads_up == 'None':
            p.pads_up = 'LR'
        
        if p.w_extra_2 == 'None':
            p.w_extra_2 = p.w2

        if p.pads_up == 'LR':
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
        elif p.pads_up == 'UD':
            line_top = draw.union([
                draw.rectangle(p.w_conn, p.w1, 0., p.w1/2 + p.d_bridge/2),
                draw.rectangle(p.w_extra_2, p.l1, -p.w_conn/2 + p.w_extra_2/2, p.w1/2 + p.d_bridge/2 + p.l1/2),
            ])
            line_bottom = draw.union([
                draw.rectangle(p.w2 + 2*p.w_extra, p.t_extra, 0., -p.t_extra/2 - p.d_bridge/2),
                draw.rectangle(p.w2, p.l2, 0., - p.d_bridge/2 -p.l2/2),
            ])

            box = draw.rectangle(p.w_conn, p.l_conn, 0.,0.)
            box_u = draw.translate(box, 0., p.l_conn/2 + p.w1/2 + p.d_bridge/2 + p.l1)
            box_d = draw.translate(box, 0., -p.l_conn/2 - p.d_bridge/2 -p.l2)
            
            lines = draw.union([line_top, line_bottom])
            boxes = draw.union([box_u, box_d])
        else:
            raise ValueError('Bad input to pads_up')
        lines_and_box = draw.union([lines, boxes])
        # Create the cut region
        cut_region = draw.subtract(draw.union([lines.buffer(p.l_cut, cap_style=2, join_style=2), boxes.buffer(p.l_cut2, cap_style=2, join_style=2)]), lines_and_box.buffer(p.l_nocut, cap_style=2, join_style=2))

        polys = [lines_and_box, cut_region]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        if p.pads_up == 'LR':
            polys = draw.translate(polys, p.l_conn, 0.)
        [lines_and_box, cut_region] = polys

        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'lines_and_box': lines_and_box},
                           helper=p.helper,
                           layer=p.layer_jxn,
                           chip=p.chip,
                          datatype=0 if 'datatype_main' not in p else p.datatype_main)
        self.add_qgeometry('poly', {'cut_region': cut_region},
                           helper=p.helper,
                           layer=p.layer_undercut,
                           chip=p.chip,
                          datatype=0 if 'datatype_undercut' not in p else p.datatype_undercut)