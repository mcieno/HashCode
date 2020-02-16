#!/usr/bin/env bash
# The proposed problem can be viewed as a subset-sum optimization problem.
# There are many subset-sum solvers out there. Also, one could easily write
# an FPTAS for subset-sum in case an exact solution is taking too much time.
# However, one could rewrite this as an ILP problem throw it to any linear
# solver, e.g. lp_solve (http://lpsolve.sourceforge.net/5.5/).
#
# For example, given the instance:
#
# ```
# 17 4
# 2 5 6 8
# ```
#
# the optimization problem is
#
# ```
# Maximize 
#   2*x0 + 5*x1 + 6*x2 + 8*x3
# Subject to
#   2*x0 + 5*x1 + 6*x2 + 8*x3 <= 17
# Binaries
#   x0  x1  x2  x3
# ```

echo '[*] Solving a.mps'
lp_solve -mps a.mps | tee a.sol.tmp
rm -f out/a.out
cat a.sol.tmp | grep -c -E "^x(\d*).*1$" >> out/a.out
cat a.sol.tmp | sed -E "/^x(\d*).*1$/!d" | cut -c2- | cut -d ' ' -f 1 | tr '\n' ' ' >> out/a.out
rm -f a.sol.tmp

echo '[*] Solving b.mps'
lp_solve -mps b.mps | tee b.sol.tmp
rm -f out/b.out
cat b.sol.tmp | grep -c -E "^x(\d*).*1$" >> out/b.out
cat b.sol.tmp | sed -E "/^x(\d*).*1$/!d" | cut -c2- | cut -d ' ' -f 1 | tr '\n' ' ' >> out/b.out
rm -f b.sol.tmp

echo '[*] Solving c.mps'
lp_solve -mps c.mps | tee c.sol.tmp
rm -f out/c.out
cat c.sol.tmp | grep -c -E "^x(\d*).*1$" >> out/c.out
cat c.sol.tmp | sed -E "/^x(\d*).*1$/!d" | cut -c2- | cut -d ' ' -f 1 | tr '\n' ' ' >> out/c.out
rm -f c.sol.tmp

echo '[*] Solving d.mps'
lp_solve -mps d.mps | tee d.sol.tmp
rm -f out/d.out
cat d.sol.tmp | grep -c -E "^x(\d*).*1$" >> out/d.out
cat d.sol.tmp | sed -E "/^x(\d*).*1$/!d" | cut -c2- | cut -d ' ' -f 1 | tr '\n' ' ' >> out/d.out
rm -f d.sol.tmp

echo '[*] Solving e.mps'
lp_solve -mps e.mps | tee e.sol.tmp
rm -f out/e.out
cat e.sol.tmp | grep -c -E "^x(\d*).*1$" >> out/e.out
cat e.sol.tmp | sed -E "/^x(\d*).*1$/!d" | cut -c2- | cut -d ' ' -f 1 | tr '\n' ' ' >> out/e.out
rm -f e.sol.tmp

echo '[+] All done'
