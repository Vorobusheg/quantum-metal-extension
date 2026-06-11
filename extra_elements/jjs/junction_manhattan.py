# -*- coding: utf-8 -*-

"""File contains dictionary for JunctionTopDown and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class JunctionManhattan(QComponent):
    """A Manhattan Junction.

    Inherits `QComponent` class.

    Description:
        A Manhattan Junction.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w_line : '500nm' -- Width of line going towards the junction
        * w_undercut : '200nm' -- Width of the undercut
        * w_undercut_big: '1um' -- Bigger undercut around the larger pads and the ends of the junctions
        * width_jxn : '350nm' -- Width of the junction from the line coming from top (make sure that either both this and height are larger than w_line or both are smaller)
        * height_jxn : '350nm' -- Width of the junction from the line coming from the side (make sure that either both this and width are larger than w_line or both are smaller)
        * main_pad_width_top : '2um' -- Width of the pad on the top
        * main_pad_height_top : '2um' -- Height of the pad on the top
        * main_pad_width_side : '2um' -- Width of the pad on the side
        * main_pad_height_side : '2um' -- Height of the pad on the side
        * main_pad_offset_height_side: '0um' -- Height offset of the top main_pad from the jxn
        * l_line_top : '4um' -- Length from the center of the top pad to the center of the junction
        * l_line_side : '4um' -- Length from the center of the side pad to the center of the junction. Also sets the offset of the side pad
        * side_side : 'left' -- Side of the side pad. Can be left or right
        * l_jxn_extra : '1um' -- Extra length of the junction wire (towards and away from respective pad) if the junction is thin (w_line > width_jxn)
        * layer_jxn : '2' -- Layer name for the junction
        * layer_undercut : '3' -- Layer name for the undercut
        * helper: 'False'
    """

    default_options = Dict(
        w_line = '500nm',
        w_undercut = '200nm',
        w_undercut_big = '1um',
        width_jxn = '350nm',
        height_jxn = '350nm',
        main_pad_width_top = '2um',
        main_pad_height_top = '2um',
        main_pad_width_side = '2um',
        main_pad_height_side = '2um',
        main_pad_offset_height_side = '0um',
        l_line_top = '4um',
        l_line_side = '4um',
        side_side = 'left',
        l_jxn_extra = '1um',
        layer_jxn = '2',
        layer_undercut = '3',
        datatype_main='0',
        datatype_undercut='0',
        helper = 'False'
    )
    """Default drawing options"""

    TOOLTIP = """A Manhattan Junction"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.

        # for x in p:
        #     print(f'{x}={p[x]}')

        pad_top = draw.rectangle(p.main_pad_width_top, p.main_pad_height_top, 0, 0)
        pad_side = draw.rectangle(p.main_pad_width_side, p.main_pad_height_side, -p.l_line_side, -p.l_line_top - p.main_pad_offset_height_side)

        if 'pad_fillet' in p:
            pad_top = pad_top.buffer(p.pad_fillet).buffer(-p.pad_fillet).buffer(-p.pad_fillet).buffer(p.pad_fillet)
            pad_side = pad_side.buffer(p.pad_fillet).buffer(-p.pad_fillet).buffer(-p.pad_fillet).buffer(p.pad_fillet)

        jxn_undercut_big = draw.union([pad_top, pad_side])

        if p.width_jxn <= p.w_line and p.height_jxn <= p.w_line:
            top_line = draw.rectangle(p.w_line, p.l_line_top - (p.height_jxn+p.l_jxn_extra)/2, 0, -(p.l_line_top - (p.height_jxn+p.l_jxn_extra)/2)/2)
            side_line = draw.rectangle(p.l_line_side - (p.width_jxn+p.l_jxn_extra)/2, p.w_line,
                                       -p.l_line_side/2 - (p.width_jxn+2*p.l_jxn_extra)/4, -p.l_line_top)
            jxn_top_line = draw.rectangle(p.width_jxn, p.height_jxn+2*p.l_jxn_extra, 0, -p.l_line_top)
            jxn_side_line = draw.rectangle(p.width_jxn+2*p.l_jxn_extra, p.height_jxn, 0, -p.l_line_top)

            top_line_full = draw.union([top_line, jxn_top_line])
            side_line_full = draw.union([side_line, jxn_side_line])

            jxn_top_line_for_undercut = draw.rectangle(p.width_jxn, p.height_jxn+2*p.l_jxn_extra+2*p.w_undercut_big, 0, -p.l_line_top)
            jxn_side_line_for_undercut = draw.rectangle(p.width_jxn+2*p.l_jxn_extra+2*p.w_undercut_big, p.height_jxn, 0, -p.l_line_top)

            top_line_full_uc = draw.union([top_line, jxn_top_line_for_undercut])
            side_line_full_uc = draw.union([side_line, jxn_side_line_for_undercut])

            if 'fillet' in p:
                top_line_full = top_line_full.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
                side_line_full = side_line_full.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)

            full_jxn = draw.union([pad_top, pad_side, top_line_full, side_line_full])

            jxn_undercut_small =  draw.union([top_line_full_uc, side_line_full_uc])
            
        elif p.width_jxn > p.w_line and p.height_jxn > p.w_line:
            top_line = draw.rectangle(p.w_line, p.l_line_top - (p.height_jxn)/2, 0, -(p.l_line_top - (p.height_jxn)/2)/2)
            side_line = draw.rectangle(p.l_line_side - (p.width_jxn)/2, p.w_line,
                                       -p.l_line_side/2 - (p.width_jxn)/4, -p.l_line_top)
            
            jxn_box = draw.rectangle(p.width_jxn, p.height_jxn, 0, -p.l_line_top)

            # if 'fillet' in p:
            #     top_line_full = top_line_full.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
            #     side_line_full = side_line_full.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)

            full_jxn = draw.union([pad_top, pad_side, top_line, side_line, jxn_box])

            jxn_undercut_big = draw.union([jxn_undercut_big, jxn_box])
            jxn_undercut_small =  draw.union([top_line, side_line])
        else:
            raise ValueError('Make sure that either both width_jxn and height_jxn are larger than w_line or both are smaller')

        jxn_undercut_big = jxn_undercut_big.buffer(p.w_undercut_big-p.w_undercut)
        jxn_undercut = draw.union([jxn_undercut_big, jxn_undercut_small]).buffer(p.w_undercut)
        
        if p.side_side.lower() == 'left':
            pass
        if p.side_side.lower() == 'right':
            full_jxn = draw.scale(full_jxn, xfact = -1, origin=(0,0,))
            jxn_undercut = draw.scale(jxn_undercut, xfact = -1, origin=(0,0,))

        jxn_undercut = draw.subtract(jxn_undercut, full_jxn)
        
        polys = [full_jxn, jxn_undercut]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [full_jxn, jxn_undercut] = polys
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'jxn': full_jxn},
                           helper=p.helper,
                           layer=p.layer_jxn,
                           chip=p.chip,
                           datatype=0 if 'datatype_main' not in p else p.datatype_main)
        self.add_qgeometry('poly', {'undercut': jxn_undercut},
                           helper=p.helper,
                           layer=p.layer_undercut,
                           chip=p.chip,
                          datatype=0 if 'datatype_undercut' not in p else p.datatype_undercut)