import numpy as np

from .taper import Taper
from .patch import Patch
from .junction_manhattan_cross import JunctionManhattan_cross

def manhattan_complete(design, name, x, y, JJ_width, taper_gap, evaporation_shift, undercut,
                       slope, length, shifts_visual=False, sym=True, slope_l=None, length_l=None,
                       crossing=None, patch_edge=None, layer_JJ=3, layer_undercut=4, layer_patch=42):
    """
       Create the complete set of elements for a Manhattan JJ:
       two tapers (only pieces with linear edges!!!) and the JJ cross.

       All lengths are strings parsed by Qiskit Metal, like '0.2um',
       '1um + 50nm' or a design variable name. The elements get plain numbers in mm.

       Parameters:

       design : Metal design
       name : core name for JJ elements
       x, y : center position
       JJ_width : width of the cross (sq root of JJ area)
       taper_gap : gap between tapers
       evaporation_shift : shift of picture due to the resist
       undercut : undercut width (for liftoff)

       # taper parameters
       slope : line slope at the JJ side (number)
       length : taper length excluding crossing
       shifts_visual : add shifted versions of tapers to check compensations (default False)
       sym : if tapers are the same (default True)
       slope_l : slope of the lower taper (number, only for sym=False)
       length_l : length of the lower taper (only for sym=False) excluding crossing
       crossing : width of the taper part which crosses with the big pad (like Nb one) 
                  (default 3*undercut + evaporation_shift/sqrt(2))
       patch_edge : distance between patch edge and taper edge (default evaporation_shift)

       # layers and data types
       layer_JJ : default = 3
       layer_undercut : default = 4
       layer_patch : default = 42

       Returns:
       elements : list of names of the created elements

       Example:
       manhattan_complete(design, 'Q1', x='1.2mm', y='-300um', JJ_width='200nm',
                          taper_gap='1um', evaporation_shift='0.4um', undercut='0.3um',
                          slope=0.5, length='2um')
    """

    # all lengths -> numbers in mm
    x = design.parse_value(x)
    y = design.parse_value(y)
    JJ_width = design.parse_value(JJ_width)
    taper_gap = design.parse_value(taper_gap)
    evaporation_shift = design.parse_value(evaporation_shift)
    undercut = design.parse_value(undercut)

    if crossing is None:
        crossing = undercut*3 + evaporation_shift/np.sqrt(2)
    else:
        crossing = design.parse_value(crossing)
        
    length = design.parse_value(length) + crossing

    if sym:
        slope_l, length_l = slope, length
    elif slope_l is None or length_l is None:
        raise ValueError('sym=False needs slope_l and length_l')
    else:
        length_l = design.parse_value(length_l) + crossing

    if patch_edge is None:
        patch_edge = evaporation_shift
    else:
        patch_edge = design.parse_value(patch_edge)
    
    elements = []

    def add_taper(side, pos_y, orientation, slope, length):
        # compensating for evaporation shift
        width_mod = evaporation_shift/np.sqrt(2)*(1 - slope)
        width_in = JJ_width*np.sqrt(2) + width_mod
        E = evaporation_shift*(1 + 1/np.sqrt(2))

        L_Nb_hole = 1/2*(width_in + 2*slope*(length - crossing) - width_mod - 2*patch_edge - (1 - slope)*(crossing + E))
        L_Si_hole = np.sqrt(2)*L_Nb_hole/(1 + slope)

        y_Nb_hole = -(width_mod + (1 - slope)*(crossing + E))/2
        x_Nb_hole = length - crossing + evaporation_shift/2/np.sqrt(2) + 3*undercut/2

        y_Si_hole = -(-y_Nb_hole - L_Nb_hole + (L_Si_hole - evaporation_shift/3 - 3/2*undercut)/np.sqrt(2))
        x_Si_hole = length - crossing - (L_Si_hole + evaporation_shift/3 + 3/2*undercut)/np.sqrt(2)

        asym_factor = np.sign(design.parse_value(orientation))

        geometry = dict(pos_x=x - width_mod/2,
                        pos_y=pos_y,
                        orientation=orientation,
                        width_in=width_in,
                        length=length,
                        slope=slope,
                        primitive='True',
                        draw='in',
                        holes = dict(real_hole=dict(pos_x=x_Si_hole, 
                                                    pos_y=y_Si_hole + width_mod*(1 - asym_factor)/2,
                                                    width=3*undercut,
                                                    length=L_Si_hole,
                                                    fillet=undercut/2,
                                                    orientation='-45'),
                                     on_Nb_hole=dict(pos_x=x_Nb_hole, 
                                                     pos_y=y_Nb_hole + width_mod*(1 - asym_factor)/2,
                                                     width=3*undercut,
                                                     length=L_Nb_hole,
                                                     fillet=undercut/2, 
                                                     orientation='0'),
                                    )
                       )

        taper = Taper(design, f'{name}_taper_{side}',
                      options=dict(geometry,
                                   undercut=undercut,
                                   layer=layer_JJ,
                                   layer_undercut=layer_undercut,
                                   primitive='1'))
        elements.append(taper.name)

        if shifts_visual:
            # copies shifted as in the two evaporations, to check the compensation
            for suffix, angle, layer in (('_1', '-45', 111), ('_2', '45', 112)):
                shifted = Taper(design, f'{name}_taper_{side}{suffix}',
                                options=dict(geometry,
                                             evaporation_angle=angle,
                                             evaporation_shift=evaporation_shift,
                                             layer=layer))
                elements.append(shifted.name)

        W = width_in - width_mod - 2*patch_edge + 2*slope*(length + E)
        H = W/(1 + slope)
        
        #  trapezium patch cutted to triangle via hole option
        patch = Patch(design, f'{name}_patch_{side}', 
                      options=dict(pos_x=x, 
                                   pos_y=y + asym_factor*(-H/2 + taper_gap/2 + length + evaporation_shift*(1 + 1/np.sqrt(2))),
                                   orientation = f'{-asym_factor*90}',
                                   width=H,
                                   height=W - 2*H*slope,
                                   height_extra=W,
                                   angles='3',
                                   fillet=undercut,
                                   layer_patch=layer_patch,
                                   ),
                     )
        elements.append(patch.name)

    add_taper('up',  pos_y=y + taper_gap/2, orientation='90',  slope=slope,   length=length)
    add_taper('low', pos_y=y - taper_gap/2, orientation='-90', slope=slope_l, length=length_l)

    # JJ cross
    # guarantee extra length of 400 nm accounting for evaporation shift
    Ljj = JJ_width + taper_gap/np.sqrt(2) + evaporation_shift + 400e-6

    
    JJ = JunctionManhattan_cross(design, f'{name}_JJ',
                                 options=dict(pos_x=x - taper_gap/2,
                                              pos_y=y,
                                              orientation='135',
                                              length=Ljj,
                                              x_cross=taper_gap/np.sqrt(2) + JJ_width/2,
                                              width=JJ_width,
                                              layer=layer_JJ,
                                              undercut='20nm',
                                              undercut_big='20nm',
                                              layer_undercut=layer_undercut))
    elements.append(JJ.name)

    return elements
    