# -*- coding: utf-8 -*-

"""File contains dictionary for GoodTaper and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
from scipy.optimize import root
import numpy as np


class CirclePad(QComponent):
    """A circle with geometrically x^2 + x^4 taper.

    Inherits `QComponent` class.

    Description:
        A Geometrically Exponential Taper.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * width_in: '20um' -- Inner Width of the Input side
        * length: '500um' -- Length of the structure including both taper and circle
        * R: '500um' --  Radius of the circle        
        * merging: '0.5' --  Number from 0 to 1 defining the point of the taper ending inside one radius scale
        * N_steps: '100' -- The number of linear steps in which one side of the taper is formed (Increase this for greater precision)
        * subtract: 'False'
        * helper: 'False'
        * layer: '1' -- Draing layer
    """

    default_options = Dict(width_in='20um',
                           length='500um',
                           R='200um',
                           merging = '0.5', # can be between 0 and 1
                           N_steps='100',
                           subtract='False',
                           helper='False',
                           layer='1',
                          )
                           
    """Default drawing options"""

    TOOLTIP = """A Geometrically Exponential Taper"""

    def make(self):
        p = self.p  # p for parsed parameters. Access to the parsed options.
        N = int(p.N_steps)
        
        # Create the geometry
        poly = []

        d_0 = p.width_in/2
        l = p.length
        R = p.R
        x_0 = l - (2 - p.merging)*R

        # searhing for a*x^2 + b*x^4 + d_0 = 0 via SLE

        M = np.asarray([[x_0**2, x_0**4],
                        [2*x_0, 4*x_0**3]])
        c = np.sqrt(R**2 - (x_0 - l + R)**2)
        V = np.asarray([c - d_0, -(x_0 - l + R)/c])

        sol = np.linalg.solve(M, V)

        # monotonic check
        c = -sol[0]/(6*sol[1])
        if(c <= 0 and sol[0] > 0):
            print("Monotonic tail derivative")
        elif(np.sqrt(c) > x_0 and sol[0] > 0):
            print("Monotonic tail derivative")
        else:
            print("Non-monotonic tail derivative")

        x_list = np.linspace(0, x_0, N)
        
        list_curve_y = sol[0]*x_list**2 + sol[1]*x_list**4 + d_0
        list_curve_y = np.append(list_curve_y, list_curve_y[-1])
        list_curve_y = np.append(list_curve_y, -np.flip(list_curve_y))
        list_curve_y = np.append(list_curve_y, list_curve_y[0])
        
        x_list_out = np.append(x_list, p.length)
        x_list_in = np.append(x_list, x_list[-1])
        x_list_out = np.append(x_list_out, np.flip(x_list_out))
        x_list_in = np.append(x_list_in, np.flip(x_list_in))
        x_list_out = np.append(x_list_out, x_list_out[0])
        x_list_in = np.append(x_list_in, x_list_in[0])

        list_curve = np.vstack((x_list_in, list_curve_y)).T

        list_curve = [tuple(row) for row in list_curve]

        taper_main = draw.Polygon(list_curve)

        # circle part
        circ = draw.Point(l - R, 0).buffer(R, resolution=100)
        taper_main = taper_main.union(circ)

        # pin
        pin_line = draw.LineString([(l, 0), (0, 0)])

        els = [taper_main, pin_line]
        
        els = draw.rotate(els, p.orientation, origin=(0., 0.))
        els = draw.translate(els, p.pos_x, p.pos_y)
        
        [taper_main, pin_line]  = els

        
        # add qgeometry
        self.add_qgeometry('poly', {'taper_main': taper_main},
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)

        # Generating pin
        self.add_pin("in",
                     points=pin_line.coords,
                     width=2*d_0,
                     input_as_norm=True)
