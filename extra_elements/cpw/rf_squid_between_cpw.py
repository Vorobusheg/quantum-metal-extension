# -*- coding: utf-8 -*-



import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class RFSQUIDBetweenCPW_noFab(QComponent):
    """The base `RFSQUIDBetweenCPW_noFab` class. Cannot be used for Fab. Use the other function for this

    Inherits `QComponent` class.

    Default Options:
        * junction_length: '20um' -- Length of junction
        * loop_width: '100um' -- Width of loop
        * loop_height: '100um' -- Height of loop
        * wire_width: '20um' -- Width of loop wire
        * wire_gap: '12um' -- Gap of loop wire
        * cpw_in_width: '20um' -- Width of input CPW
        * cpw_out_width: '20um' -- Width of output CPW
        * cpw_in_gap: '12um' -- Gap of input CPW
        * cpw_out_gap: '12um' -- Gap of output CPW
        * cpw_in_length: '20um' -- Length of input CPW
        * cpw_out_length: '20um' -- Length of output CPW
        * junction_side: '0' -- '0' means junction on left arm for orientation=0, '1' means junction on right arm
    """

    default_options = Dict(
        junction_length= '20um',
        loop_width= '100um',
        loop_height= '100um',
        wire_width= '20um',
        wire_gap= '12um',
        cpw_in_width= '20um',
        cpw_out_width= '20um',
        cpw_in_gap= '12um',
        cpw_out_gap= '12um',
        cpw_in_length= '20um',
        cpw_out_length= '20um',
        junction_side= '0',
        )
    """Default drawing options"""

#     component_metadata = Dict(_qgeometry_table_poly='True',
#                               _qgeometry_table_junction='True')
    """Component metadata"""

    TOOLTIP = """The base `TransmonPocket` class."""

    def make(self):
        """Define the way the options are turned into QGeometry.

        The make function implements the logic that creates the geometry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed
        information, such as layer, subtract, etc.
        """

        # self.p allows us to directly access parsed values (string -> numbers) from the user option
        p = self.p

        # extract chip name
        chip = p.chip
        
        # Assuming junction on left and then flipping if on right
        
        pocket = draw.rectangle(p.loop_width + p.wire_width + 2*p.wire_gap, p.loop_height + p.wire_width + 2*p.wire_gap)
        
        loop = draw.LineString([
            (-p.loop_width/2, p.junction_length/2),
            (-p.loop_width/2, p.loop_height/2),
            (p.loop_width/2, p.loop_height/2),
            (p.loop_width/2, -p.loop_height/2),
            (-p.loop_width/2, -p.loop_height/2),
            (-p.loop_width/2, -p.junction_length/2),
        ])
        
        cpw_in = draw.LineString([(0,p.loop_height/2+ p.wire_width/2), (0,p.loop_height/2+ p.wire_width/2+p.cpw_in_length)])
        cpw_out = draw.LineString([(0,-p.loop_height/2- p.wire_width/2), (0,-p.loop_height/2- p.wire_width/2-p.cpw_out_length)])

        rect_jj = draw.LineString([(-p.loop_width/2, -p.junction_length/2), (-p.loop_width/2, p.junction_length/2)])
        
        # Rotate and translate all qgeometry as needed.
        # Done with utility functions in Metal 'draw_utility' for easy rotation/translation
        # NOTE: Should modify so rotate/translate accepts qgeometry, would allow for
        # smoother implementation.
        polys = [pocket, loop, cpw_in, cpw_out, rect_jj]
        if p.junction_side==1:
            polys = draw.scale(polys, xfact=-1)
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [pocket, loop, cpw_in, cpw_out, rect_jj] = polys

        # Use the geometry to create Metal qgeometry
        self.add_qgeometry('path',
                           dict(cpw_in_gap=cpw_in),
                           width=p.cpw_in_width + 2*p.cpw_in_gap,
                           layer=p.layer,
                           subtract=True,
                           chip=chip)
        self.add_qgeometry('path',
                           dict(cpw_out_gap=cpw_out),
                           width=p.cpw_out_width+2*p.cpw_out_gap,
                           layer=p.layer,
                           subtract=True,
                           chip=chip)
        self.add_qgeometry('path',
                           dict(cpw_in_main=cpw_in),
                           layer=p.layer,
                           width=p.cpw_in_width,
                           chip=chip)
        self.add_qgeometry('path',
                           dict(cpw_out_main=cpw_out),
                           layer=p.layer,
                           width=p.cpw_out_width,
                           chip=chip)
        self.add_qgeometry('path',
                           dict(loop=loop),
                           layer=p.layer,
                           width=p.wire_width,
                           chip=chip)
        self.add_qgeometry('poly',
                           dict(pocket=pocket),
                           subtract=True,
                           layer = p.layer,
                           chip=chip)
        self.add_qgeometry('junction',
                           dict(rect_jj=rect_jj),
                           width=p.wire_width,
                           chip=chip)
        self.add_pin('cpw_in',
                     points=np.array(cpw_in.coords),
                     width=p.cpw_in_width,
                     input_as_norm=True)
        self.add_pin('cpw_out',
                     points=np.array(cpw_out.coords),
                     width=p.cpw_out_width,
                     input_as_norm=True)

