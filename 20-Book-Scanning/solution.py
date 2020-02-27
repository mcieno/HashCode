#!/usr/bin/env python3
import math
import random
import sys

from copy import deepcopy
try:
    from tqdm import tqdm
except ImportError:
    tqdm = list


random.seed(0x3133731337)


def log(*args, x='*'):
    print(f'[{x}] {" ".join(str(s) for s in args)}', file=sys.stderr)


if len(sys.argv) < 2:
    log(f'Usage: ./{sys.argv[0]} INPUT_FILE [OUTPUT_FILE] [PRESOL_FILE]', '-')
    sys.exit(0)

infile = sys.argv[1].strip()
outfile = sys.argv[2].strip() if len(sys.argv) > 2 else infile + '.out'
presolfile = sys.argv[3].strip() if len(sys.argv) > 3 else None

log('Parsing input')
# B             = Number of books
# L             = Number of libraries
# D             = Number of days
#
# B2Profit  [i] = (list[int]) : <Profit of book i>
# B2Libs    [i] = (set{int})  : <Set of libraries containing book i>
# B2Count   [i] = (int)       : <Number of libraries containing book i>
#
# L2Books   [j] = (list[int]) : <List of books inside library j, sorted by decreasing profit>
# L2Delay   [j] = (int)       : <Signup time of library j>
# L2Rate    [j] = (int)       : <Number of books library j can output at once>
# L2Output  [j] = (int)       : <Number of books library j is able to output, considering the time left>
# L2Profit  [j] = (int)       : <Profit of library j, considering the time left>

with open(infile, 'r') as fi:
    # B: num. of books
    # L: num. of libraries
    # D: num. of days
    B, L, D = list(map(int, fi.readline().strip().split()))
    B2Profit = tuple(map(int, fi.readline().strip().split()))
    assert len(B2Profit) == B

    B2Libs = [set() for i in range(B)]
    L2Books = [[] for j in range(L)]
    L2Delay = [0 for j in range(L)]
    L2Rate = [0 for j in range(L)]
    L2Output = [0 for j in range(L)]
    L2Profit = [0 for j in range(L)]

    for j in tqdm(range(L)):
        num_books, signup_time, books_per_day = list(
            map(int, fi.readline().strip().split()))
        L2Delay[j] = signup_time
        L2Rate[j] = books_per_day
        L2Books[j] = sorted(map(int, fi.readline().strip().split()), key=lambda i: -B2Profit[i])
        L2Output[j] = min(num_books, (D - signup_time) * books_per_day)
        L2Profit[j] = sum(B2Profit[i] for i in L2Books[j][:L2Output[j]])
        for i in L2Books[j]:
            B2Libs[i].add(j)

    B2Count = [len(B2Libs[i]) for i in range(B)]
    L2Rate = tuple(L2Rate)
    L2Delay = tuple(L2Delay)

_L2Output = tuple(deepcopy(L2Output))
_L2Profit = tuple(deepcopy(L2Profit))
_L2Books = tuple(deepcopy(L2Books))

# STATISTICS
TOTPROFIT = sum(B2Profit)
MAXPROFIT = max(B2Profit)
MINPROFIT = min(B2Profit)
AVGPROFIT = sum(B2Profit) / B
STDPROFIT = math.sqrt(sum((x - AVGPROFIT)**2 for x in B2Profit) / B)

MAXLIBPROFIT = max(L2Profit)
MINLIBPROFIT = min(L2Profit)
AVGLIBPROFIT = sum(L2Profit) / L
STDLIBPROFIT = math.sqrt(sum((x - AVGLIBPROFIT)**2 for x in L2Profit) / L)

MAXRATE = max(L2Rate)
MINRATE = min(L2Rate)
AVGRATE = sum(L2Rate) / L
STDRATE = math.sqrt(sum((x - AVGRATE)**2 for x in L2Rate) / L)

MAXDELAY = max(L2Delay)
MINDELAY = min(L2Delay)
AVGDELAY = sum(L2Delay) / L
STDDELAY = math.sqrt(sum((x - AVGDELAY)**2 for x in L2Delay) / L)

