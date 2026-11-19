#!/usr/bin/env python3
"""
Crosstalk con pista de guarda + hilera de vías a masa (apantallamiento + via fencing).

'gap' = separación BORDE A BORDE entre las dos pistas [mm].
Por defecto corre gap = 2 y 4 mm:
    python3 simular_crosstalk_via_fencing_y_apantallamiento.py            # 2 y 4 mm
    python3 simular_crosstalk_via_fencing_y_apantallamiento.py 4          # solo 4 mm
    python3 simular_crosstalk_via_fencing_y_apantallamiento.py --hilos 8
    python3 simular_crosstalk_via_fencing_y_apantallamiento.py --completo # 4 puertos, para validar la simetría

Optimizaciones: solo se excita el puerto 1 (resto de S por simetría/reciprocidad),
cobre como lámina PEC de espesor cero, plano de masa como frontera PEC,
malla fina solo dentro del gap y gruesa (2 mm) en el resto.
"""
import argparse
import os
import shutil
import time
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS

MODO = 'ambos'          # 'ninguno' | 'guarda' | 'vias' | 'ambos'
PREFIJO = 'crosstalk_shielded'       # prefijo del archivo .s4p

ap = argparse.ArgumentParser()
ap.add_argument('gaps', type=float, nargs='*', default=[2.0, 4.0],
                help='separaciones borde a borde en mm (default: 2 4)')
ap.add_argument('--hilos', type=int, default=None, help='numThreads de openEMS')
ap.add_argument('--celdas-z', type=int, default=3, help='celdas en el sustrato')
ap.add_argument('--end', type=float, default=1e-4, help='EndCriteria')
ap.add_argument('--completo', action='store_true', help='simular los 4 puertos')
ap.add_argument('--conservar', action='store_true', help='no borrar carpetas tmp')
args = ap.parse_args()

# ---------------- Parámetros físicos ----------------
eps_r = 3.66
W = 40.0             # ancho de pista [mm]
L = 60.0             # largo de pista [mm]
h = 0.508            # espesor del sustrato [mm]
via_r = 0.3          # radio de vías [mm]
via_pitch = 5.0      # paso de vías en Y [mm]
margin = 15.0        # aire alrededor [mm]
z_top = 12.0         # altura sobre el sustrato [mm]
res_xy = 2.0         # resolución gruesa fuera del gap [mm]
Z0 = 50.0

freq = np.linspace(1e6, 1e9, 400)
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)


def seg(a, b, n):
    """n celdas uniformes entre a y b (devuelve n+1 líneas)."""
    return np.linspace(a, b, int(n) + 1)


