# -*- coding: utf-8 -*-

"""File contains dictionary for GoodTaper and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
from scipy.optimize import root
import numpy as np


class Taper(QComponent):
    """A Geometrically Exponential Taper.

    Inherits `QComponent` class.

    Description:
        A Geometrically Exponential Taper.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * outer_width_in: '22um' -- Outer Width of the Input side
        * width_in: '10um' -- Inner Width of the Input side
        * outer_width_out: '220um' -- Outer Width of the Output side (Always keep output dimensions > input dimensions for proper offshooting)
        * width_out: '100um' -- Inner Width of the Output side (Always keep output dimensions > input dimensions for proper offshooting)
        * length: '300um' -- Length of the taper including the offshoots
        * offshoot_out: '80um' --  Length of the offshoot of the outer part
        * offshoot_in: '40um' --  Length of the offshoot of the inner part
        * N_steps: '20' -- The number of linear steps in which one side of the taper is formed (Increase this for greater precision)
        * subtract: 'False'
        * helper: 'False'
    """

    default_options = Dict(width_in='10um',
                           width_mid='50um',
                           width_out='100um',
                           length='300um',
                           length_in='20um',
                           length_cut='20um',
                           slope='0.45',
                           end_slope='0',
                           evaporation_angle='0',
                           evaporation_shift='0um',
                           N_steps='100',
                           undercut='0um',
                           subtract='False',
                           helper='False',
                           draw='all', # can be 'all', 'in', 'out',
                           layer='1',
                           layer_undercut='1',
                           datatype_main = '0',
                           datatype_undercut='10',
                           _default_hole=Dict(
                               pos_x='0um',
                               pos_y='0um',
                               orientation='0',
                               width='0um',
                               length='0um',
                               fillet='0um',
                          ),
                          )
                           
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
        poly = []

        if(p.end_slope==0):
            # circle ending
            d_0 = p.width_in/2
            d_2 = p.width_mid/2
            d_3 = p.width_out/2
    
            x_1 = p.length_in
            x_3 = p.length
            s = p.slope
            
            d_1 = d_0 + s*x_1
    
            # searching alpha, x_2 and R
            def x_2_of_alpha(alpha): 
                A = 2*(alpha*(d_2 - d_1) + s)
                B = d_3 - d_2
                return x_3 + B*(A - np.sqrt(A**2 + 4))/2
    
            def alpha_eq(alpha): return (np.exp(alpha*(x_2_of_alpha(alpha) - x_1)) - 1 - (d_2 - d_1)/s*alpha)**2
    
            sol = root(alpha_eq, x0=100)
            alpha=np.max(sol.x)
            if(np.abs(alpha) < 1e-10): raise ValueError('Bad inputs, smoothing is impossible!')
            x_2 = x_2_of_alpha(alpha)
            R = ((d_3 - d_2)**2/(x_3 - x_2) + x_3 - x_2)/2
       
        else:
            # exponent ending
            s = p.slope
            k = p.end_slope
            d_0 = p.width_in/2
            d_2 = p.width_out/2
            x_2 = p.length
            
            x_1 = ((k - s)*x_2 - np.log(k/s)*(d_2 - d_0))/(k - s*(np.log(k/s) + 1))
            d_1 = d_0 + s*x_1

            if(x_1 < 0 or d_1 < 0): raise ValueError('Bad inputs, smoothing is impossible!')
                
            alpha = np.log(k/s)/(x_2 - x_1)
        
        x_list = np.linspace(x_1, x_2, N)

        list_curve_y = s/alpha*(np.exp(alpha*(x_list - x_1)) - 1) + d_1
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

        # exponential part
        taper_main = draw.Polygon(list_curve)

        # linear part
        linear = draw.Polygon([(0, -d_0), (0, +d_0), (x_1, +d_1), (x_1, -d_1)])
        taper_main = taper_main.union(linear)

        if(p.end_slope==0):

            # the rest part
            rect = draw.rectangle(x_3-x_2, d_3*2, (x_3 + x_2)/2, 0)
            
            circ = draw.Point(x_3 - R, d_3).buffer(R, resolution=100)
            circ = circ.intersection(rect)
            rect = draw.subtract(rect, circ)
    
            circ = draw.Point(x_3 - R, -d_3).buffer(R, resolution=100)
            circ = circ.intersection(rect)
            rect = draw.subtract(rect, circ)
            
            taper_main = taper_main.union(rect)

        # cutting
        if(p.draw == 'out'):
            rect = draw.rectangle(p.length-p.length_cut, p.width_out, (p.length + p.length_cut)/2, 0)
            taper_main = taper_main.intersection(rect)
        elif(p.draw == 'in'):
            rect = draw.rectangle(p.length_cut, p.width_out, p.length_cut/2, 0)
            taper_main = taper_main.intersection(rect)
        elif(p.draw != 'all'):
            raise ValueError('Incorrect draw!')

        # subtracting holes
        for name in self.options.holes:
            hole = draw.rectangle(p.holes[name].width, p.holes[name].length, p.holes[name].pos_x, p.holes[name].pos_y)
            hole = hole.buffer(p.holes[name].fillet).buffer(-p.holes[name].fillet).buffer(-p.holes[name].fillet).buffer(p.holes[name].fillet)
            hole = draw.rotate(hole, p.holes[name].orientation, origin=(p.holes[name].pos_x, p.holes[name].pos_y))
            taper_main = draw.subtract(taper_main, hole.intersection(taper_main))
        
        taper_main = draw.rotate(taper_main, p.orientation, origin=(0., 0.))
        taper_main = draw.translate(taper_main, p.pos_x, p.pos_y)
        
        # evaporation shift
        phi = p.evaporation_angle/180*np.pi
        shifts = np.linspace(0, p.evaporation_shift, 20)
        tmp = taper_main
        for shift in shifts: taper_main = taper_main.intersection(draw.translate(tmp, shift*np.cos(phi), shift*np.sin(phi)))

        # make undercut
        undercut = taper_main.buffer(p.undercut)
        ##############################################

        # add qgeometry
        self.add_qgeometry('poly', {'taper_main': taper_main},
                           subtract=p.subtract,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                           datatype=0 if 'datatype_main' not in p else p.datatype_main)

        if(p.undercut != 0):
            # add qgeometry
            self.add_qgeometry('poly', {'undercut': undercut},
                               subtract=p.subtract,
                               helper=p.helper,
                               layer=p.layer_undercut,
                               chip=p.chip,
                               datatype=10 if 'datatype_undercut' not in p else p.datatype_undercut)
