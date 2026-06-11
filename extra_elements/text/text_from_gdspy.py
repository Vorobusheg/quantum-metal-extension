# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np
from .fontpolylist import _font

## The polygons and some of the code here are copied from GDSPy code completely and utterly, so that is where the copyright of this part of the code lies

class Text(QComponent):
    """Text writing

    Inherits QComponent class.

    The class will add default_options class Dict to QComponent class before calling make.

    Default Options:
        * 'text_write': Text to be written
        * 'fontsize': Size of the font in um, maybe slightly arbitrary
        * helper: 'False'
    """

    default_options = Dict(text_write = '',
                           fontsize = '50um',
                           helper='False',
                          subtract='True')
    """Default drawing options"""

    TOOLTIP = """A single configurable square"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.

        # create the geometry
        all_polys = []
        multfactor = p.fontsize/9

        posX = 0
        posY = 0

        text_write = self.options.text_write

        for idx_char in range(len(text_write)):
            if text_write[idx_char] == "\n":
                posY -= 11
                posX = 0
            elif text_write[idx_char] == "\t":
                posX = posX + 32 - (posX + 8) % 32
            elif text_write[idx_char] == " ":
                posX = posX + 8
            else:
                if text_write[idx_char] in _font:
                    for pl in _font[text_write[idx_char]]:
                        polygon = pl[:]
                        for ii in range(len(polygon)):
                            xp = (posX + polygon[ii][0])
                            yp = (posY + polygon[ii][1])
                            polygon[ii] = (xp, yp)
                        all_polys.append(draw.Polygon(polygon))
                
                    posX += 8
        all_polys = draw.union(all_polys)
        all_polys = draw.translate(all_polys, -4.*len(text_write), 0.)
        all_polys = draw.scale(all_polys, xfact = multfactor, yfact=multfactor, origin=(0,0))
        all_polys = draw.rotate(all_polys, p.orientation, origin=(0,0))
        all_polys = draw.translate(all_polys, p.pos_x, p.pos_y)
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'text_write': all_polys},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                           subtract=p.subtract,
                          datatype=10)