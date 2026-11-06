# -*- coding: utf-8 -*-
"""JunctionManhattanBigFixed: a Manhattan Josephson junction with its undercut."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class JunctionManhattan(QComponent):
    """A Manhattan junction: two pads joined by two perpendicular lines, with an undercut.

    Inherits `QComponent` class.

    Description:
        A top pad and a side pad are joined by two perpendicular lines, ``w_line`` wide.
        The top line goes down from the top pad; the side line goes from the side pad
        towards it. The junction is where the two lines cross, at (0, -l_line_top)
        relative to the centre of the top pad. Its size is ``width_jxn`` along x and
        ``height_jxn`` along y. Two shapes are made:

        * ``jxn`` (layer ``layer_jxn``): pads, lines and junction, as one polygon
        * ``undercut`` (layer ``layer_undercut``): the undercut around ``jxn``, without
          ``jxn`` itself

        The origin of the component (``pos_x``, ``pos_y``) is the centre of the top pad,
        and ``orientation`` rotates the component around it. The positions below are
        given before this rotation, for ``side_side='left'``; ``side_side='right'``
        mirrors everything in x.

    Thin junction (width_jxn <= w_line and height_jxn <= w_line):
        Near the crossing each line becomes a thin finger:

        * the top line ends at y = -l_line_top + (height_jxn + l_jxn_extra)/2 and continues
          as a finger ``width_jxn`` wide;
        * the side line ends at x = -(width_jxn + l_jxn_extra)/2 - l_jxn_extra/4 and
          continues as a finger ``height_jxn`` high.

        The two fingers cross in a ``width_jxn`` x ``height_jxn`` overlap (the junction), and
        each finger goes ``l_jxn_extra`` past the other one.

    Big junction (width_jxn > w_line and height_jxn > w_line), box shift:
        The junction is a box, ``width_jxn`` x ``height_jxn``, at the crossing of the lines.
        The box is not centred on the crossing: its lower right corner is on the lower right
        corner of the crossing, (w_line/2, -l_line_top - w_line/2). As a result:

        * the right edge of the box continues the right edge of the top line, and the
          bottom edge of the box continues the bottom edge of the side line, so these
          outer edges stay straight;
        * the box grows only up and to the left, towards the pads;
        * compared with a box centred on the crossing, the centre of the box moves by
          dx = -(width_jxn - w_line)/2 and dy = +(height_jxn - w_line)/2, to
          (-(width_jxn - w_line)/2, -l_line_top + (height_jxn - w_line)/2);
        * the lines end where they would end at a centred box (the top line at
          y = -l_line_top + height_jxn/2, the side line at x = -width_jxn/2), so they go
          (height_jxn - w_line)/2 and (width_jxn - w_line)/2 into the box. The area of
          ``jxn`` is therefore w_line * ((width_jxn - w_line)/2 + (height_jxn - w_line)/2)
          smaller than with a centred box.

    Sketch:
        Big junction, side_side='left' (not to scale)
        ::

                                +-----------+
                                |  top pad  |
                                |     o     |     o: origin = (pos_x, pos_y)
                                +----+  +---+
                                     |  |         top line, w_line wide
                           +---------+  |   --
                           |            |    ^
                           |    box     |    |  height_jxn
                           |            |    |
             +-------+     |            |    |
             |  side +-----+          x |    |    x: line crossing, (0, -l_line_top)
             |  pad  +------------------+   --
             +-------+     <------------>
                              width_jxn

        The right edge of the box is in line with the right edge of the top line, and the
        bottom edge of the box is in line with the bottom edge of the side line.

    Undercut:
        The undercut is ``w_undercut_big`` wide around the pads and around the box of a big
        junction, and ``w_undercut`` wide around the lines and the fingers. For a thin
        junction the fingers are first made ``w_undercut_big`` longer at both ends, so the
        undercut reaches ``w_undercut_big + w_undercut`` past the finger ends. The corners of
        the undercut are round, and ``jxn`` is cut out of it.

    .. meta::
        :description: Manhattan junction with undercut

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w_line: '500nm' -- Width of the two lines from the pads to the junction
        * w_undercut: '200nm' -- Width of the undercut around the lines and the fingers
        * w_undercut_big: '1um' -- Width of the undercut around the pads and the big box;
          for a thin junction, also how far the undercut goes past the finger ends
          (plus w_undercut)
        * width_jxn: '350nm' -- Junction size along x: width of the top finger (thin
          junction) or of the box (big junction)
        * height_jxn: '350nm' -- Junction size along y: height of the side finger (thin
          junction) or of the box (big junction). width_jxn and height_jxn must be both
          <= w_line (thin junction) or both > w_line (big junction)
        * main_pad_width_top: '2um' -- Width of the top pad
        * main_pad_height_top: '2um' -- Height of the top pad
        * main_pad_width_side: '2um' -- Width of the side pad
        * main_pad_height_side: '2um' -- Height of the side pad
        * main_pad_offset_height_side: '0um' -- Moves the side pad down: its centre is at
          y = -l_line_top - main_pad_offset_height_side; the side line stays at y = -l_line_top
        * l_line_top: '4um' -- Distance from the centre of the top pad to the junction, along y
        * l_line_side: '4um' -- Distance from the centre of the side pad to the junction, along x
        * side_side: 'left' -- Side of the side pad: 'left' or 'right'
        * l_jxn_extra: '1um' -- Thin junction: how far each finger goes past the other one
        * pad_fillet: '0um' -- Radius to round the corners of the pads; 0: square corners
        * fillet: '0um' -- Thin junction: radius to round the corners of the lines and
          fingers; 0: square corners
        * layer_jxn: '2' -- Layer of the junction (pads, lines and junction)
        * layer_undercut: '3' -- Layer of the undercut
        * datatype_main: '0' -- Datatype stored with the junction shape
        * datatype_undercut: '0' -- Datatype stored with the undercut shape
        * helper: 'False' -- Make both shapes helper shapes
    """

    default_options = Dict(
        w_line='500nm',
        w_undercut='200nm',
        w_undercut_big='1um',
        width_jxn='350nm',
        height_jxn='350nm',
        main_pad_width_top='2um',
        main_pad_height_top='2um',
        main_pad_width_side='2um',
        main_pad_height_side='2um',
        main_pad_offset_height_side='0um',
        l_line_top='4um',
        l_line_side='4um',
        side_side='left',
        l_jxn_extra='1um',
        pad_fillet='0um',
        fillet='0um',
        layer_jxn='2',
        layer_undercut='3',
        datatype_main='0',
        datatype_undercut='0',
        helper='False')
    """Default drawing options"""

    TOOLTIP = """A Manhattan junction with its undercut"""

    def make(self):
        """Convert the options into the junction and undercut polygons."""
        p = self.p
        w, wx, hy = p.w_line, p.width_jxn, p.height_jxn          # line width, junction size
        lt, ls, e = p.l_line_top, p.l_line_side, p.l_jxn_extra
        side = str(p.side_side).lower()
        if side not in ('left', 'right'):
            raise ValueError(f"side_side must be 'left' or 'right', not {p.side_side!r}")

        pad_top = draw.rectangle(p.main_pad_width_top, p.main_pad_height_top, 0, 0)
        pad_side = draw.rectangle(p.main_pad_width_side, p.main_pad_height_side,
                                  -ls, -lt - p.main_pad_offset_height_side)
        if p.pad_fillet > 0:                                      # round all corners, inner and outer
            r = p.pad_fillet
            pad_top, pad_side = [s.buffer(r).buffer(-r).buffer(-r).buffer(r) for s in (pad_top, pad_side)]
        pads = draw.union([pad_top, pad_side])

        if wx <= w and hy <= w:
            # thin junction: wide lines, then crossing fingers that go l_jxn_extra past each other
            top_line = draw.rectangle(w, lt - (hy + e) / 2, 0, -(lt - (hy + e) / 2) / 2)
            side_line = draw.rectangle(ls - (wx + e) / 2, w, -ls / 2 - (wx + 2 * e) / 4, -lt)
            top = draw.union([top_line, draw.rectangle(wx, hy + 2 * e, 0, -lt)])
            side_ = draw.union([side_line, draw.rectangle(wx + 2 * e, hy, 0, -lt)])
            under_big = pads
            under_small = draw.union([                            # fingers w_undercut_big longer
                top_line, draw.rectangle(wx, hy + 2 * e + 2 * p.w_undercut_big, 0, -lt),
                side_line, draw.rectangle(wx + 2 * e + 2 * p.w_undercut_big, hy, 0, -lt)])
            if p.fillet > 0:                                      # round all corners, inner and outer
                r = p.fillet
                top, side_ = [s.buffer(r).buffer(-r).buffer(-r).buffer(r) for s in (top, side_)]
            jxn = draw.union([pads, top, side_])
        elif wx > w and hy > w:
            # big junction: box with its lower right corner on that of the line crossing
            top_line = draw.rectangle(w, lt - hy / 2, 0, -(lt - hy / 2) / 2)
            side_line = draw.rectangle(ls - wx / 2, w, -ls / 2 - wx / 4, -lt)
            box = draw.rectangle(wx, hy, -(wx - w) / 2, -lt + (hy - w) / 2)
            under_big = draw.union([pads, box])
            under_small = draw.union([top_line, side_line])
            jxn = draw.union([pads, top_line, side_line, box])
        else:
            raise ValueError('Make sure that either both width_jxn and height_jxn are larger '
                             'than w_line or both are smaller')

        under = draw.union([under_big.buffer(p.w_undercut_big - p.w_undercut), under_small])
        under = under.buffer(p.w_undercut)
        if side == 'right':
            jxn, under = draw.scale([jxn, under], xfact=-1, origin=(0, 0))
        under = draw.subtract(under, jxn)

        jxn, under = draw.translate(draw.rotate([jxn, under], p.orientation, origin=(0, 0)),
                                    p.pos_x, p.pos_y)
        self.add_qgeometry('poly', {'jxn': jxn}, helper=p.helper, layer=p.layer_jxn,
                           chip=p.chip, datatype=p.datatype_main)
        self.add_qgeometry('poly', {'undercut': under}, helper=p.helper, layer=p.layer_undercut,
                           chip=p.chip, datatype=p.datatype_undercut)