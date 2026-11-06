import copy
from numbers import Real
import numpy as np


def copy_group(design, names, suffix='_copy'):
    """
       Copy a set of Qiskit Metal components, remapping route pin references within the group.

       Parameters:
       
       design : Metal design
       names : list of elements names
       suffix : suffix for names in the copy

       Returns:
       new_names : list of elements' copies names
    """

    mapping = {name: name + suffix for name in names}
    new_names = []

    def get_pin_refs(opts):
        """Return the pin dicts ({'component':..., 'pin':...}) found in pin_inputs."""
        pins = opts.get('pin_inputs', {})
        return [v for v in pins.values()
                if isinstance(v, dict) and v.get('component')]

    plain, routed = [], []
    for name in names:
        comp = design.components[name]
        opts = copy.deepcopy(dict(comp.options))
        (routed if get_pin_refs(opts) else plain).append((name, comp, opts))

    # pass 1: endpoint components (qubits, terminations, ...)
    for name, comp, opts in plain:
        type(comp)(design, mapping[name], options=opts)
        new_names.append(mapping[name])

    # pass 2: routes, endpoints remapped to the copies
    for name, comp, opts in routed:
        for pin in get_pin_refs(opts):
            old = pin['component']
            if old in mapping:
                pin['component'] = mapping[old]
            else:
                raise ValueError(
                    f"Route '{name}' connects to '{old}', which is not in the "
                    f"copied group — its pin is already in use by the original. "
                    f"Add '{old}' to the group or retarget the copy manually.")
        type(comp)(design, mapping[name], options=opts)
        new_names.append(mapping[name])

    return new_names


def transform_group(design, names, dx=0.0, dy=0.0, angle=0.0, pivot=(0.0, 0.0)):
    """
       Rigidly translate/rotate a set of instances about a shared pivot.
       QRoutes (meanders etc.) are not moved directly: their anchors (if any)
       are transformed, and they are rebuilt last so they re-route to the
       moved endpoint pins.
 
       Parameters:
 
       design : Metal design
       names : list of elements names
       dx, dy : translation shifts: '10um', '-0.1mm + 5um', a design variable, or a number in mm
       angle : rotation angle in degrees: 90, '90' or a design variable
       pivot : (x, y) – rotation center, each given like dx, dy
 
       Returns:
       names : list of elements names
    """
 
    def num(value, what):
        """Metal parser + check: parse_value does not raise, it returns the input unchanged."""
        v = design.parse_value(value)
        if isinstance(v, bool) or not isinstance(v, Real) or not np.isfinite(v):
            raise ValueError(f'{what}: cannot parse {value!r}')
        return float(v)
 
    dx, dy, angle = num(dx, 'dx'), num(dy, 'dy'), num(angle, 'angle')
    if isinstance(pivot, str):                 # one string, Metal list syntax: "['500um', '-1.5mm']"
        pivot = design.parse_value(pivot)
    px, py = pivot                             # exactly two values
    px, py = num(px, 'pivot x'), num(py, 'pivot y')
 
    th = np.deg2rad(angle)
    c, s = np.cos(th), np.sin(th)
 
    def rot_shift(x, y):
        """Rotate (x, y) about the pivot, then translate by (dx, dy)."""
        xr = px + c * (x - px) - s * (y - py)
        yr = py + s * (x - px) + c * (y - py)
        return xr + dx, yr + dy
 
    def is_route(comp):
        pins = comp.options.get('pin_inputs', {})
        return isinstance(pins, dict) and any(
            isinstance(v, dict) and v.get('component') for v in pins.values())
 
    routes = []
 
    # pass 1: move all non-route components
    for name in names:
        comp = design.components[name]
        if is_route(comp):
            routes.append(comp)
            continue
        x = num(comp.options.pos_x, f'{name}.pos_x')
        y = num(comp.options.pos_y, f'{name}.pos_y')
        o = num(comp.options.orientation, f'{name}.orientation')
        xn, yn = rot_shift(x, y)
        comp.options.pos_x = f'{xn}mm'          # parse_value always returns mm
        comp.options.pos_y = f'{yn}mm'
        comp.options.orientation = str(o + angle)
        comp.rebuild()
 
    # pass 2: routes — transform absolute anchors, then rebuild to follow pins
    for comp in routes:
        anchors = comp.options.get('anchors', None)
        if anchors:                       # RouteMixed / anchored variants
            for key in list(anchors.keys()):
                ax, ay = np.asarray(design.parse_value(anchors[key]), dtype=float)
                anchors[key] = np.array(rot_shift(ax, ay))
        comp.rebuild()
    return names
    