log((f'Statistics:\n'
     f'       B             = {B}\n'
     f'       L             = {L}\n'
     f'       D             = {D}\n'
     f'       TOTPROFIT     = {TOTPROFIT}\n'
     f'       MAXPROFIT     = {MAXPROFIT}\n'
     f'       MINPROFIT     = {MINPROFIT}\n'
     f'       AVGPROFIT     = {AVGPROFIT}\n'
     f'       STDPROFIT     = {STDPROFIT}\n'
     f'       MAXLIBPROFIT  = {MAXLIBPROFIT}\n'
     f'       MINLIBPROFIT  = {MINLIBPROFIT}\n'
     f'       AVGLIBPROFIT  = {AVGLIBPROFIT}\n'
     f'       STDLIBPROFIT  = {STDLIBPROFIT}\n'
     f'       MAXRATE       = {MAXRATE}\n'
     f'       MINRATE       = {MINRATE}\n'
     f'       AVGRATE       = {AVGRATE}\n'
     f'       STDRATE       = {STDRATE}\n'
     f'       MAXDELAY      = {MAXDELAY}\n'
     f'       MINDELAY      = {MINDELAY}\n'
     f'       AVGDELAY      = {AVGDELAY}\n'
     f'       STDDELAY      = {STDDELAY}\n'))


def sig(x, _min, _max, _std, _L=100):
    '''Weight from 0 to _L, based on min, max and std,
    using a logistic function.
    '''
    if _std == 0 or _max - _min == 0:
        # If data has no variance, it's not worth scoring it
        return .0

    return _L / (1 + math.exp(-(_std / _max) * (x - _min) / (_max - _min)))


def score_selection(selection):
    '''Return the score of a selection, that is a list of pairs:

    ```
    [
      (
       lib_id,
       list_of_books
      ),
      ...
    ]
    ```
    '''
    # No repeated libraries
    assert len(selection) == len(set(list(map(lambda x: x[0], selection))))

    # Discard repeated books
    T = D
    books = set()
    for k in range(len(selection)):
        j = selection[k][0]
        T -= L2Delay[j]
        if T <= 0:
            selection = selection[:k]
            break
        b = sorted(set(selection[k][1]) - books, key=lambda i: -B2Profit[i])[:T * L2Rate[j]]
        books = books.union(b)
        selection[k] = (j, b)

    return selection, sum(B2Profit[i] for i in books)


def input_selection(fname):
    '''Import a pre-solved selection.
    '''
    selection = []
    with open(fname, 'r') as fi:
        nlibs = int(fi.readline())
        for _ in range(nlibs):
            l, _ = list(map(int, fi.readline().strip().split()))
            b = list(map(int, fi.readline().strip().split()))
            selection.append(
                (l, b)
            )
    return score_selection(selection)


# TWEAKABLE PARAMETERS
#   - AA, AAX: Importance of profit
#   - BB, BBX: Importance of scanning speed
#   - CC, CCX: Importance of signup time
#   - SKIP: Importance of keeping the list sorted (=1 to update everytime)
#   - MANY: Libraries to pick without re-sorting. Increase to speed up.
#   - RR: Randomness
#   - NRAND: How many times try to find a better solution via randomization
#   - DEPTH: How many swaps to do for each randomization try

update_alpha = True
update_beta = STDRATE != .0
update_gamma = STDDELAY != .0

# Parameters found with little elbow grease and a prayer
if '/a_' in infile:
    AA, AAX = 1, 1
    BB, BBX = 1, 1
    CC, CCX = 1, 1
    SKIP = 1
    MANY = 1
    # Baseline: 21 (opt)
    RR = 0
    NRAND, DEPTH = 0, 0

elif '/b_' in infile:
    AA, AAX = 1, 1
    BB, BBX = 1, 1
    CC, CCX = 1, 1
    SKIP = 100
    MANY = 100
    # Baseline: 5822900 (opt?)
    RR = 0
    NRAND, DEPTH = 0, 0

