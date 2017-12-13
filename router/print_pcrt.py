if __name__ == '__main__':
    import argparse
    import pcrt

    parser = argparse.ArgumentParser()

    parser.add_argument('filename', type=str)

    args, unknown = parser.parse_known_args()

    (width, height), diagonals, nets, constraints, disabled = pcrt.read(args.filename)

    net_coords = {}
    for net in nets:
        for c in net:
            net_coords[c] = True

    const_coords = {}
    for const in constraints:
        for c in const:
            const_coords[c] = True

    dis_coords = []
    for dis in disabled:
        for c in dis:
            dis_coords[c] = True

    print(net_coords)
    print(const_coords)
    print(dis_coords)
    for y in range(height):
        for x in range(width):
            if (x, y) in net_coords:
                print('n', end='')
            elif (x, y) in const_coords:
                print('c', end='')
            elif (x, y) in dis_coords:
                print('d', end='')
            else:
                print(' ', end='')
        print()
