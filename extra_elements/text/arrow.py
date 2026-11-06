"""Arrow QComponent for Qiskit Metal."""

from shapely.geometry import Polygon

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class Arrow(QComponent):
    """A single arrow drawn as one polygon.

    Inherits QComponent class.

    The arrow points along +x before rotation. Its tail (the back end of the
    shaft) sits at (pos_x, pos_y), and the whole arrow is rotated by
    `orientation` (degrees) around the tail.

        tail                       tip
         |<------ length ---------->|
                          |<-head-->|
                          |\\
         +----------------+ \\         ---
         |    shaft            >      width / head_width
         +----------------+ /         ---
                          |/

    Default Options:
        * length: '300um' -- total length, from tail to tip
        * width: '20um' -- width of the shaft
        * head_length: '80um' -- length of the head, from its base to the tip
        * head_width: '80um' -- width of the head at its base
        * subtract: 'False'
        * helper: 'False'
    """

    default_options = Dict(
        length="300um",
        width="20um",
        head_length="80um",
        head_width="80um",
        subtract="False",
        helper="False",
    )
    """Default drawing options"""

    TOOLTIP = """A single configurable arrow"""

    def make(self):
        """Build the arrow polygon and add it to the design."""
        p = self.p

        if p.head_length >= p.length:
            raise ValueError(
                f"{self.name}: head_length ({p.head_length}) must be smaller "
                f"than length ({p.length})."
            )
        if p.head_width < p.width:
            raise ValueError(
                f"{self.name}: head_width ({p.head_width}) must not be smaller "
                f"than width ({p.width})."
            )

        shaft = p.length - p.head_length  # length of the shaft alone
        w = p.width / 2  # half width of the shaft
        hw = p.head_width / 2  # half width of the head

        # Points in counter-clockwise order, tail at (0, 0), tip at (length, 0)
        arrow = Polygon([
            (0, -w),
            (shaft, -w),
            (shaft, -hw),
            (p.length, 0),
            (shaft, hw),
            (shaft, w),
            (0, w),
        ])

        # Rotate around the tail, then move the tail to (pos_x, pos_y)
        arrow = draw.rotate(arrow, p.orientation, origin=(0, 0))
        arrow = draw.translate(arrow, p.pos_x, p.pos_y)

        self.add_qgeometry(
            "poly",
            {"arrow": arrow},
            subtract=p.subtract,
            helper=p.helper,
            layer=p.layer,
            chip=p.chip,
        )