from pycircuit.layers import Layers, Layer, Materials
from pycircuit.outline import OutlineDesignRules
from pycircuit.traces import TraceDesignRules
from pycircuit.pcb import PcbAttributes


def oshpark_4layer():
    '''Design rules for a OSHPark 4-layer board

       layer stackup:
       1.0 mil (0.0254mm)    solder resist    +/-0.2mil (0.0051mm)
       1.4 mil (0.0356mm)    1 oz copper
       6.7 mil (0.1702mm)    FR408 prepreg    +/-.67mil (0.017mm)
       0.7 mil (0.0178mm)    0.5 oz copper
        47 mil (1.1938mm)    FR408 core       +/-4.7mil (0.1194mm)
       0.7 mil (0.0178mm)    0.5 oz copper
       6.7 mil (0.1702mm)    FR408 prepreg    +/-.67mil (0.017mm)
       1.4 mil (0.0356mm)    1 oz copper
       1.0 mil (0.0254mm)    solder resist    +/-0.2mil (0.0051mm)

       outline design rules:
       min_drill_size  = 10mil (0.254mm)
       min_slot_width  = 100"  (1.7272mm)
       min_cutout_size = 100"  (1.7272mm)

       net design rules:
       min_trace_width     =  5mil (0.127mm)
       min_clearance       =  5mil (0.127mm)
       min_via_drill       = 10mil (0.254mm)
       min_annular_ring    =  4mil (0.1016mm)
       min_edge_clearance  = 15mil (0.381mm)
    '''

    layers = Layers([
        Layer('silk_top', None, Materials.SilkScreen),
        Layer('finish_top', None, Materials.ENIG),
        Layer('mask_top', 0.0254, Materials.PurpleSolderMask),

        Layer('top', 0.0356, Materials.Cu),
        Layer('sub_outer1', 0.1702, Materials.FR408),

        Layer('inner1', 0.0178, Materials.Cu),
        Layer('sub_inner', 1.1938, Materials.FR408),
        Layer('inner2', 0.0178, Materials.Cu),

        Layer('sub_outer2', 0.1702, Materials.FR408),
        Layer('bottom', 0.0356, Materials.Cu),

        Layer('mask_bottom', 0.0254, Materials.PurpleSolderMask),
        Layer('finish_bottom', None, Materials.ENIG),
        Layer('silk_bottom', None, Materials.SilkScreen),
    ])

    outline_design_rules = OutlineDesignRules(
        min_drill_size  = 0.254,
        min_slot_width  = 1.7272,
        min_cutout_size = 1.7272
    )

    trace_design_rules = TraceDesignRules(
        min_width            = 0.127,
        min_clearance        = 0.127,
        min_drill            = 0.254,
        min_annular_ring     = 0.1016,
        min_edge_clearance   = 0.381,
        blind_vias_allowed   = False,
        burried_vias_allowed = False
    )

    cost_cm2 = 1.5
    return PcbAttributes(layers, outline_design_rules,
                         trace_design_rules, cost_cm2)


def oshpark_2layer():
    '''Design rules for a OSHPark 2-layer board

       layer stackup:
       1.0 mil (0.0254mm)    solder resist    +/-0.2mil (0.00508mm)
       1.4 mil (0.0356mm)    1 oz copper
        60 mil (1.5240mm)    core             +/-6.0mil (0.1524mm)
       1.4 mil (0.0356mm)    1 oz copper
       1.0 mil (0.0254mm)    solder resist    +/-0.2mil (0.00508mm)

       outline design rules:
       min_drill_size  = 10mil (0.254mm)
       min_slot_width  = 100"  (1.7272mm)
       min_cutout_size = 100"  (1.7272mm)

       net design rules:
       min_trace_width     =  6mil (0.1524mm)
       min_clearance       =  6mil (0.1524mm)
       min_via_drill       = 10mil (0.254mm)
       min_annular_ring    =  5mil (0.127mm)
       min_edge_clearance  = 15mil (0.381mm)
    '''

    layers = Layers([
        Layer('silk_top', None, Materials.SilkScreen),
        Layer('finish_top', None, Materials.ENIG),
        Layer('mask_top', 0.0254, Materials.PurpleSolderMask),

        Layer('top', 0.0356, Materials.Cu),
        Layer('substrate', 1.5240, Materials.FR4),
        Layer('bottom', 0.0356, Materials.Cu),

        Layer('mask_bottom', 0.0254, Materials.PurpleSolderMask),
        Layer('finish_bottom', None, Materials.ENIG),
        Layer('silk_bottom', None, Materials.SilkScreen),
    ])

    outline_design_rules = OutlineDesignRules(
        min_drill_size  = 0.254,
        min_slot_width  = 1.7272,
        min_cutout_size = 1.7272
    )

    trace_design_rules = TraceDesignRules(
        min_width            = 0.1524,
        min_clearance        = 0.1524,
        min_drill            = 0.254,
        min_annular_ring     = 0.127,
        min_edge_clearance   = 0.381,
        blind_vias_allowed   = False,
        burried_vias_allowed = False
    )

    cost_cm2 = 0.75
    return PcbAttributes(layers, outline_design_rules,
                         trace_design_rules, cost_cm2)
