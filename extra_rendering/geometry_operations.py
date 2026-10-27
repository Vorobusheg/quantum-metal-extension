import copy

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
       dx, dy : translation shifts (mm)
       angle : rotation angle in degrees
       pivot : (x, y) – rotation center (mm)

       Returns:
       names : list of elements names
    """
    
    u = design.get_units()
    th = np.deg2rad(angle)
    c, s = np.cos(th), np.sin(th)
    px, py = pivot

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
        x = comp.parse_value(comp.options.pos_x)
        y = comp.parse_value(comp.options.pos_y)
        o = float(comp.options.orientation)
        xn, yn = rot_shift(x, y)
        comp.options.pos_x = f'{xn}{u}'
        comp.options.pos_y = f'{yn}{u}'
        comp.options.orientation = str(o + angle)
        comp.rebuild()

    # pass 2: routes — transform absolute anchors, then rebuild to follow pins
    for comp in routes:
        anchors = comp.options.get('anchors', None)
        if anchors:                       # RouteMixed / anchored variants
            for key in list(anchors.keys()):
                ax, ay = np.asarray(comp.parse_value(anchors[key]), dtype=float)
                anchors[key] = np.array(rot_shift(ax, ay))
        comp.rebuild()
    return names

