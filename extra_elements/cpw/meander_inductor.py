# -*- coding: utf-8 -*-

"""File contains dictionary for MeanderInductor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class MeanderInductor(QComponent):
    """A Meandering Inductor with a specified overlap length heuristic and height.

    Inherits `QComponent` class.

    Description:
        A meandering inductor.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * width: '4um' -- the width of the line
        * gap: '4um' -- The separation between the two turns
        * length: '1500um' -- A heuristic overlap length (Basically the total length of the inductor strip)
        * height: '300um' -- Height approximated to the closest conforming length <= the provided one
        * centered: 'False' -- center at (0.,0.) or lower bottom pin at (0.,0.)?
        * subtract: 'False'
        * helper: 'False'
    """

    default_options = Dict(width='4um',
                           length='1500um',
                           gap='4um',
                           height='300um',
                           centered='False',
                           subtract='False',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A meandering inductor"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        length_left = p.length
        diff = p.gap + p.width
        n_turns = int(p.height/(2.*diff))
        l = (length_left-diff)/(2*n_turns+1)

        height = 2.*diff*n_turns
        
        inductor = [(0.,0.)]
        
        for i in range(n_turns):
            inductor.append((inductor[-1][0]+l, inductor[-1][1]))
            inductor.append((inductor[-1][0], inductor[-1][1]+diff))
            inductor.append((inductor[-1][0]-l, inductor[-1][1]))
            inductor.append((inductor[-1][0], inductor[-1][1]+diff))
        inductor[0] = (-diff,0.)
        N = len(inductor)
        for i in range(1,N+1):
            x,y = inductor[N-i]
            x = 2*l + diff - x
            inductor.append((x, y))

        inductor = draw.LineString(inductor)

        inductor = draw.rotate(inductor, p.orientation, origin=(l+(diff/2.), height/2.))
        inductor = draw.translate(inductor, p.pos_x, p.pos_y)

        if p.centered == "True":
            #print(bool(p.centered), p.centered)
            inductor = draw.translate(inductor, -(l+(diff/2.)), -height/2.)

        ##############################################
        # add qgeometry
        self.add_qgeometry('path', {'inductor': inductor},
                           width=p.width,
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        # FIX POINTS,
        self.add_pin('Pin1',
                     points=np.array(inductor.coords)[[-1,0]],
                     width=p.width,
                     input_as_norm=True)
        self.add_pin('Pin2',
                     points=np.array(inductor.coords)[-2:],
                     width=p.width,
                     input_as_norm=True)