from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent


class CrossedArrows(QComponent):
    """Two arrows crossing at the origin at 90 degrees.

    Each arrow = a shaft (path) + a triangular head (poly).
    The whole set is drawn at the origin, then moved/rotated as a rigid body.
    """

    default_options = Dict(
        length='0.4mm',        # tip-to-tip length of each arrow
        shaft_width='30um',  # linewidth of the shaft
        head_length='0.1mm', # length of the triangular head
        head_width='0.1mm',  # base width of the head
        pos_x='0um',
        pos_y='0um',
        orientation='0',     # rotates the whole crossed pair
        helper='False',
        subtract='True',
    )
    """Default drawing options"""

    def make(self):
        p = self.p
        L = p.length
        hl = p.head_length
        hw = p.head_width

        # --- one arrow pointing along +x, centered on the origin ---
        shaft = draw.LineString([(-L / 2, 0), (L / 2 - hl, 0)])
        head = draw.Polygon([
            (L / 2, 0),
            (L / 2 - hl, hw / 2),
            (L / 2 - hl, -hw / 2),
        ])

        # --- second arrow = first one rotated 90 deg about the origin ---
        shaft_v = draw.rotate(shaft, 90, origin=(0, 0))
        head_v = draw.rotate(head, 90, origin=(0, 0))

        # --- collect the whole set and transform together ---
        geom = [shaft, head, shaft_v, head_v]
        geom = draw.rotate(geom, p.orientation, origin=(0, 0))
        geom = draw.translate(geom, p.pos_x, p.pos_y)
        [shaft, head, shaft_v, head_v] = geom

        # --- register geometry (same layer / subtract as Text) ---
        self.add_qgeometry('path',
                           {'shaft_h': shaft, 'shaft_v': shaft_v},
                           width=p.shaft_width,
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                           subtract=p.subtract,
                           datatype=10)
        self.add_qgeometry('poly',
                           {'head_h': head, 'head_v': head_v},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip,
                           subtract=p.subtract,
                           datatype=10)