def correr(gap):
    gap_str = f"{int(gap)}" if float(gap).is_integer() else f"{gap}"
    use_guard = MODO in ('guarda', 'ambos')   # pista de guarda superior
    use_vias = MODO in ('vias', 'ambos')      # hilera de vías a masa

    # Guarda: 2 mm como en el diseño original, pero nunca más de gap/2
    guard_w = min(2.0, gap / 2.0)
    side = (gap - guard_w) / 2.0 if use_guard else gap
    res_gap = min(0.5, side / 2.0)          # >= 2 celdas por tramo libre

    x1, x2 = -(W + gap) / 2.0, (W + gap) / 2.0
    xo = gap / 2.0 + W                      # borde exterior de las pistas
    xd = xo + margin                        # borde del dominio
    y_vias = np.arange(0.0, L + 1e-6, via_pitch)

    def correr_puerto(k):
        FDTD = openEMS(EndCriteria=args.end)
        CSX = ContinuousStructure()
        FDTD.SetCSX(CSX)

        # ---- Malla ----
        mesh = CSX.GetGrid()
        mesh.SetDeltaUnit(1e-3)
        if use_guard:
            xg = np.concatenate([
                seg(-gap/2, -guard_w/2, np.ceil(side / res_gap)),
                seg(-guard_w/2, guard_w/2, 2),
                seg(guard_w/2, gap/2, np.ceil(side / res_gap)),
            ])
        else:
            xg = seg(-gap/2, gap/2, np.ceil(gap / res_gap))
        mesh.AddLine('x', list(xg) + [0.0, -xd, -xo, xo, xd])
        ys = [-margin, 0.0, L, L + margin] + (list(y_vias) if use_vias else [])
        mesh.AddLine('y', ys)
        mesh.AddLine('z', list(seg(-h, 0.0, args.celdas_z)) + [z_top])
        for ax in ('x', 'y', 'z'):
            mesh.SmoothMeshLines(ax, res_xy, 1.4)

        # ---- Geometría ----
        sub = CSX.AddMaterial('Substrate', epsilon=eps_r)
        sub.AddBox(priority=10, start=[-xd, -margin, -h], stop=[xd, L + margin, 0.0])

        cu = CSX.AddMetal('Copper')          # láminas de espesor cero en z=0
        for xc in (x1, x2):
            cu.AddBox(priority=30, start=[xc - W/2, 0.0, 0.0], stop=[xc + W/2, L, 0.0])
        if use_guard:
            cu.AddBox(priority=30, start=[-guard_w/2, 0.0, 0.0], stop=[guard_w/2, L, 0.0])
        if use_vias:
            for yv in y_vias:
                cu.AddCylinder(priority=40, start=[0.0, yv, -h], stop=[0.0, yv, 0.0],
                               radius=via_r)

        # ---- Puertos: P1 (x1,y=0) P2 (x1,y=L) P3 (x2,y=0) P4 (x2,y=L) ----
        coords = [(x1, 0.0), (x1, L), (x2, 0.0), (x2, L)]
        ports = [FDTD.AddLumpedPort(i + 1, Z0,
                                    start=[px - W/2, py, -h], stop=[px + W/2, py, 0.0],
                                    p_dir='z', excite=1 if i == k else 0, priority=100)
                 for i, (px, py) in enumerate(coords)]

        FDTD.SetGaussExcite(500e6, 500e6)
        # [xmin, xmax, ymin, ymax, zmin, zmax]; zmin = plano de masa (PEC)
        FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PEC', 'PML_8'])

        run_dir = os.path.join(base_dir, f"tmp_{PREFIJO}_sep_{gap_str}mm_p{k+1}")
        os.makedirs(run_dir, exist_ok=True)
        run_kw = {'cleanup': True}
        if args.hilos is not None:          # no pasar None: openEMS lo rechaza
            run_kw['numThreads'] = args.hilos
        FDTD.Run(run_dir, **run_kw)

        for p in ports:
            p.CalcPort(run_dir, freq)
        inc = ports[k].uf_inc
        col = np.array([(p.uf_ref if i == k else p.uf_tot) / (inc + 1e-15)
                        for i, p in enumerate(ports)])
        if not args.conservar:
            shutil.rmtree(run_dir, ignore_errors=True)
        return col

    t0 = time.perf_counter()
    S = np.zeros((4, 4, len(freq)), dtype=complex)
    if args.completo:
        for k in range(4):
            print(f"\n--- [{MODO}] gap {gap_str} mm: puerto {k+1}/4 ---")
            S[:, k, :] = correr_puerto(k)
    else:
        print(f"\n--- [{MODO}] gap {gap_str} mm: puerto 1 (resto por simetría) ---")
        a, b, c, d = correr_puerto(0)        # S11, S21, S31, S41
        S[0] = [a, b, c, d]
        S[1] = [b, a, d, c]
        S[2] = [c, d, a, b]
        S[3] = [d, c, b, a]

    out = os.path.join(data_dir, f"{PREFIJO}_sep_{gap_str}mm.s4p")
    with open(out, 'w') as f:
        f.write("# GHz S RI R 50\n")
        for i, fv in enumerate(freq):
            line = f"{fv/1e9:.6f} "
            for r in range(4):
                for c_ in range(4):
                    v = S[r, c_, i]
                    line += f"{v.real:.6f} {v.imag:.6f} "
            f.write(line.strip() + "\n")
    print(f"[OK] {out}  ({time.perf_counter() - t0:.1f} s)")

    print(f"\n--- RESUMEN [{MODO}] gap = {gap_str} mm ---")
    print(f"{'Frecuencia':<12} | {'S11 (dB)':<10} | {'S21 (dB)':<10} | {'S31 (dB)':<10} | {'S41 (dB)':<10}")
    print("-" * 62)
    for ft in (100e6, 500e6, 1e9):
        i = np.argmin(np.abs(freq - ft))
        db = lambda m, n: 20 * np.log10(np.abs(S[m, n, i]) + 1e-12)
        print(f"{freq[i]/1e6:6.1f} MHz   | {db(0,0):8.2f} | {db(1,0):8.2f} | {db(2,0):8.2f} | {db(3,0):8.2f}")


for g in args.gaps:
    correr(g)