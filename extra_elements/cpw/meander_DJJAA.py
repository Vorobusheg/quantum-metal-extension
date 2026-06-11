# -*- coding: utf-8 -*-

"""File contains dictionary for MeanderInductor and the make()."""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class MeanderDJJAA(QComponent):
    """A Meandering Inductor with a specified overlap length heuristic and height.

    Inherits `QComponent` class.

    Description:
        A meandering inductor.

    Default Options:
        Convention: Values (unless noted) are strings with units included,
        (e.g., '30um')

        * jxn_width: '4um' -- the width of the jxn line
        * loop_side: '6um' -- The side length of the loop
        * extra_jxn_length: '1um' -- Extra length for junctions
        * extra_length_evap: '8um' -- Extra length of junctions for evaporation
        * squids_per_turn: '50' -- Number of SQUIDs in every half turn. Only accepts even numbers
        * squid_separation: '12um' -- Separation between two squids in the same turn
        * turn_separation: '12um' -- Separation between two SQUIDs in the two turns
        * total_turns: '20' -- Total number of full turns (currently can only be an integer)
        * evap_direction: '00' -- Can be 00,01,10,11. First number is up or down (1 for down, 0 for up, so extra_length_evap is given below a vertical line for 1 and above for 0). Second number is left or right (1 for right, 0 for left, so extra_length_evap is given to the right of a horizontal line for 1 and to the left for 0) 
        * extend_begin_length: '20um' -- How much to extend the beginning line to the left
        * extend_end_length: '20um' -- How much to extend the ending line to the right
        * helper: 'False'
    """

    default_options = Dict(jxn_width='4um',
                           loop_side='6um',
                           extra_jxn_length='1um',
                           extra_length_evap='8um',
                           squids_per_turn='50',
                           squid_separation='12um',
                           turn_separation='12um',
                           total_turns='20',
                           evap_direction='11',
                           extend_begin_length='20um',
                           extend_end_length='20um',
                           N_squids_begin = None,
                           N_squids_end = None,
                           helper='False')
    """Default drawing options"""

    TOOLTIP = """A meandering inductor"""

    def make(self):
        """The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed information, such
        as layer, subtract, etc."""
        p = self.p  # p for parsed parameters. Access to the parsed options.
        # Create the geometry

        if 'N_squids_begin' not in self.options or self.options.N_squids_begin is None:
            N_squids_begin = int(p.squids_per_turn)//2
        else:
            N_squids_begin = int(p.N_squids_begin)
        if 'N_squids_end' not in self.options or self.options.N_squids_end is None:
            N_squids_end = int(p.squids_per_turn)//2 + 1
        else:
            N_squids_end = int(p.N_squids_end)

        l_single = p.loop_side + 2*p.extra_jxn_length + p.extra_length_evap

        extension_begin = draw.rectangle(p.extend_begin_length, p.jxn_width, -p.extend_begin_length/2 - (l_single + p.jxn_width)/2 + (float(self.options.evap_direction[1])-0.5)*p.extra_length_evap)

        extension_end = draw.rectangle(p.extend_end_length, p.jxn_width, p.extend_end_length/2 + (l_single + p.jxn_width)/2 + (float(self.options.evap_direction[1])-0.5)*p.extra_length_evap)

        hor_element_bare = draw.rectangle(l_single + p.jxn_width, p.jxn_width, (float(self.options.evap_direction[1])-0.5)*p.extra_length_evap,0.)
        
        ver_element_bare_half = draw.rectangle(p.jxn_width, l_single+p.jxn_width, 0., p.loop_side/2 + (float(self.options.evap_direction[0])-0.5)*p.extra_length_evap)
        ver_element_bare_full = draw.rectangle(p.jxn_width, 2*p.loop_side + 2*p.extra_jxn_length + p.extra_length_evap + p.squid_separation + p.jxn_width, 0., p.loop_side + (float(self.options.evap_direction[0])-0.5)*p.extra_length_evap + p.squid_separation/2)

        if int(p.squids_per_turn) % 2 == 1:
            raise ValueError("Odd number of SQUIDS per turn. Case not handled")

        N_jxns_half = int(p.squids_per_turn//2)
        N_jxns_down_half = int(p.squids_per_turn) - N_jxns_half

        total_turns = int(p.total_turns)

        turn_joiner_up = draw.rectangle(p.turn_separation, p.jxn_width, p.turn_separation + (float(self.options.evap_direction[1])-0.5)*p.extra_length_evap, (N_jxns_half-1)*(p.loop_side + p.squid_separation) + p.loop_side)
        turn_joiner_down = draw.rectangle(p.turn_separation, p.jxn_width, 2*p.loop_side + 1*p.turn_separation + (float(self.options.evap_direction[1])-0.5)*p.extra_length_evap, -N_jxns_down_half*(p.loop_side + p.squid_separation))

        turn_joiner_full = draw.union([turn_joiner_up, turn_joiner_down])

        single_squid_horizontal = draw.union([hor_element_bare, draw.translate(hor_element_bare, 0., p.loop_side)])

        quarter_turn_horizontal_up = draw.union([
            draw.translate(single_squid_horizontal, 0., idx*(p.loop_side + p.squid_separation)) for idx in range(N_jxns_half - N_squids_begin, N_jxns_half)
        ] + [draw.translate(extension_begin, 0., (N_jxns_half - N_squids_begin)*(p.loop_side + p.squid_separation))])

        quarter_turn_vertical_up = draw.union([draw.translate(ver_element_bare_half, -p.loop_side/2 *(-1 if (N_jxns_half - N_squids_begin)%2 else 1), (N_jxns_half - N_squids_begin)*(p.loop_side + p.squid_separation)),
                                               draw.translate(ver_element_bare_half, -p.loop_side/2 *(-1 if N_jxns_half%2 else 1), (N_jxns_half-1)*(p.loop_side + p.squid_separation))] + 
                                              [draw.translate(ver_element_bare_full, (p.loop_side/2)*(-1 if idx%2 else 1),
                                                              idx*(p.loop_side + p.squid_separation)) for idx in range(N_jxns_half - N_squids_begin, N_jxns_half-1)]
                                             )
        quarter_turn_up = draw.union([quarter_turn_horizontal_up, quarter_turn_vertical_up])

        quarter_turn_horizontal_down = draw.union([
            draw.translate(single_squid_horizontal, 0., -(idx+1)*(p.loop_side + p.squid_separation)) for idx in range(N_jxns_half - N_squids_end, N_jxns_down_half)
        ] + [draw.translate(extension_end, 0., (N_squids_end - N_jxns_half - 1)*(p.loop_side + p.squid_separation))])

        quarter_turn_vertical_down = draw.union([draw.translate(ver_element_bare_half, -p.loop_side/2 *(-1 if (N_squids_end - N_jxns_half)%2 else 1), (N_squids_end - N_jxns_half - 1)*(p.loop_side + p.squid_separation)),
                                               draw.translate(ver_element_bare_half, -p.loop_side/2 *(-1 if N_jxns_half%2 else 1), -N_jxns_half*(p.loop_side + p.squid_separation))] + 
                                              [draw.translate(ver_element_bare_full, (p.loop_side/2)*(-1 if idx%2 else 1),
                                                              idx*(p.loop_side + p.squid_separation)) for idx in range(-N_jxns_half,0)]
                                             )
        quarter_turn_down = draw.union([quarter_turn_horizontal_down, quarter_turn_vertical_down])

        half_turn_horizontal = draw.union([
            draw.translate(single_squid_horizontal, 0., idx*(p.loop_side + p.squid_separation)) for idx in range(-N_jxns_down_half, N_jxns_half)
        ])

        half_turn_vertical = draw.union([draw.translate(ver_element_bare_half, -p.loop_side/2, -N_jxns_half*(p.loop_side + p.squid_separation)),
                                               draw.translate(ver_element_bare_half, -p.loop_side/2, (N_jxns_half-1)*(p.loop_side + p.squid_separation))] + 
                                              [draw.translate(ver_element_bare_full, (p.loop_side/2)*(-1 if idx%2 else 1),
                                                              idx*(p.loop_side + p.squid_separation)) for idx in range(-N_jxns_half, N_jxns_half-1)]
                                             )
        half_turn = draw.union([half_turn_horizontal, half_turn_vertical])
        
        all_turns = draw.union([quarter_turn_up] +
                                    [draw.translate(half_turn, idx*(p.loop_side + p.turn_separation), 0) for idx in range(1,2*total_turns)] +
                                    [draw.translate(quarter_turn_down, (2*total_turns)*(p.loop_side + p.turn_separation), 0)] +
                                    [draw.translate(turn_joiner_full, 2*idx*(p.loop_side + p.turn_separation), 0) for idx in range(total_turns)]
                                   )

        all_turns = draw.translate(all_turns, p.extend_begin_length + (1-float(self.options.evap_direction[1]))*p.extra_length_evap, 0.)
        all_turns = draw.rotate(all_turns, p.orientation, origin=(0.,0.))
        all_turns = draw.translate(all_turns, p.pos_x, p.pos_y)
        
        print(f'Total SQUIDs = {(2*p.squids_per_turn-1)*total_turns + N_squids_begin + N_squids_end}')
        
        ##############################################
        # add qgeometry
        self.add_qgeometry('poly', {'array': all_turns},
                           helper=p.helper,
                           layer=p.layer,
                           chip=p.chip)
        