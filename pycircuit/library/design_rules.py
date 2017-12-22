from pycircuit.pcb import Layers, NetClass


def oshpark_4layer():
    '''Design rules for a OSHPark 4-layer board

       track width: 5mil (0.127mm)
       track clearance: 5mil (0.127mm)
       drill: 10mil (0.254mm)
       annular ring: 4mil (0.102mm)

       via diameter: 2 * annular ring + drill = 18mil (0.457mm)
       via clearance: track clearance
    '''

    layers = Layers.four_layer_board(oz_outer=1, oz_inner=0.5)
    net_class = NetClass(segment_width=0.15,
                         segment_clearance=0.15,
                         via_drill=0.25,
                         via_diameter=0.5,
                         via_clearance=0.15)
    cost_cm2 = 1.5
    return layers, net_class, cost_cm2


def oshpark_2layer():
    '''Design rules for a OSHPark 2-layer board

       track width: 6mil (0.152mm)
       track clearance: 6mil (0.152mm)
       drill: 10mil (0.254mm)
       annular ring: 5mil (0.127mm)

       via diameter: 2 * annular ring + drill = 20mil (0.508mm)
       via clearance: track clearance
    '''

    layers = Layers.two_layer_board(oz=1),
    net_class = NetClass(segment_width=0.15,
                         segment_clearance=0.15,
                         via_drill=0.25,
                         via_diameter=0.5,
                         via_clearance=0.15)
    cost_cm2 = 0.75
    return layers, net_class, cost_cm2
