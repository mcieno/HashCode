def sizes(num):

    def factor(x):
        for d in range(1, x // 2 + 1):
            if x % d == 0:
                yield d
        yield num

    for div in factor(num):
        yield (div, num // div)


def mask(mat, max_r, max_c, min_m, min_t, row, col, combs, ignore):
    """Try to cut a slice of pizza for all given slices combinations and returns
    the (height, width) pair satisfying the constraints on the ingredients.

    Args:
        mat: Matrix of characters, or list of strings, representing the pizza.
        max_r: Height of the pizza.
        max_c: Width of the pizza.
        min_m: Minimum amount of mushrooms in a slice.
        min_t: Minimum amount of tomatoes in a slice.
        row: Vertical index of the top-left piece of the slice.
        col: Horizontal index of the top-left piece of the slice.
        combs: List of tuples (height, width) of the slices to test.
        ignore: Boolean matrix with max_r rows and max_c columns whose element
            (i, j) is True if and only if the piece of pizza at (i, j) belongs
            to another slice.
    Returns:
          Tuple object (height, width) of the slice satisfying the constraints
          on the ingredients whose top-left element is the one given.
          None in case no slice is valid.
    """
    for comb in combs:
        h, w = comb
        abort = False
        hovering = []
        tomatoes = 0
        mushrooms = 0
        if row + h > max_r or col + w > max_c:
            continue
        for r in range(row, row + h):
            for c in range(col, col + w):
                if ignore[r][c] is True:
                    abort = True
                    break
                hovering.append((r, c))
                if mat[r][c] == 'T':
                    tomatoes += 1
                else:
                    mushrooms += 1
            if abort is True:
                break
        if abort is True:
            continue
        if tomatoes >= min_t and mushrooms >= min_m:
            for y, x in hovering:
                ignore[y][x] = True
            return comb
    return None


def grow(s, limit, max_r, max_c, ignore):
    """Grow a slice of pizza in each direction while possible.

    Args:
        s: Slice of pizza to expand.
        limit: Maximum amount of pieces a slice can be made of.
        max_r: Height of the pizza.
        max_c: Width of the pizza.
        ignore: Boolean matrix with max_r rows and max_c columns whose element
            (i, j) is True if and only if the piece of pizza at (i, j) belongs
            to another slice.
    """
    growable = True
    s_i, s_j = s['idx']
    s_h, s_w = s['siz']
    while growable:
        growable = False
        if s_i > 0 and \
                (s_h + 1) * s_w <= limit and \
                all(ignore[s_i - 1][s_j + k] is False for k in range(s_w)):
            s_i -= 1
            s_h += 1
            growable = True
        if s_j > 0 and \
                s_h * (s_w + 1) <= limit and \
                all(ignore[s_i + k][s_j - 1] is False for k in range(s_h)):
            s_j -= 1
            s_w += 1
            growable = True
        if s_i + s_h < max_r and \
                (s_h + 1) * s_w <= limit and \
                all(ignore[s_i + s_h][s_j + k] is False for k in range(s_w)):
            s_h += 1
            growable = True
        if s_j + s_w < max_c and \
                s_h * (s_w + 1) <= limit and \
                all(ignore[s_i + k][s_j + s_w] is False for k in range(s_h)):
            s_w += 1
            growable = True

    for r in range(s_h):
        for c in range(s_w):
            ignore[s_i + r][s_j + c] = True

    return {'idx': (s_i, s_j), 'siz': (s_h, s_w)}


def main():
    """Reads pizza's data from file specified in command line and finds a
    solution to the cutting problem.

    Algorithm:
        1. Given the minimum and maximum size a single slice can have, build a
            list of lists of tuples (height, width) specifying all the possible
            vertical and horizontal size a slice could have.
        2. For each cell of the pizza matrix, try to fit a slice satisfying the
            constraints. Give priority to small slices.
        3. For each slice found, expand it, if possible, on all 4 directions.
    """
    import sys

    if len(sys.argv) < 2:
        sys.stderr.write('Filename missing\n')
        sys.exit()

    with open(sys.argv[1], 'r') as fi:
        pizza = [line.strip() for line in fi]

    rows, cols, min_pieces, max_pieces = [int(x) for x in pizza.pop(0).split()]

    all_combs = [[x for x in sizes(piece)] for piece in range(2 * min_pieces, max_pieces + 1)]

    slices = []
    already = [[False] * cols for _ in range(rows)]

    for i in range(rows):
        j = 0
        while j < cols:
            for combs in all_combs:
                x = mask(pizza, rows, cols, min_pieces, min_pieces, i, j, combs, already)
                if x is not None:
                    slices.append({'idx': (i, j), 'siz': x})
                    break
            j += 1
            while j < cols and already[i][j] is True:
                j += 1

    for i in range(len(slices)):
        slices[i] = grow(slices[i], max_pieces, rows, cols, already)
    
    print(len(slices))
    for s in slices:
        print(s['idx'][0], s['idx'][1], s['idx'][0] + s['siz'][0] - 1, s['idx'][1] + s['siz'][1] - 1)


if __name__ == '__main__':
    main()
