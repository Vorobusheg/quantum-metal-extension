# -*- coding: utf-8 -*-

"""File contains dictionary for JunctionTopDown and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class JunctionManhattan_cross(QComponent):
    """A Manhattan Junction for xmon with optional patching.

    Inherits `QComponent` class.

    Description:
        A Manhattan Junction for xmon with optional patching.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * w_line : '500nm' -- Width of line going towards the junction
        * w_undercut : '200nm' -- Width of the undercut
        * width_jxn : '350nm' -- Width of the junction from the line coming from top
        * height_jxn : '350nm' -- Width of the junction from the line coming from the side
        * main_pad_size_top : '2um' -- Size of the pad on the top
        * main_pad_size_side : '2um' -- Size of the pad on the side
        * helper: 'False'
    """

    default_options = Dict(length='1um',
                           x_cross='0.8um',
                           width='0.3um',
                           undercut='0um',
                           undercut_big='0um',
                           layer='2',
                           layer_undercut='3',
                           draw='all', # can be 'all', 'first', 'second',
                           helper='False',)
    """Default drawing options"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""

        p = self.p  # p for parsed parameters. Access to the parsed options.
        
        # junction arm
        rect = draw.rectangle(p.length - p.width/2, p.width, (p.length - p.width/2 - 2*p.x_cross)/2, 0)
        circ = draw.Point(p.length - p.width/2 - p.x_cross, 0).buffer(p.width/2, resolution=50)
        main = rect.union(circ)
        
        # add second arm
        main = main.union(draw.rotate(main, 90, origin=(0., 0.)))

        # arm choice
        if(p.draw == 'first'):
            main = main.intersection(draw.rectangle(2*p.length, p.width, 0, 0))
        elif(p.draw == 'second'):
            main = main.intersection(draw.rectangle(p.width, 2*p.length, 0, 0))
        elif(p.draw != 'all'):
            raise ValueError('Incorrect draw!')
            
        # general movement
        main = draw.rotate(main, p.orientation, origin=(0., 0.))
        main = draw.translate(main, p.pos_x, p.pos_y)

        if(p.undercut != 0):
            # make undercut
            undercut = draw.rectangle(p.length + p.undercut_big - p.width/2, p.width, (p.length + p.undercut_big - p.width/2 - 2*p.x_cross)/2, 0)
            circ = draw.Point(p.length  + p.undercut_big - p.width/2 - p.x_cross, 0).buffer(p.width/2, resolution=50)
            undercut = undercut.union(circ)
            # add second arm
            undercut = undercut.union(draw.rotate(undercut, 90, origin=(0., 0.)))
            undercut = undercut.buffer(p.undercut)
            # general movement
            undercut = draw.rotate(undercut, p.orientation, origin=(0., 0.))
            undercut = draw.translate(undercut, p.pos_x, p.pos_y)
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'cross': main},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
       
        if(p.undercut != 0):
            # add qgeometry
            self.add_qgeometry('poly', {'undercut': undercut},
                               helper=p.helper,
                               layer=p.layer_undercut,
                               chip=p.chip)
            