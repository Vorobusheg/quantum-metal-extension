# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class FingerCapacitor(QComponent):
    """A Finger Capacitor with a specified overlap length per finger and height.

    Inherits `QComponent` class.

    Description:
        A finger capacitor.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * width: '4um' -- the width of the line
        * gap: '4um' -- The separation between the two turns
        * overlap: '100um' -- The overlap length between fingers
        * height: '300um' -- Height approximated to the closest conforming length <= the provided one
        * n_finger: '10' -- Number of fingers per electrode
        * set_fingers: 'True' -- If False, constructs capacitor by using the 'height' parameter, else uses the 'n_finger' parameter
        * pin1_position: 'Bottom' -- Can take three values 'Bottom', 'Center', 'Top' and based on that, the pin is placed at the bottom, center, or top of the left electrode. 
        * pin2_position: 'Bottom' -- Can take three values 'Bottom', 'Center', 'Top' and based on that, the pin is placed at the bottom, center, or top of the right electrode. 
        * centered: 'False' -- center at (0.,0.) or lower bottom pin at (0.,0.)?
        * helper: 'False'
    """

    default_options = Dict(width='4um',
                           overlap='100um',
                           gap='4um',
                           height='300um',
                           n_finger='10',
                           set_fingers='True',
                           pin1_position='Bottom',
                           pin2_position='Bottom',
                           centered='False',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A Finger Capacitor"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        diff = p.gap + p.width
        l = p.overlap
        if p.set_fingers == 'True':
            n_finger = int(p.n_finger)
        else:
            n_finger = int(p.height/(2*diff))

        capacitor_box = draw.rectangle(l + 2*diff, 2*diff*n_finger, l/2, diff*n_finger)
        capacitor_etch = draw.rectangle(l + 2*diff, 2*diff*n_finger, l/2, diff*n_finger)
        capacitor_cut = [(-p.width/2,-p.width/2)]
        
        for i in range(n_finger):
            capacitor_cut.append((capacitor_cut[-1][0], capacitor_cut[-1][1] + diff))
            capacitor_cut.append((capacitor_cut[-1][0] + l + p.gap, capacitor_cut[-1][1]))
            capacitor_cut.append((capacitor_cut[-1][0], capacitor_cut[-1][1] + diff))
            capacitor_cut.append((capacitor_cut[-1][0] - l - p.gap, capacitor_cut[-1][1])) 
            
        capacitor_cut = draw.LineString(capacitor_cut).buffer(p.gap/2, cap_style=2, join_style=2)
        capacitor = draw.subtract(capacitor_box, capacitor_cut)

        capacitor = draw.translate(capacitor, p.pos_x, p.pos_y - p.width/2)
        capacitor_etch = draw.translate(capacitor_etch, p.pos_x, p.pos_y - p.width/2)

        capacitor = draw.rotate(capacitor, p.orientation, origin=(l + diff, diff*n_finger))
        capacitor_etch = draw.rotate(capacitor_etch, p.orientation, origin=(l + diff, diff*n_finger))

        if p.centered == "True":
            capacitor = draw.translate(capacitor, -l - diff, -diff*n_finger)
            capacitor_etch = draw.translate(capacitor_etch, -l - diff, -diff*n_finger)

        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'capacitor': capacitor},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        self.add_qgeometry('poly', {'capacitor_etch': capacitor_etch},
                           width=p.gap,
                           helper=p.helper,
                           subtract=True,
                           layer=p.layer,
                           chip=p.chip)
        # FIX POINTS,
        if p.centered == 'True':
            offset_x, offset_y = -l - diff + p.pos_x , -diff*n_finger+p.pos_y
        else:
            offset_x, offset_y = p.pos_x,p.pos_y
        offset_x1, offset_y1 = offset_x, offset_y
        offset_x2, offset_y2 = offset_x + l + 2*diff, offset_y
        if p.pin1_position == 'Center':
            offset_y1 = diff*(n_finger-1)/2
        elif p.pin1_position == 'Top':
            offset_y1 = diff*(n_finger-1)
        
        if p.pin2_position == 'Center':
            offset_y2 = diff*(n_finger-1)/2
        elif p.pin2_position == 'Top':
            offset_y2 = diff*(n_finger-1)
        

        self.add_pin('Pin1',
                     points=np.array([[offset_x1 - 2.*diff, offset_y1],[offset_x1 - diff, offset_y1]]),
                     width=p.width,
                     input_as_norm=True)
        self.add_pin('Pin2',
                     points=np.array([[offset_x2 - 2.*diff, offset_y2],[offset_x2 - diff, offset_y2]]),
                     width=p.width,
                     input_as_norm=True)