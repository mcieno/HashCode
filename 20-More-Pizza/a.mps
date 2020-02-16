* Problem:    Subset Sum: A - example
* Class:      MIP
* Rows:       1
* Columns:    4 (4 integer, 4 binary)
* Non-zeros:  4
* Format:     Fixed MPS
*
NAME
ROWS
 N  R0000000
 L  r.5
COLUMNS
    M0000001  'MARKER'                 'INTORG'
    x0        R0000000            -2   r.5                  2
    x1        R0000000            -5   r.5                  5
    x2        R0000000            -6   r.5                  6
    x3        R0000000            -8   r.5                  8
    M0000002  'MARKER'                 'INTEND'
RHS
    RHS1      r.5                 17
BOUNDS
 UP BND1      x0                   1
 UP BND1      x1                   1
 UP BND1      x2                   1
 UP BND1      x3                   1
ENDATA
