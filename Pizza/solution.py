import sys


def sizes(num):
    """Genera tutte le possibili coppie di numeri interi che formano un
    rettangolo di una certa area.

    Positional arguments:
    num -- area del rettangolo desiderato

    Esempio:
    num = 10
    yield (1, 10), (2, 5), (5, 2), (10, 1)
    """
    def factor(x):
        for d in range(1, x // 2 + 1):
            if x % d == 0:
                yield d
        yield num
    for i in factor(num):
        yield (i, num // i)


def mask(mat, max_r, max_c, count, row, col, combs, ignore):
    """Testa tutte le possibili dimensioni di fetta e ritorna quella che
    soddisfa le condizioni sugli ingredienti, aggiornando di conseguenza
    l'insieme di spicchi gia' impegnati.

    Positional arguments:
    mat -- matrice di 'T' e 'M' rappresentante la pizza.
    max_r -- righe (altezza) della pizza.
    max_c -- colonne (larghezza) della pizza.
    count -- numero minimo di ciascun ingrediente che la fetta deve contenere.
    row -- indice di riga alla quale la fetta inizia (angolo alto sinistro).
    col -- indice di colonna alla quale la fetta inizia (angolo alto sinistro).
    combs -- lista di possibili combinazioni di dimensioni della fetta.
    ignore -- matrice booleana tale che ignore[i][j] == True se e solo se la
              cella (i, j) della pizza e' gia' impegnata in un'altra fetta.

    Returns:
    Combinazione di altezza-larghezza tra quelle presenti in combs
    che individua una fetta con i requisiti richiesti sugli ingredienti.
    Se nessuna combinazione e' soddisfacente, ritorna None.
    """
    # Testa ogni combinazione possibile di dimensione della fetta
    for comb in combs:
        h, w = comb
        # Flag che diventa True se la fetta contiene un pezzo gia' contenuto in
        # un'altra fetta
        abort = False
        # Lista delle coordinate che la fetta attuale occupa
        hovering = []
        # Contatori del numero di ingredienti nella fetta
        tomatoes = 0
        mushrooms = 0
        # Se le dimensioni della fetta eccedono la pizza passa alla prossima
        if row + h > max_r or col + w > max_c:
            continue
        # Controlla tutti i pezzi della fetta attuale e conta quanti ingredienti
        # sono contenuti. Se pero' un pezzo e' gia nella lista delle coordinate
        # gia' impegnate in altre fette imposta il flag a True e passa alla
        # prossima combinazione
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
        # Se la combinazione non andava bene, passa alla prossima
        if abort is True:
            continue
        # La fetta soddisfa i requisiti
        if tomatoes >= count and mushrooms >= count:
            # Aggiorna la matrice dei pezzi da ignorare
            for y, x in hovering:
                ignore[y][x] = True
            # Ritorna la combinazione altezza-larghezza trovata
            return comb
    # Non e' stata trovata alcuna fetta
    return None


def grow(s, limit, max_r, max_c, ignore):
    """Allarga una fetta di pizza finche' possibile e aggiorna l'inieme
    di spicchi gia' impegnati di conseguenza.

    Positional arguments:
    s -- fetta di pizza da allargare.
    limit -- numero massimo di spicchi che la fetta puo' contenere.
    max_r -- righe (altezza) della pizza.
    max_c -- colonne (larghezza) della pizza.
    ignore -- matrice booleana tale che ignore[i][j] == True se e solo se la
              cella (i, j) della pizza e' gia' impegnata in un'altra fetta.

    Returns:
    Fetta di pizza appena allargata.
    """
    # Espandi, finche' possibile, la fetta verso l'alto
    while s['idx'][0] > 0 and \
          (s['siz'][0] + 1) * s['siz'][1] <= limit and \
          all(ignore[s['idx'][0] - 1][s['idx'][1] + k] is not True for k in range(s['siz'][1])):
        s['idx'] = (s['idx'][0] - 1, s['idx'][1])
        s['siz'] = (s['siz'][0] + 1, s['siz'][1])
    # Espandi, finche' possibile, la fetta verso sinistra
    while s['idx'][1] > 0 and \
          s['siz'][0] * (s['siz'][1] + 1) <= limit and \
          all(ignore[s['idx'][0] + k][s['idx'][1] - 1] is not True for k in range(s['siz'][0])):
        s['idx'] = (s['idx'][0], s['idx'][1] - 1)
        s['siz'] = (s['siz'][0], s['siz'][1] + 1)
    # Espandi, finche' possibile, la fetta verso il basso
    while s['idx'][0] + s['siz'][0] < max_r and \
          (s['siz'][0] + 1) * s['siz'][1] <= limit and \
          all(ignore[s['idx'][0] + s['siz'][0]][s['idx'][1] + k] is not True for k in range(s['siz'][1])):
        s['siz'] = (s['siz'][0] + 1, s['siz'][1])
    # Espandi, finche' possibile, la fetta verso destra
    while s['idx'][1] + s['siz'][1] < max_c and \
          s['siz'][0] * (s['siz'][1] + 1) <= limit and \
          all(ignore[s['idx'][0] + k][s['idx'][1] + s['siz'][1]] is not True for k in range(s['siz'][0])):
        s['siz'] = (s['siz'][0], s['siz'][1] + 1)

    # Aggiorna le coordinate da ignorare
    for i in range(s['siz'][0]):
        for j in range(s['siz'][1]):
            ignore[s['idx'][0] + i][s['idx'][1] + j] = True

    return s


if __name__ == '__main__':
    """Algoritmo:

      1. Data la dimensione minima e massima che una fetta puo' avere genera una
      lista di possibili dimensioni che le fette possono assumere:
        Esempio:
          minimo = 5
          massimo = 9
          [
            5: [(1, 5), (5, 1)]
            6: [(1, 6), (2, 3), (3, 2), (6, 1)]
            7: [(1, 7), (7, 1)]
            8: [(1, 8), (2, 4), (4, 2), (8, 1)]
            9: [(1, 9), (3, 3), (9, 1)]
          ]

      2. Per ogni casella si cerca, se esiste, una fetta che soddisfa le
      le condizioni richieste sugli ingredienti (vedi metodo <mask>).
      Si preferiscono fette piccole a fette grandi. Ogni nuova fetta trovate, si
      tiene memoria delle coordinate che essa occupa, cosi' da non avere fette
      che si sovrappongono.

      3. Per ogni fetta trovata, cerca quando possibile, di aumentarne le
      dimensioni, stando attento sia a non eccedere la dimensione massima
      imposta, sia a non sovrapporsi alle fette gia' esistenti (vedi metodo
      <grow>).
    """
    # Per avere piu' informazioni in output
    DEBUG = False

    # Il nome del file viene letto come argomento da riga di comando
    if len(sys.argv) < 2:
        sys.stderr.write('Filename missing\n')
        sys.exit()

    with open(sys.argv[1], 'r') as f:
        pizza = [x.strip() for x in f]

    # DEBUG -- START
    if DEBUG is True:
        sys.stdout.write('Input:\n\n')
        for line in pizza:
            sys.stdout.write('{}\n'.format(line))
        sys.stdout.write('-' * 30 + '\n')
    # DEBUG -- END

    # rows = 'Numero di righe della pizza (altezza)'
    # cols = 'Numero di colonne della pizza (larghezza)'
    # min_pieces = 'Numero minimo di pezzi per ingrediente su ogni fetta'
    # max_pieces = 'Dimensione massima che una fetta puo' avere'
    rows, cols, min_pieces, max_pieces = [int(x) for x in pizza.pop(0).split()]

    # Lista 2-dimensionale. Ogni suo elemento e' una lista delle combinazioni
    # di altezza-larghezza possibili per una fetta di una certa dimensione.
    all_combs = [[x for x in sizes(piece)] for piece in range(2 * min_pieces, max_pieces + 1)]

    # DEBUG -- START
    if DEBUG is True:
        sys.stdout.write('Combinations:\n\n')
        for combs in all_combs:
            sys.stdout.write('{}:\t {}\n'.format(combs[0][0] * combs[0][1], combs))
        sys.stdout.write('-' * 30 + '\n')
    # DEBUG -- END

    # Inizializza la lista delle fette (slices) e una matrice ausiliaria per
    # tenere memoria delle coordinate gia' occupate (already).
    slices = []
    already = [[False] * cols for _ in range(rows)]

    # Per ogni pezzetto di pizza, cerca se esiste una fetta che abbia questo
    # elemento nell'angolo in alto a sinistra e soddisfa le condizioni richieste
    for i in range(rows):
        # Usa un ciclo while per le colonne, cosi' che se avesse appena tagliato
        # una fetta di una certa larghezza possiamo saltare avanti con la
        # ricerca di un numero di colonne maggiore, evitando controlli inutili
        j = 0
        while j < cols:
            # all_combs e un'array di liste, ognuna delle quali contiene le
            # possibili combinazioni di altezza-larghezza per avere una fetta di
            # una certa dimensione. Cerca per ognuna di queste se esiste una
            # fetta valida per quanto riguarda il numero minimo di ingredienti
            for combs in all_combs:
                x = mask(pizza, rows, cols, min_pieces, i, j, combs, already)
                if x is not None:
                    # DEBUG -- START
                    if DEBUG is True:
                        sys.stdout.write('New slice found at {}, size: {}\n'.format((i, j), x))
                    # DEBUG -- END
                    # Aggiunge alla lista slices la fetta appena trovata sotto
                    # forma di dizionario le cui chiavi sono:
                    #  - 'idx': coppia (i, j) delle coordinate dello spicchio in
                    #           alto a sinistra
                    #  - 'siz': coppia (h, w) dell'altezza e larghezza della
                    #           fetta
                    slices.append({'idx': (i, j), 'siz': x})
                    # Rompi il for, in quanto non serve controllare altre
                    # combinazioni, dato che l'abbiamo gia' trovata quella buona
                    break
            # Mediamente l'indice di colonna potra' essere incrementato di
            # quantita' maggiori di 1, questo perche' buona parte della pizza e'
            # gia' occupata da fette. In questo modo le iterazioni saranno meno
            if already[i][j] is not True:
                j += 1
            else:
                while j < cols and already[i][j] is True:
                    j += 1

    # Porva a espandere tutte le fette
    for i in range(len(slices)):
        # DEBUG -- START
        if DEBUG is True:
            sys.stdout.write('About to expand:\n\t{}\n'.format(slices[i]))
        # DEBUG -- END
        # Espandi la fetta in posizione i ed aggiornane il valore nella Lista
        # delle fette
        slices[i] = grow(slices[i], max_pieces, rows, cols, already)
        # DEBUG -- START
        if DEBUG is True:
            sys.stdout.write('\t{}\n'.format(slices[i]))
        # DEBUG -- END

    # Output nel formato richiesto per inviare la soluzione al sistema
    print(len(slices))
    for s in slices:
        print(s['idx'][0], s['idx'][1], s['idx'][0] + s['siz'][0] - 1, s['idx'][1] + s['siz'][1] - 1)

    # DEBUG -- START
    if DEBUG is True:
        sys.stdout.write('{} PIZZA AFTER SLICING {}\n'.format('-' * 10, '-' * 10))
        for row in range(rows):
            for col in range(cols):
                if already[row][col] is True:
                    sys.stdout.write('*')
                else:
                    sys.stdout.write(pizza[row][col])
            sys.stdout.write('\n')
    # DEBUG -- END
