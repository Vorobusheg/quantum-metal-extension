# -*- coding: utf-8 -*-

"""
File contains dictionary for RectangularCoilByTurns and the make().
Adapted from implementation by Christian
"""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np

class ResonatorCoilByTurns(QComponent):
    """A rectangular spiral resonator where the user can specify the inner diameter,
    the number of turns, the spacing between turns, and the wire width, height, and position.

    Inherits `QComponent` class

    Default Options:
        * inner_diameter: '10um' -- Inner diameter of the spiral
        * n: '3' -- Number of turns of the spiral
        * spacing: '2um' -- Spacing between the turns of the spiral
        * line_width: '1um' -- The width of the wire of the spiral
        * height: '40um' -- The height of the wire in the spiral
        * etch_box_extra_x: '50um' -- Extra etching away of the ground plane in the x-direction
        * etch_box_extra_y: '50um' -- Extra etching away of the ground plane in the y-direction
        * generate_coupling_pad: 'True' -- If to generate a coupling pad
        * coupling_pad_distance: '100um' -- Distance from the end of coil where the coupling pad would be
        * coupling_pad_width: '100um' -- Width of coupling pad
        * coupling_pad_height: '10um' -- Thickness of coupling pad
    """
    component_metadata = Dict(short_name='res_rect_turns')
    default_options = Dict(
        inner_diameter='10um',
        n='3',
        spacing='2um',
        line_width='1um',
        height='40um',
        etch_box_extra_x='50um',
        etch_box_extra_y='50um',
        generate_coupling_pad='True',
        coupling_pad_distance='100um',
        coupling_pad_width='100um',
        coupling_pad_height='10um',
    )
    TOOLTIP = """A rectangular spiral resonator with customizable position, inner diameter,
    number of turns, spacing, and wire dimensions."""

    def make(self):
        p = self.p  # parsed parameters
        n = int(p.n)

        # Initialize the list for the spiral points
        spiral_list = []

        # Starting points based on the inner diameter and position
        x_point = p.inner_diameter / 2
        y_point = p.height / 2

        # Check if the initial dimensions are feasible
        if x_point <= p.line_width or y_point <= p.line_width:
            self.logger.warning('Inputted values result in the dimensions being too small.')
            return

        # Build the rectangular spiral geometry, adjusting for position
        for step in range(n):
            # Add corrected position to each coordinate
            spiral_list.extend([
                (-x_point, -y_point),
                (x_point, -y_point),
                (x_point, y_point),
                (-x_point - (p.line_width + p.spacing), y_point)
            ])

            # Increment the x and y points for the next turn
            x_point += p.line_width + p.spacing
            y_point += p.line_width + p.spacing

        # Final adjustment to close the spiral's path if necessary
        spiral_list.append((-x_point, -y_point))
        
        # Add a distance to the coupling pad if necessary
        if p.generate_coupling_pad == 'True':
            x_point, y_point = x_point, y_point+p.coupling_pad_distance
            spiral_list.append((-x_point, -y_point))

        # Convert the list of points into a geometric shape
        spiral_geometry = draw.LineString(spiral_list)
        
        coil_etch = draw.rectangle(2*np.abs(x_point)+2*p.etch_box_extra_x, 2*np.abs(y_point)+2*p.etch_box_extra_y, 0, 0)
        
        spiral_geometry = draw.rotate(spiral_geometry, p.orientation, origin=(0,0))
        coil_etch = draw.rotate(coil_etch, p.orientation, origin=(0,0))
          
        spiral_geometry = draw.translate(spiral_geometry, p.pos_x, p.pos_y)
        coil_etch = draw.translate(coil_etch, p.pos_x, p.pos_y)
        
        # Generate the resonator's geometric structure and add to the design
        self.add_qgeometry('path', {'coil_resonator': spiral_geometry}, width=p.line_width)
        self.add_qgeometry('poly', {'coil_etch': coil_etch}, subtract=True)
        
        # Add a distance to the coupling pad if necessary
        if p.generate_coupling_pad == 'True':
            coupling_pad = draw.rectangle(p.coupling_pad_width, p.coupling_pad_height, -x_point, -y_point)
            coupling_pad = draw.rotate(coupling_pad, p.orientation, origin=(0,0))
            coupling_pad = draw.translate(coupling_pad, p.pos_x, p.pos_y)
            self.add_qgeometry('poly', {'coupling_pad': coupling_pad})