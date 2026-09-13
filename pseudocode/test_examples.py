# -*- coding: utf-8 -*-
"""Check the Python transcription against the worked examples Mathcad stored
in the worksheets themselves."""
import sys, io

import constants as K
import lumped as LU
import wires as W
import microstrip as MS
import stripline as SL
import resistance as R

CASES = []


def chk(label, got, want, tol=1e-9):
    CASES.append((label, got, want, tol))


# --- CONSTANT.mcd ---------------------------------------------------------
chk('E0_INCHES', K.E0_INCHES, 2.2489159999999998e-13)
chk('U0_INCHES', K.U0_INCHES, 3.19185813604723e-08)
chk('U0_INCHES/(2pi)', K.L_COEFF, 5.08e-09, 1e-3)
chk('C_INCHES', K.C_INCHES, 11803149606.299213)
chk('1e12/C_INCHES', K.PDLY_LIGHT_PS_PER_IN, 84.723148765843888)

# --- CAPAC.mcd ------------------------------------------------------------
chk('XCF(100pF,100MHz)', LU.XCF(100 * 10 ** -12, 10 ** 8), 15.915494309189537)
chk('XCR(100pF,5ns)', LU.XCR(100 * 10 ** -12, 5 * 10 ** -9), 15.915494309189533)

# --- CIRCULAR.mcd ---------------------------------------------------------
chk('LCIRC(.01,1.3)', LU.LCIRC(.01, 1.3), 1.0032467312050629e-07)
chk('LCIRC(.1,1.3)', LU.LCIRC(.1, 1.3), 5.3628247434587034e-08)
chk('XLF(100nH,100MHz)', LU.XLF(100 * 10 ** -9, 10 ** 8), 62.831853071795862)
chk('XLT(100nH,5ns)', LU.XLT(100 * 10 ** -9, 5 * 10 ** -9), 62.831853071795862)

# --- ROUND.mcd ------------------------------------------------------------
D, X, H = .01, 2.000, .100
chk('ZROUND', W.ZROUND(D, H), 221.33276724683617)
chk('LROUND(D,H,X)', W.LROUND(D, H, X), 3.7479015253797596e-08)
chk('LROUND(D,H,X)*1e9', W.LROUND(D, H, X) * 10 ** 9, 37.4790152537976)
chk('LROUND(D,H,1)', W.LROUND(D, H, 1), 1.8739507626898798e-08)
chk('CROUND(D,H,X)', W.CROUND(D, H, X), 7.6608629670681425e-13)
chk('CROUND(D,H,X)*1e12', W.CROUND(D, H, X) * 10 ** 12, 0.76608629670681427)
chk('CROUND(D,H,1)', W.CROUND(D, H, 1), 3.8304314835340713e-13)

# --- COAX.mcd -------------------------------------------------------------
D1, D2, X, er = .01, .1, 20.000, 2.2
chk('ZCOAX', W.ZCOAX(D1, D2, er), 93.144153180389836)
chk('LCOAX(D1,D2,X)', W.LCOAX(D1, D2, X), 2.3394264544819505e-07)
chk('LCOAX(D1,D2,X)*1e9', W.LCOAX(D1, D2, X) * 10 ** 9, 233.94264544819504)
chk('LCOAX(D1,D2,1)', W.LCOAX(D1, D2, 1), 1.1697132272409754e-08)
chk('CCOAX(D1,D2,er,X)', W.CCOAX(D1, D2, er, X), 2.6943629657277744e-11)
chk('CCOAX(D1,D2,er,X)*1e12', W.CCOAX(D1, D2, er, X) * 10 ** 12, 26.943629657277743)
chk('CCOAX(D1,D2,er,1)', W.CCOAX(D1, D2, er, 1), 1.3471814828638871e-12)

# --- TWIST.mcd ------------------------------------------------------------
D, X, S, er = .02, 2.000, .038, 2.5
chk('ZTWIST', W.ZTWIST(D, S, er), 101.31945719108722)
chk('LTWIST(D,S,X)', W.LTWIST(D, S, X), 2.7127221676001153e-08)
chk('LTWIST(D,S,X)*1e9', W.LTWIST(D, S, X) * 10 ** 9, 27.127221676001152)
chk('LTWIST(D,S,1)', W.LTWIST(D, S, 1), 1.3563610838000576e-08)
chk('CTWIST(D,S,er,X)', W.CTWIST(D, S, er, X), 2.6460653013906885e-12)
chk('CTWIST(D,S,er,1)', W.CTWIST(D, S, er, 1), 1.3230326506953442e-12)

