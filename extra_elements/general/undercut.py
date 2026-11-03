import numpy as np
from shapely import wkt
from shapely.geometry import LineString
from qiskit_metal import Dict, draw
from qiskit_metal.qlibrary.core import QComponent, QRoute
from qiskit_metal.toolbox_metal.parsing import is_true

class Undercut(QComponent):
    """The metal shapes of another component, grown by a given width: an undercut layer.

    Inherits `QComponent` class.

    Makes the undercut of an existing component (the source) without any change in the
    source class. Every metal shape of the source (``poly`` and ``path`` qgeometry with
    ``subtract=False``) is grown by ``width`` and drawn on ``layer``, under the same name.
    Helper shapes (``helper=True``) are included, because Metal's GDS export draws them.
    The result is the full grown shape, as ``shape.buffer(width)``: it covers the source
    shape, it is not only the rim around it.

    Sketch:
        Undercut (dots) of one source shape (lines), seen from the top
        ::

            ............................
            :  ______________________  :
            : |                      | :
            : |     source shape     | :
            : |______________________| :
            :..........................:
                                     <-> width

    Position:
        The undercut is an independent component with its own ``pos_x``, ``pos_y`` and
        ``orientation``. The ones not given are taken from the frame of the source at
        creation, so the undercut is placed on the source. After that it does not follow
        the source: move and copy the two together, e.g. put the undercut in the same list
        of components for ``transform_group`` and ``copy_group``.

        The frame of a component is its ``pos_x``, ``pos_y`` and ``orientation``. A route
        (``QRoute``) is drawn between pins, so its frame is its start pin: the middle point
        and the normal direction of the pin.

    Shape, bind=True (default):
        At every rebuild the shapes are read again from the source, relative to the frame
        of the source, and drawn in the frame of the undercut. So when the source
        dimensions change, ``design.rebuild()`` or ``gui.rebuild()`` updates the undercut.
        A copy of the undercut keeps ``component`` equal to the original source and takes
        its shape: it is correct as long as the copied source has the same shape as the
        original, and the original must stay in the design.

        When a group is rotated by a multiple of 90 degrees, Metal draws a route again with
        the same shape relative to its start pin, so the undercut stays correct. After other
        angles Metal draws a meander differently, and the undercut matches the new route
        only after the next ``design.rebuild()`` or ``gui.rebuild()``.

    Shape, bind=False:
        The shapes are read from the source once, at the first build, and kept in the
        option ``shapes`` (relative to the frame of the source, before they are grown).
        Later builds and all copies use only ``shapes``, so the source can be changed or
        deleted: e.g. make the undercut of an object, copy the two and move the copies,
        then delete the original object and its undercut. ``width`` and ``layer`` still
        apply; ``names`` is used only when the shapes are read. To read the shapes again,
        empty them (``undercut.options.shapes = {}``) and rebuild while the source exists.
        ``bind=True`` empties ``shapes``.

    Paths:
        A ``path`` stays a path, ``2*width`` wider and ``width`` longer at both ends, so the
        GDS renderer rounds its corners (``fillet``) exactly as those of the source trace.

    Names of the source shapes:
        The names for ``names`` are in the qgeometry tables of the source component::

            T = design.components['T']
            T.qgeometry_table('poly')[['name', 'layer', 'subtract', 'helper']]
            T.qgeometry_table('path')[['name', 'layer', 'subtract', 'width']]
            list(T.qgeometry_dict('poly'))      # names only; the same for 'path'

        Only the rows with ``subtract=False`` can be used. A name that the source does not
        have raises an error, which lists the names the source has.

    .. meta::
        :description: Undercut of a component

    Default Options:
        * component: '' -- Name of the source component
        * width: '0.3um' -- Undercut width: the distance by which every shape is grown
        * layer: '4' -- Layer of the undercut
        * names: '' -- Source shapes to grow, e.g. 'pad_top,pad_bot' or ['pad_top', 'pad_bot'];
          '' (or None, []) takes all shapes with subtract=False
        * bind: 'True' -- True: read the shapes from the source at every rebuild;
          False: read them once and keep them in ``shapes``
        * shapes: Dict() -- Shapes kept with bind=False, filled at the first build:
          Dict(poly=Dict(name=Dict(geometry=WKT)), path=Dict(name=Dict(geometry=WKT, width, fillet)))
        * pos_x, pos_y, orientation, chip -- Position of the undercut and chip, as for any
          component; taken from the source when not given

    Values (unless noted) are strings with units included, (e.g., '30um')

    Example:
        Undercut of the two pads of the transmon 'T' and of the trace of the route 'reso'::

            Undercut(design, 'T_undercut', options=dict(component='T', width='0.3um', layer=4,
                                                        names='pad_top,pad_bot'))
            Undercut(design, 'reso_undercut', options=dict(component='reso', width='0.3um',
                                                           layer=4, names='trace'))

        Undercut that does not need its source any more, for copies of a prototype::

            Undercut(design, 'T_undercut', options=dict(component='T', names='pad_top,pad_bot',
                                                        bind=False))
            # copy 'T' and 'T_undercut' together and move the copies, then
            design.delete_component('T_undercut')
            design.delete_component('T')
    """

    component_metadata = Dict(short_name='undercut', _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(component='', width='0.3um', layer='4', names='', bind='True', shapes=Dict())
    """Default drawing options"""

    TOOLTIP = """The metal shapes of another component, grown by a given width"""

    def __init__(self, design, name=None, options=None, **kwargs):
        """Same as for any QComponent. The pos_x, pos_y, orientation and chip that are not
        given are taken from the source component, so the undercut is placed on it."""
        options = Dict(options or {})
        if options.get('component') in design.components:
            source = design.components[options['component']]
            x, y, angle = self.source_frame(source)
            for key, value in (('pos_x', f'{x}mm'), ('pos_y', f'{y}mm'), ('orientation', f'{angle}'),
                               ('chip', source.options.chip)):
                options.setdefault(key, value)
        super().__init__(design, name, options=options, **kwargs)

    @staticmethod
    def source_frame(source):
        """Frame the source is drawn in: (x, y) in mm and orientation in degrees.

        Its pos_x, pos_y and orientation; for a route, which is drawn between pins,
        the middle and the normal of its start pin.
        """
        if isinstance(source, QRoute):
            pin = source.pins['start']
            return pin['middle'][0], pin['middle'][1], np.degrees(np.arctan2(*pin['normal'][::-1]))
        return source.p.pos_x, source.p.pos_y, source.p.orientation

    def source_shapes(self):
        """The chosen metal shapes of the source, relative to its frame, before they are grown.

        Returns:
            Dict: in the format of the option ``shapes``
        """
        source = self.design.components[self.options.component]
        if source is None:
            raise ValueError(f'{self.name}: source component {self.options.component!r} does not exist')
        rows = [(table, row) for table in ('poly', 'path')
                for _, row in source.qgeometry_table(table).iterrows()
                if not row['subtract']]                                      # metal shapes only
        names = self.options.names or ''                                     # None, '', [] -> all
        names = [n.strip() for n in (names.split(',') if isinstance(names, str) else names) if n.strip()]
        missing = set(names) - {row['name'] for _, row in rows}
        if missing or not rows:
            raise ValueError(f'{source.name}: no metal shapes {sorted(missing)}; '
                             f'it has {[row["name"] for _, row in rows]}')

        x0, y0, angle0 = self.source_frame(source)
        shapes = Dict(poly=Dict(), path=Dict())
        for table, row in rows:
            if names and row['name'] not in names:
                continue
            local = draw.rotate(draw.translate(row['geometry'], -x0, -y0), -angle0, origin=(0, 0))
            shapes[table][row['name']] = Dict(geometry=wkt.dumps(local, rounding_precision=12, trim=True))
            if table == 'path':
                shapes[table][row['name']].update(width=float(row['width']), fillet=float(row['fillet']))
        return shapes

    def make(self):
        """Build the undercut from the source (bind=True) or from the kept shapes (bind=False)."""
        if is_true(self.options.bind):
            shapes = self.source_shapes()
            self.options.shapes = Dict()
        else:
            if not self.options.shapes:
                self.options.shapes = self.source_shapes()
            shapes = self.options.shapes

        p, u = self.p, self.p.width
        for table, entries in shapes.items():
            for name, entry in entries.items():
                shape = draw.rotate(wkt.loads(entry['geometry']), p.orientation, origin=(0, 0))
                shape = draw.translate(shape, p.pos_x, p.pos_y)             # source frame -> own frame
                if table == 'poly':
                    self.add_qgeometry('poly', {name: shape.buffer(u)}, layer=p.layer)
                else:
                    c = np.array(shape.coords)
                    for end, prev in ((0, 1), (-1, -2)):                # extend both ends by u
                        c[end] += u * (c[end] - c[prev]) / np.linalg.norm(c[end] - c[prev])
                    self.add_qgeometry('path', {name: LineString(c)}, width=float(entry['width']) + 2 * u,
                                       fillet=float(entry['fillet']), layer=p.layer)
                    