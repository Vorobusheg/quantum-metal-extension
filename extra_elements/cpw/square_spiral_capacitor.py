# -*- coding: utf-8 -*-

"""File contains dictionary for SquareSpiralCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class SquareSpiralCapacitor(QComponent):
    """A square spiral capacitor with a specified overlap length heuristic and aspect ratio.

    Inherits `QComponent` class.

    Description:
        A square spiral capacitor.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * width: '4um' -- the width of the line of the spiral
        * gap: '4um' -- The distance between the two "plates" of the capacitor
        * length: '150um' -- A heuristic overlap length (Basically the total length of the outer spiral)
        * aspect: '0.5' -- Height:Width ratio of the external spiral
        * externalWidth: '50um' -- External Width
        * centered: 'False' -- center at (0.,0.) or the outer pins at (0.,0.)?
        * subtract: 'False'
        * helper: 'False'
    """

    default_options = Dict(width='4um',
                           length='150um',
                           gap='4um',
                           aspect='0.5',
                           externalWidth='50um',
                           centered='False',
                           subtract='False',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """An square spiral capacitor"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        length_left = p.length
        l = p.externalWidth
        h = l*float(p.aspect)
        diff = p.gap + p.width

        outer_spiral = [(0.,0.)]
        inner_spiral = [(diff, 0.)]

        while length_left > 0.:
            h_allowed = min(length_left, h)
            outer_spiral.append((outer_spiral[-1][0], outer_spiral[-1][1] + h_allowed))
            inner_spiral.append((inner_spiral[-1][0], outer_spiral[-1][1] - diff))
            length_left -= h_allowed
            if length_left <= 0.:
                inner_spiral[-1] = (inner_spiral[-1][0], inner_spiral[-1][1]+ diff)
                break

            l_allowed = min(length_left, l)
            outer_spiral.append((outer_spiral[-1][0] + l_allowed, outer_spiral[-1][1]))
            inner_spiral.append((outer_spiral[-1][0] - diff, inner_spiral[-1][1]))
            length_left -= l_allowed
            if length_left <= 0.:
                inner_spiral[-1] = (inner_spiral[-1][0] + diff, inner_spiral[-1][1])
                break

            l -= 2.*diff
            h -= 2.*diff

            if l <0. or h < 0.:
                break

            h_allowed = min(length_left, h)
            outer_spiral.append((outer_spiral[-1][0], outer_spiral[-1][1] - h_allowed))
            inner_spiral.append((inner_spiral[-1][0], outer_spiral[-1][1] + diff))
            length_left -= h_allowed
            if length_left <= 0.:
                inner_spiral[-1] = (inner_spiral[-1][0], inner_spiral[-1][1] - diff)
                break

            l_allowed = min(length_left, l)
            outer_spiral.append((outer_spiral[-1][0] - l_allowed, outer_spiral[-1][1]))
            inner_spiral.append((outer_spiral[-1][0] + diff, inner_spiral[-1][1]))
            length_left -= l_allowed
            if length_left <= 0.:
                inner_spiral[-1] = (inner_spiral[-1][0] - diff, inner_spiral[-1][1])
                break
            
            l -= 2.*diff
            h -= 2.*diff

            if l <0. or h < 0.:
                break


        outer_spiral = draw.LineString(outer_spiral)
        inner_spiral = draw.LineString(inner_spiral)

        outer_spiral = draw.rotate(outer_spiral, p.orientation, origin=(p.externalWidth, float(p.aspect)*p.externalWidth))
        outer_spiral = draw.translate(outer_spiral, p.pos_x, p.pos_y)

        inner_spiral = draw.rotate(inner_spiral, p.orientation, origin=(p.externalWidth, float(p.aspect)*p.externalWidth))
        inner_spiral = draw.translate(inner_spiral, p.pos_x, p.pos_y)

        if p.centered == "True":
            #print(bool(p.centered), p.centered)
            outer_spiral = draw.translate(outer_spiral, -p.externalWidth/2, -float(p.aspect)*p.externalWidth/2)
            inner_spiral = draw.translate(inner_spiral, -p.externalWidth/2, -float(p.aspect)*p.externalWidth/2)

        ##############################################
        # add qgeometry
        self.add_qgeometry('path', {'cap_outer': outer_spiral},
                           width=p.width,
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)

        self.add_qgeometry('path', {'cap_inner': inner_spiral},
                            width=p.width,
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        # FIX POINTS,
        self.add_pin('outerPin',
                     points=np.array(outer_spiral.coords)[:2],
                     width=p.width,
                     input_as_norm=True)
        self.add_pin('innerPin',
                     points=np.array(inner_spiral.coords)[:2],
                     width=p.width,
                     input_as_norm=True)