# --- MSTRIP.mcd -----------------------------------------------------------
H, Wd, T, X, er = .006, .008, .00137, 11.000, 4.5
chk('ZMSTRIP', MS.ZMSTRIP(H, Wd, T, er), 56.4434757473894)
chk('LMSTRIP(H,W,T,X)', MS.LMSTRIP(H, Wd, T, X), 9.3400757344533228e-08)
chk('LMSTRIP(H,W,T,X)*1e9', MS.LMSTRIP(H, Wd, T, X) * 10 ** 9, 93.400757344533233)
chk('LMSTRIP(H,W,T,1)', MS.LMSTRIP(H, Wd, T, 1), 8.4909779404121116e-09)
chk('CMSTRIP(H,W,T,er,X)', MS.CMSTRIP(H, Wd, T, er, X), 2.9317227617246377e-11)
chk('CMSTRIP(H,W,T,er,1)', MS.CMSTRIP(H, Wd, T, er, 1), 2.6652025106587616e-12)

alpha = MS.ZMSTRIP_TOL(.007, .002, .011, .002, .0022, 4.5, .1)
for i, want in enumerate([64.786784392070174, 51.372408178485863, 37.926663287015465]):
    chk('ZMSTRIP_TOL[%d]' % i, alpha[i], want)
for i, want in enumerate([-0.12881957161169236, -0.013538281305002351, 0.13731143957520631]):
    chk('MS REFL[%d]' % i, MS.REFL(alpha, 50)[i], want)

# --- SLINE.mcd ------------------------------------------------------------
B, Wd, T, X, er = .020, .006, .00137, 11.000, 4.5
chk('ZSTRIP', SL.ZSTRIP(B, Wd, T, er), 51.437079595177309)
chk('LSTRIP(B,W,T,X)', SL.LSTRIP(B, Wd, T, X), 1.0168600660829638e-07)
chk('LSTRIP(B,W,T,X)*1e9', SL.LSTRIP(B, Wd, T, X) * 10 ** 9, 101.68600660829638)
chk('LSTRIP(B,W,T,1)', SL.LSTRIP(B, Wd, T, 1), 9.2441824189360338e-09)
chk('CSTRIP(B,W,T,er,X)', SL.CSTRIP(B, Wd, T, er, X), 3.8433380552099893e-11)
chk('CSTRIP(B,W,T,er,1)', SL.CSTRIP(B, Wd, T, er, 1), 3.4939436865545359e-12)

alpha = SL.ZOFF_TOL(.007, .002, .032, .002, .008, .002, .0015, 4.5, .1)
for i, want in enumerate([64.056647305279526, 51.726315927621933, 39.2280294542347]):
    chk('ZOFF_TOL[%d]' % i, alpha[i], want)
for i, want in enumerate([-0.1232426836785414, -0.016970200010488958, 0.12072406632369118]):
    chk('SL REFL[%d]' % i, SL.REFL(alpha, 50)[i], want)

# --- RESIST.mcd (round-trip checks; the sheet has no stored results) ------
chk('DIAMETER(30)', R.DIAMETER(30), 0.01, 1e-12)
chk('AWG(.01)', R.AWG(.01), 30.0, 1e-12)
chk('AWG(DIAMETER(24))', R.AWG(R.DIAMETER(24)), 24.0, 1e-12)
chk('THICKNESS(1)', R.THICKNESS(1), 0.00137, 1e-12)
chk('CPW(.00137)', R.CPW(.00137), 1.0, 1e-12)

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    bad = 0
    for label, got, want, tol in CASES:
        rel = abs(got - want) / (abs(want) if want else 1)
        ok = rel <= tol
        if not ok:
            bad += 1
            print('FAIL %-24s got %r want %r (rel %.3g)' % (label, got, want, rel))
    print('%d/%d worked examples reproduced' % (len(CASES) - bad, len(CASES)))
    sys.exit(1 if bad else 0)
