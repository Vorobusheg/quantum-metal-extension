# -*- coding: utf-8 -*-

"""File contains dictionary for FingerCapacitor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class Patch(QComponent):
    """A single configurable trapezoid or triangle (cut out of the trapezoid) to be used as a patch.

    Inherits QComponent class.

    The class will add default_options class Dict to QComponent class before calling make.

    Default Options:
        * width: '500um'
        * height: '300um'
        * height_extra: height of the right edge
        * angles: quantity of angles for the figure (can be 3 or 4)
        * layer_patch : '2' -- Layer name for the rectangle patch
        * helper: 'False'
    """

    default_options = Dict(width='500um',
                           height='300um',
                           height_extra='-1um',
                           angles='4',
                           layer_patch='2',
                           datatype_patch='0',
                           helper='False',
                           _default_hole=Dict(
                               pos_x='0um',
                               pos_y='0um',
                               orientation='0',
                               width='0um',
                               length='0um',
                               fillet='0um',
                          ),)
    """Default drawing options"""

    TOOLTIP = """A single configurable square"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.

        if(p.height_extra < 0): p.height_extra = p.height

        if p.angles == 4:          
            # create the geometry
            geom = draw.Polygon([(p.width/2, p.height/2), (p.width/2, -p.height/2), (-p.width/2, -p.height_extra/2), (-p.width/2, p.height_extra/2)])
        elif p.angles == 3:
            # create the geometry
            geom = draw.Polygon([(p.width/2, p.height/2), (-p.width/2, -p.height_extra/2), (-p.width/2, p.height_extra/2)])
        else:
            raise ValueError('angles value is invalid, chose between 3 and 4')

        # subtracting holes
        for name in self.options.holes:
            hole = draw.rectangle(p.holes[name].width, p.holes[name].length, p.holes[name].pos_x, p.holes[name].pos_y)
            hole = hole.buffer(p.holes[name].fillet).buffer(-p.holes[name].fillet).buffer(-p.holes[name].fillet).buffer(p.holes[name].fillet)
            hole = draw.rotate(hole, p.holes[name].orientation, origin=(p.holes[name].pos_x, p.holes[name].pos_y))
            geom = draw.subtract(geom, hole.intersection(geom))
            
        if 'fillet' in p:
            geom = geom.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        polys = [geom]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        
        [geom] = polys
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'patch': geom},
                           helper=p.helper,
                           layer=p.layer_patch,
                           chip=p.chip,
                          datatype=0 if 'datatype_patch' not in p else p.datatype_patch)
        