elif 'c_' in infile:
    AA, AAX = 2.02, 0
    BB, BBX = .01, 0
    CC, CCX = 2.17, 0
    SKIP = 1
    MANY = 9
    # Baseline: 5689598
    RR = 3
    NRAND, DEPTH = 50, 6

elif '/d_' in infile:
    AA, AAX = 2, 0
    BB, BBX = 0, 0
    CC, CCX = 20, 0
    SKIP = 1
    MANY = 10
    # Baseline: 5029180
    RR = 3
    NRAND, DEPTH = 50, 5

elif '/e_' in infile:
    AA, AAX = 1.5, 0
    BB, BBX = .1, .1
    CC, CCX = 1.75, 0
    SKIP = 98
    MANY = 2
    # Baseline: 5092015
    RR = 0
    NRAND, DEPTH = 500, 15

elif '/f_' in infile:
    AA, AAX = 1.5, 0
    BB, BBX = .1, 0
    CC, CCX = 1.79, 0
    SKIP = 1
    MANY = 1
    # Baseline: 5345656
    RR = 0
    NRAND, DEPTH = 500, 15

else:
    update_alpha = False
    AA, AAX = 1, 1
    BB, BBX = 1, 1
    CC, CCX = 1, 1
    SKIP = 1
    MANY = 1
    RR = 0
    NRAND, DEPTH = 10, 2

log(f'{AA}@{AAX} {BB}@{BBX} {CC}@{CCX} #{SKIP} #{MANY} ${RR} ${NRAND} ${DEPTH}')


if presolfile:
    SELECTION, SCORE = input_selection(presolfile)

else:
    log('Generating greedy solution')
    # Initial sorting of libraries
    LIBRARIES = list(range(L))
    LIBRARIES = sorted(
        LIBRARIES,
        key=lambda j: - (
            + sig(L2Profit[j], MINLIBPROFIT, MAXLIBPROFIT, STDLIBPROFIT)**AA
            + sig(L2Rate[j], MINRATE, MAXRATE, STDRATE)**BB
            - sig(L2Delay[j], MINDELAY, MAXDELAY, STDDELAY)**CC
        )
    )
    ALREADYSCANNED = set()
    remaining_time = D
    SELECTION = []

    for _ in tqdm(range(L)):

        for _ in range(MANY):
            if not LIBRARIES:
                break

            l = LIBRARIES.pop(0)

            if L2Profit[l] == 0:
                continue

            if remaining_time <= L2Delay[l]:
                continue

            remaining_time -= L2Delay[l]
            books = L2Books[l][:L2Output[l]]

            if not books:
                remaining_time += L2Delay[l]
                continue

            ALREADYSCANNED = ALREADYSCANNED.union(books)

            SELECTION.append(
                (l, books)
            )

        if not LIBRARIES:
            break

        for j in range(L):
            # Update data structures
            L2Output[j] = (remaining_time - L2Delay[j]) * L2Rate[j]
            L2Books[j] = sorted(set(L2Books[j]) - ALREADYSCANNED,
                                key=lambda i: -B2Profit[i])
            L2Profit[j] = sum(B2Profit[i] for i in L2Books[j][:L2Output[j]])

        if len(LIBRARIES) % SKIP == 0:
            LIBRARIES = set(LIBRARIES) - set([j for j in range(L) if L2Profit[j] == 0])
            if not LIBRARIES: break

            pp = [L2Profit[j] for j in LIBRARIES]
            MINLIBPROFIT = min(pp)
            MAXLIBPROFIT = max(pp)
            AVGLIBPROFIT = sum(pp) / len(pp)
            STDLIBPROFIT = math.sqrt(sum((x - AVGLIBPROFIT)**2 for x in pp) / len(pp))

            rr = [L2Rate[j] for j in LIBRARIES]
            MINRATE = min(rr)
            MAXRATE = max(rr)
            AVGRATE = sum(rr) / len(rr)
            STDRATE = math.sqrt(sum((x - AVGRATE)**2 for x in rr) / len(rr))

            dd = [L2Delay[j] for j in LIBRARIES]
            MINDELAY = min(dd)
            MAXDELAY = max(dd)
            AVGDELAY = sum(dd) / len(dd)
            STDDELAY = math.sqrt(sum((x - AVGDELAY)**2 for x in dd) / len(dd))

            LIBRARIES = sorted(
                LIBRARIES,
                key=lambda j: - (
                    + RR * random.random()
                    + sig(L2Profit[j], MINLIBPROFIT, MAXLIBPROFIT, STDLIBPROFIT)**(AA**(1 + sig(2 - remaining_time/D, 0, 1, AAX, 2)))
                    + sig(L2Rate[j], MINRATE, MAXRATE, STDRATE)**(BB ** (1 + sig(2 - remaining_time/D, 0, 1, BBX, 2)))
                    - sig(L2Delay[j], MINDELAY, MAXDELAY, STDDELAY)**(CC ** (1 + sig(2 - remaining_time/D, 0, 1, CCX, 2)))
                )
            )

    # Clean up the selection
    SELECTION = [(j, _L2Books[j]) for j, _ in SELECTION]
    SELECTION, SCORE = score_selection(SELECTION)

