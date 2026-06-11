# -*- coding: utf-8 -*-



import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class DCSQUIDBetweenCPW_Fab(QComponent):
    """The base `DCSQUIDBetweenCPW_noFab` class. Cannot be used for Fab. Use the other function for this

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
        fillet='5um',
        inductance1='10nH',
        inductance2='10nH',
        capacitance1='0.5fF',
        capacitance2='0.5fF',
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
        
#         loop = draw.LineString([
#             (-p.loop_width/2, p.junction_length/2),
#             (-p.loop_width/2, p.loop_height/2),
#             (p.loop_width/2, p.loop_height/2),
#             (p.loop_width/2, -p.loop_height/2),
#             (-p.loop_width/2, -p.loop_height/2),
#             (-p.loop_width/2, -p.junction_length/2),
#         ])
        loop = draw.subtract(draw.rectangle(p.loop_width + p.wire_width, p.loop_height + p.wire_width),
                             draw.rectangle(p.loop_width-p.wire_width, p.loop_height-p.wire_width),
                            )
        
        cpw_in = draw.LineString([(0,p.loop_height/2+ p.wire_width/2), (0,p.loop_height/2+ p.wire_width/2+p.cpw_in_length)])
        cpw_out = draw.LineString([(0,-p.loop_height/2- p.wire_width/2), (0,-p.loop_height/2- p.wire_width/2-p.cpw_out_length)])
        
        cpw_in_app = draw.LineString([(0,p.loop_height/2+ p.wire_width/2), (0,p.loop_height/2+ p.wire_width/2+p.cpw_in_length/2)])
        cpw_out_app = draw.LineString([(0,-p.loop_height/2- p.wire_width/2), (0,-p.loop_height/2- p.wire_width/2-p.cpw_out_length/2)])
        
        loop = draw.union([loop,
                           draw.buffer(cpw_in_app, p.cpw_in_width/2),
                           draw.buffer(cpw_out_app, p.cpw_out_width/2),
                            ])
        
        if 'fillet' in p:
            loop = loop.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
            pocket = pocket.buffer(p.fillet).buffer(-p.fillet).buffer(-p.fillet).buffer(p.fillet)
        
        loop = draw.union([loop,
                           draw.buffer(cpw_in, p.cpw_in_width/2),
                           draw.buffer(cpw_out, p.cpw_out_width/2),
                            ])
           
        pocket = draw.union([pocket,
                             draw.buffer(cpw_in, p.cpw_in_width/2 + p.cpw_in_gap),
                             draw.buffer(cpw_out, p.cpw_out_width/2 + p.cpw_out_gap),
                            ])

        rect_jj_1 = draw.LineString([(-p.loop_width/2, -p.junction_length/2), (-p.loop_width/2, p.junction_length/2)])
        rect_jj_2 = draw.LineString([(p.loop_width/2, -p.junction_length/2), (p.loop_width/2, p.junction_length/2)])
        
        loop = draw.subtract(loop, draw.buffer(rect_jj_1, p.wire_width+p.wire_gap))
        loop = draw.subtract(loop, draw.buffer(rect_jj_2, p.wire_width+p.wire_gap))
        
        # Rotate and translate all qgeometry as needed.
        # Done with utility functions in Metal 'draw_utility' for easy rotation/translation
        # NOTE: Should modify so rotate/translate accepts qgeometry, would allow for
        # smoother implementation.
        polys = [pocket, loop, cpw_in, cpw_out, rect_jj_1, rect_jj_2]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [pocket, loop, cpw_in, cpw_out, rect_jj_1, rect_jj_2] = polys
        
        # Use the geometry to create Metal qgeometry
#         self.add_qgeometry('path',
#                            dict(cpw_in_gap=cpw_in),
#                            width=p.cpw_in_width + 2*p.cpw_in_gap,
#                            layer=p.layer,
#                            subtract=True,
#                            chip=chip)
#         self.add_qgeometry('path',
#                            dict(cpw_out_gap=cpw_out),
#                            width=p.cpw_out_width+2*p.cpw_out_gap,
#                            layer=p.layer,
#                            subtract=True,
#                            chip=chip)
#         self.add_qgeometry('path',
#                            dict(cpw_in_main=cpw_in),
#                            layer=p.layer,
#                            width=p.cpw_in_width,
#                            chip=chip)
#         self.add_qgeometry('path',
#                            dict(cpw_out_main=cpw_out),
#                            layer=p.layer,
#                            width=p.cpw_out_width,
#                            chip=chip)
        self.add_qgeometry('poly',
                           dict(loop=loop),
                           layer=p.layer,
                           chip=chip)
        self.add_qgeometry('poly',
                           dict(pocket=pocket),
                           subtract=True,
                           layer = p.layer,
                           chip=chip)
        self.add_qgeometry('junction',
                           dict(rect_jj1=rect_jj_1),
                           hfss_inductance=self.options.inductance1,
                           hfss_capacitance=self.options.capacitance1,
                           width=p.wire_width,
                           chip=chip)
        self.add_qgeometry('junction',
                           dict(rect_jj2=rect_jj_2),
                           hfss_inductance=self.options.inductance2,
                           hfss_capacitance=self.options.capacitance2,
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

