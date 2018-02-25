import sys


def sizes(num):
    """Metodo generatore di possibili coppie di numeri interi che formano un
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


def mask(mat, max_r, max_c, count, coord, combs, ignore):
    """Testa tutte le possibili dimensioni di fetta e ritorna quella che
    soddisfa le condizioni sugli ingredienti, aggiornando di conseguenza
    l'insieme di spicchi gia' impegnati.

    Positional arguments:
    mat -- matrice di 'T' e 'M' rappresentante la pizza.
    max_r -- righe (altezza) della pizza.
    max_c -- colonne (larghezza) della pizza.
    count -- numero minimo di ciascun ingrediente che la fetta deve contenere.
    coord -- cordinata alla quale la fetta inizia (angolo alto sinistro).
    combs -- lista di possibili combinazioni di dimensioni della fetta.
    ignore -- insieme di coordinate degli spicchi gia' impegnati in altre fette.

    Returns:
    Combinazione di altezza-larghezza tra quelle presenti in combs
    che individua una fetta con i requisiti richiesti sugli ingredienti.
    Se nessuna combinazione e' soddisfacente, ritorna None.
    """
    row, col = coord
    # Testa ogni combinazione possibile di dimensione della fetta
    for comb in combs:
        h, w = comb
        # Flag che diventa True se la fetta contiene un pezzo gia' contenuto in
        # un'altra fetta
        abort = False
        # Insieme delle coordinate che la fetta attuale occupa
        hovering = set()
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
                if (r, c) in ignore:
                    abort = True
                    break
                hovering.add((r, c))
                if mat[r][c] == 'T':
                    tomatoes += 1
                else:
                    mushrooms += 1
            if abort is True:
                break
        # Se la fetta soddisfa i requisiti, ritorna la combinazione
        if abort is not True and tomatoes >= count and mushrooms >= count:
            ignore.update(hovering)
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
    ignore -- insieme di coordinate degli spicchi gia' impegnati in altre fette.

    Returns:
    Fetta di pizza appena allargata.
    """
    # Espandi, finche' possibile, la fetta verso l'alto
    while s['idx'][0] > 0 and \
          (s['siz'][0] + 1) * s['siz'][1] <= limit and \
          all((s['idx'][0] - 1, s['idx'][1] + k) not in ignore for k in range(s['siz'][1])):
        s['idx'] = (s['idx'][0] - 1, s['idx'][1])
        s['siz'] = (s['siz'][0] + 1, s['siz'][1])
    # Espandi, finche' possibile, la fetta verso sinistra
    while s['idx'][1] > 0 and \
          s['siz'][0] * (s['siz'][1] + 1) <= limit and \
          all((s['idx'][0] + k, s['idx'][1] - 1) not in ignore for k in range(s['siz'][0])):
        s['idx'] = (s['idx'][0], s['idx'][1] - 1)
        s['siz'] = (s['siz'][0], s['siz'][1] + 1)
    # Espandi, finche' possibile, la fetta verso il basso
    while s['idx'][0] + s['siz'][0] < max_r and \
          (s['siz'][0] + 1) * s['siz'][1] <= limit and \
          all((s['idx'][0] + s['siz'][0], s['idx'][1] + k) not in ignore for k in range(s['siz'][1])):
        s['siz'] = (s['siz'][0] + 1, s['siz'][1])
    # Espandi, finche' possibile, la fetta verso destra
    while s['idx'][1] + s['siz'][1] < max_c and \
          s['siz'][0] * (s['siz'][1] + 1) <= limit and \
          all((s['idx'][0] + k, s['idx'][1] + s['siz'][1]) not in ignore for k in range(s['siz'][0])):
        s['siz'] = (s['siz'][0], s['siz'][1] + 1)

    # Aggiorna le coordinate da ignorare
    hovering = set()
    for i in range(s['siz'][0]):
        for j in range(s['siz'][1]):
            hovering.add((s['idx'][0] + i, s['idx'][1] + j))
    ignore.update(hovering)

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
        quit()

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

    # Inizializza la lista delle fette (slices) e l'insieme delle coordinate
    # gia' occupate, e dunque da ignorare (already).
    slices = []
    already = set()

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
                x = mask(pizza, rows, cols, min_pieces, (i, j), combs, already)
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
                    # Avendo appena aggiunto una fetta, saltiamo abbastanza
                    # colonne, evitando cicli inutili.
                    # Nota: vanno saltate x[1] caselle, dato che fuori da questo
                    #       ciclo viene aggiunto 1 in ogni caso, ne fa saltare
                    #       x[1] - 1, e poi viene riaggiunta l'unita'.
                    j += x[1] - 1
                    # Rompi il for, in quanto non serve controllare altre
                    # combinazioni, dato che l'abbiamo gia' trovata quella buona
                    break
            # I cicli infiniti non ci piacciono
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
                if (row, col) in already:
                    sys.stdout.write('*')
                else:
                    sys.stdout.write(pizza[row][col])
            sys.stdout.write('\n')
    # DEBUG -- END