ALREADYSCANNED = set([i for _, b in SELECTION for i in b])

log((f'Greedy solution:\n'
     f'       Score     = {SCORE}\n'
     f'       Libraries = {round(100 * len(SELECTION)/L, 1):.1f}% = {len(SELECTION)}/{L}\n'
     f'       Books     = {round(100 * len(ALREADYSCANNED)/B, 1):.1f}% = {len(ALREADYSCANNED)}/{B}'))

# RANDOMIZE SOLUTION
def do_swap(selection, k_slow, k_fast=None):
    NEWSELECTION = deepcopy(selection)

    j_slow, b_slow = NEWSELECTION[k_slow]

    j_slow, _ = NEWSELECTION.pop(k_slow)
    NEWSELECTION = [(j, _L2Books[j]) for j, _ in NEWSELECTION]
    NEWSELECTION, NEWSCORE = score_selection(NEWSELECTION)

    NEWALREADYSCANNED = set([i for _, b in NEWSELECTION for i in b])
    selectedlibs = set(list(map(lambda x: x[0], NEWSELECTION)))

    T = D - sum(L2Delay[j] for j in selectedlibs)

    # Push j_slow back and update
    NEWLIBRARIES = set(range(L)) - selectedlibs
    for j in range(L):
        if j in selectedlibs:
            # No need to update already selected libraries
            continue

        L2Books[j] = sorted(
            set(_L2Books[j]) - NEWALREADYSCANNED,
            key=lambda i: -B2Profit[i]
        )[:(T - L2Delay[j]) * L2Rate[j]]

        L2Profit[j] = sum(B2Profit[i] for i in L2Books[j])

        NEWLIBRARIES -= set([j for j in range(L) if L2Profit[j] == 0])

    if NEWLIBRARIES:
        pp = [L2Profit[j] for j in NEWLIBRARIES]
        MINLIBPROFIT = min(pp)
        MAXLIBPROFIT = max(pp)
        AVGLIBPROFIT = sum(pp) / len(pp)
        STDLIBPROFIT = math.sqrt(
            sum((x - AVGLIBPROFIT)**2 for x in pp) / len(pp))

        rr = [L2Rate[j] for j in NEWLIBRARIES]
        MINRATE = min(rr)
        MAXRATE = max(rr)
        AVGRATE = sum(rr) / len(rr)
        STDRATE = math.sqrt(sum((x - AVGRATE)**2 for x in rr) / len(rr))

        dd = [L2Delay[j] for j in NEWLIBRARIES]
        MINDELAY = min(dd)
        MAXDELAY = max(dd)
        AVGDELAY = sum(dd) / len(dd)
        STDDELAY = math.sqrt(sum((x - AVGDELAY)**2 for x in dd) / len(dd))

        NEWLIBRARIES = sorted(
            NEWLIBRARIES,
            key=lambda j: - (
                + sig(L2Profit[j], MINLIBPROFIT, MAXLIBPROFIT, STDLIBPROFIT)**AA
                + sig(L2Rate[j], MINRATE, MAXRATE, STDRATE)**BB
                - sig(L2Delay[j], MINDELAY, MAXDELAY, STDDELAY)**CC
            )
        )

        if k_fast is None:
            k_fast = random.randint(
                0, min(max(10, len(NEWLIBRARIES) // 20), len(NEWLIBRARIES) - 1))

        jj = NEWLIBRARIES.pop(k_fast)
        log(f'Replacing [{k_slow}]: {j_slow} out, {jj} in')
        NEWSELECTION.append((jj, _L2Books[jj]))

        NEWSELECTION = [(j, _L2Books[j]) for j, _ in NEWSELECTION]
        NEWSELECTION, NEWSCORE = score_selection(NEWSELECTION)

        NEWALREADYSCANNED = set([i for _, b in NEWSELECTION for i in b])

    return NEWSELECTION, NEWSCORE, NEWALREADYSCANNED


for nr in range(NRAND):
    NEWSELECTION = SELECTION
    # Do at most DEPTH swaps, if no luck, rollback
    for _ in range(DEPTH):
        k_slow = sorted(
            range(len(NEWSELECTION)),
            key=lambda kk: sum(B2Profit[i] for i in NEWSELECTION[kk][1]) / (
                L2Delay[NEWSELECTION[kk][0]] +
                len(NEWSELECTION[kk][1]) / L2Rate[NEWSELECTION[kk][0]]
            )
        )[random.randint(0, min(max(10, len(NEWSELECTION) // 20), len(NEWSELECTION) - 1))]
        # k_slow = random.randint(0, len(NEWSELECTION) - 1)

        NEWSELECTION, NEWSCORE, NEWALREADYSCANNED = do_swap(NEWSELECTION, k_slow)

        if NEWSCORE > SCORE:
            log((f'{nr}| Got better: {NEWSCORE} > {SCORE}\n'
                f'       Score     = {NEWSCORE}\n'
                f'       Libraries = {round(100 * len(NEWSELECTION)/L, 1):.1f}% = {len(NEWSELECTION)}/{L}\n'
                f'       Books     = {round(100 * len(NEWALREADYSCANNED)/B, 1):.1f}% = {len(NEWALREADYSCANNED)}/{B}'))

            SELECTION = NEWSELECTION
            SCORE = NEWSCORE
            ALREADYSCANNED = NEWALREADYSCANNED
            break

    else:
        if NEWSCORE == SCORE:
            log((f'{nr}| Got same: {NEWSCORE} = {SCORE}\n'
                 f'       Score     = {NEWSCORE}\n'
                 f'       Libraries = {round(100 * len(NEWSELECTION)/L, 1):.1f}% = {len(NEWSELECTION)}/{L}\n'
                 f'       Books     = {round(100 * len(NEWALREADYSCANNED)/B, 1):.1f}% = {len(NEWALREADYSCANNED)}/{B}'))

            SELECTION = NEWSELECTION
            SCORE = NEWSCORE
            ALREADYSCANNED = NEWALREADYSCANNED
        else:
            log(f'{nr}| Not better: {NEWSCORE} < {SCORE}')


log((f'Best solution:\n'
     f'       Score     = {SCORE}\n'
     f'       Libraries = {round(100 * len(SELECTION)/L, 1):.1f}% = {len(SELECTION)}/{L}\n'
     f'       Books     = {round(100 * len(ALREADYSCANNED)/B, 1):.1f}% = {len(ALREADYSCANNED)}/{B}'))

with open(outfile, 'w') as fo:
    fo.write(
        f'{len(SELECTION)}\n' + \
        '\n'.join(
            f'{l} {len(books)}\n' + \
            ' '.join(str(b) for b in books) for l, books in SELECTION
        )
    )

log(f'Solution written to {outfile}')
