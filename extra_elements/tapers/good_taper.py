# -*- coding: utf-8 -*-

"""File contains dictionary for GoodTaper and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class GoodTaper(QComponent):
    """A Geometrically Exponential Taper.

    Inherits `QComponent` class.

    Description:
        A Geometrically Exponential Taper.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * outer_width_in: '22um' -- Outer Width of the Input side
        * inner_width_in: '10um' -- Inner Width of the Input side
        * outer_width_out: '220um' -- Outer Width of the Output side (Always keep output dimensions > input dimensions for proper offshooting)
        * inner_width_out: '100um' -- Inner Width of the Output side (Always keep output dimensions > input dimensions for proper offshooting)
        * length: '300um' -- Length of the taper including the offshoots
        * offshoot_out: '80um' --  Length of the offshoot of the outer part
        * offshoot_in: '40um' --  Length of the offshoot of the inner part
        * N_steps: '20' -- The number of linear steps in which one side of the taper is formed (Increase this for greater precision)
        * siding: 'Right' -- Output on the right or left
        * subtract: 'False'
        * helper: 'False'
    """

    default_options = Dict(outer_width_in='22um',
                           inner_width_in='10um',
                           outer_width_out='220um',
                           inner_width_out='100um',
                           length='300um',
                           offshoot_out='80um',
                           offshoot_in='40um',
                           N_steps='20',
                           siding='Right',
                           subtract='False',
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A Geometrically Exponential Taper"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        N = int(p.N_steps)
        
        # Create the geometry
        outer_poly = []
        inner_poly = []

        x_list = np.linspace(0., p.length - p.offshoot_out, N)
        outer_list_curve_y = p.outer_width_in*np.power(p.outer_width_out/p.outer_width_in ,x_list/(p.length - p.offshoot_out))/2.
        inner_list_curve_y = p.inner_width_in*np.power(p.inner_width_out/p.inner_width_in, x_list/(p.length - p.offshoot_out))/2.
        
        outer_list_curve_y = np.append(outer_list_curve_y, outer_list_curve_y[-1])
        inner_list_curve_y = np.append(inner_list_curve_y, inner_list_curve_y[-1])

        outer_list_curve_y = np.append(outer_list_curve_y, -np.flip(outer_list_curve_y))
        inner_list_curve_y = np.append(inner_list_curve_y, -np.flip(inner_list_curve_y))

        outer_list_curve_y = np.append(outer_list_curve_y, outer_list_curve_y[0])
        inner_list_curve_y = np.append(inner_list_curve_y, inner_list_curve_y[0])
        
        x_list_out = np.append(x_list, p.length)
        x_list_in = np.append(x_list, x_list[-1] + p.offshoot_in)

        x_list_out = np.append(x_list_out, np.flip(x_list_out))
        x_list_in = np.append(x_list_in, np.flip(x_list_in))

        x_list_out = np.append(x_list_out, x_list_out[0])
        x_list_in = np.append(x_list_in, x_list_in[0])

        if p.siding == 'Right':
            pass
        elif p.siding == 'Left':
            x_list_out = -x_list_out
            x_list_in = -x_list_in
        else:
            raise ValueError("Siding can only be Right or Left")

        outer_list_curve = np.vstack((x_list_out, outer_list_curve_y)).T

        inner_list_curve = np.vstack((x_list_in, inner_list_curve_y)).T

        outer_list = [tuple(row) for row in outer_list_curve]
        inner_list = [tuple(row) for row in inner_list_curve]

        taper_empty = draw.Polygon(outer_list)
        taper_main = draw.Polygon(inner_list)

        taper_empty = draw.rotate(taper_empty, p.orientation, origin=(0., 0.))
        taper_empty = draw.translate(taper_empty, p.pos_x, p.pos_y)

        taper_main = draw.rotate(taper_main, p.orientation, origin=(0., 0.))
        taper_main = draw.translate(taper_main, p.pos_x, p.pos_y)

        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'taper_empty': taper_empty},
                           subtract=True,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        self.add_qgeometry('poly', {'taper_main': taper_main},
                           subtract=False,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        # FIX POINTS,
        self.add_pin('Pin1',
                     points=[(0, -p.inner_width_in/2.), (0, p.inner_width_in/2.)],
                     width=p.inner_width_in,
                     input_as_norm=False)