# -*- coding: utf-8 -*-

"""File contains dictionary for JunctionTopDown and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class JunctionChain(QComponent):
    """A Junction Chain for top down deposition.

    Inherits `QComponent` class.

    Description:
        A Junction Chain for top down deposition.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w: '1180nm' -- the width of the central rectangle
        * h: '1095nm' -- the height of the central rectangle
        * b: '20nm' -- Buffer around central rectangle
        * t: '130nm' -- Separation between two rectangles
        * bo: '180nm' -- Single layer removal on each side
        * h_offset: '4um' -- Junction offset from the center
        * h_total: '50um' -- Total Height
        * N_jxns: '200' -- Number of junctions (if not possible to accomodate these many, will throw an error)
        * layer_1: '2'
        * layer_2: '3'
        * helper: 'False'
    """

    default_options = Dict(w = '1180nm',
                           h = '1095nm',
                           b = '20nm',
                           t = '130nm',
                           bo = '180nm',
                           h_offset = '4um',
                           h_total = '50um',
                           N_jxns = '200',
                           layer_1 = '2',
                           layer_2 = '3',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A Junction Chain for top down deposition"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        h_per_jxn = p.h + 2*p.b + p.t
        p.N_jxns = int(p.N_jxns)
        h_tot_jxns = h_per_jxn*p.N_jxns
        if h_per_jxn*p.N_jxns > (p.h_total - p.h_offset):
            raise ValueError(f"Cannot accomodate these many jxns. Can accomodate at most {int((p.h_total - p.h_offset)/h_per_jxn)} jxns")

        box_jxn = draw.Polygon([(0.,0.),(0.,p.h),(p.w, p.h),(p.w,0)])
        box_jxn_buff = draw.translate(draw.Polygon([(-p.b,-p.b),(-p.b,p.h+p.b),(p.w+p.b, p.h+p.b),(p.w+p.b,-p.b)]), -p.w/2, -p.h/2)

        all_jxns_list = [draw.Polygon([(0.,0. + i*h_per_jxn),(0.,p.h+ i*h_per_jxn),(p.w, p.h+ i*h_per_jxn),(p.w,0+ i*h_per_jxn)]) for i in range(p.N_jxns)]
        all_jxns_buff_list = [draw.Polygon([(-p.b,-p.b+ i*h_per_jxn),(-p.b,p.h+p.b+ i*h_per_jxn),(p.w+p.b, p.h+p.b+ i*h_per_jxn),(p.w+p.b,-p.b+ i*h_per_jxn)]) for i in range(p.N_jxns)]

        h_boxup = p.h_total/2 - h_tot_jxns/2 - p.h_offset
        h_boxdown = p.h_total/2 - h_tot_jxns/2 + p.h_offset

        all_jxns_list = all_jxns_list + [draw.translate(draw.Polygon([(0.,0.),(0.,h_boxup),(p.w, h_boxup),(p.w,0)]), 0, h_tot_jxns),
                                         draw.translate(draw.Polygon([(0.,0.),(0.,h_boxdown),(p.w, h_boxdown),(p.w,0)]), 0, -(h_boxdown))]

        all_jxns_buff_list = all_jxns_buff_list + [
            draw.translate(draw.Polygon([(-p.b,-p.b),(-p.b,h_boxup),(p.w+p.b, h_boxup),(p.w+p.b,-p.b)]), 0, h_tot_jxns),
            draw.translate(draw.Polygon([(-p.b,0),(-p.b,h_boxdown+p.b),(p.w+p.b, h_boxdown+p.b),(p.w+p.b,0)]), 0, -(h_boxdown)),
        ]
        
        all_jxns = draw.translate(draw.union(all_jxns_list), -p.w/2, p.h_offset + p.h_total/2 - h_tot_jxns/2)
        all_jxns_buff = draw.translate(draw.union(all_jxns_buff_list), -p.w/2, p.h_offset+ p.h_total/2 - h_tot_jxns/2)

        # all_jxns = draw.translate(draw.MultiPolygon([((0.,0. + i*h_per_jxn),(0.,p.h+ i*h_per_jxn),(p.w, p.h+ i*h_per_jxn),(p.w,0+ i*h_per_jxn)) for i in range(p.N_jxns)]), -p.w/2, p.h_offset)
        # all_jxns_buff = draw.translate(draw.MultiPolygon([((-p.b,-p.b+ i*h_per_jxn),(-p.b,p.h+p.b+ i*h_per_jxn),(p.w+p.b, p.h+p.b+ i*h_per_jxn),(p.w+p.b,-p.b+ i*h_per_jxn),) for i in range(p.N_jxns)]), -p.w/2, p.h_offset)

        undercut_box = draw.translate(draw.Polygon([(-p.b-p.bo,0),(-p.b-p.bo,p.h_total),(p.w+p.b+p.bo, p.h_total),(p.w+p.b+p.bo,0)]), -p.w/2, 0)
        undercut_box = draw.subtract(undercut_box, all_jxns_buff)

        all_jxns = draw.translate(draw.rotate(all_jxns, p.orientation, origin=(0,0)), p.pos_x, p.pos_y)
        undercut_box = draw.translate(draw.rotate(undercut_box, p.orientation, origin=(0,0)), p.pos_x, p.pos_y)

        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'array_jxns': all_jxns},
                           helper=p.helper,
                           layer=p.layer_1,
                           chip=p.chip)
        self.add_qgeometry('poly', {'array_undercut': undercut_box},
                           helper=p.helper,
                           layer=p.layer_2,
                           chip=p.chip)