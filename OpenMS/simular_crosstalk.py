import sys
import os
import numpy as np
from CSXCAD import ContinuousStructure
from openEMS import openEMS

# Validar argumento de entrada por terminal
if len(sys.argv) != 2:
    print("Uso: python3 simular_crosstalk.py <separacion_en_mm>")
    print("Ejemplo: python3 simular_crosstalk.py 6")
    sys.exit(1)

separation = float(sys.argv[1])
sep_str = f"{int(separation)}" if separation.is_integer() else f"{separation}"
output_filename = f"crosstalk_subghz_sep_{sep_str}mm.s4p"

# Parámetros físicos y geométricos
eps_r = 4.3
trace_width = 3.0    # mm (~50 ohms en FR4 de 1.6 mm)
trace_length = 50.0  # mm

p1_center = -separation / 2.0
p2_center = separation / 2.0

# Configuración de malla (cubriendo cómodamente desde 2 mm hasta 15 mm)
resolution_fine = 0.25   # mm (12 celdas a lo ancho de cada pista de 3 mm)
resolution_coarse = 2.0  # mm

mesh_x = np.concatenate([
    np.arange(-25.0, -11.0, resolution_coarse),
    np.arange(-11.0, 11.0 + resolution_fine, resolution_fine),
    np.arange(13.0, 25.0 + resolution_coarse, resolution_coarse)
])

mesh_y = np.concatenate([
    np.arange(-10.0, 0.0, resolution_coarse),
    np.linspace(0.0, trace_length, 51),
    np.arange(trace_length + resolution_coarse, trace_length + 10.0 + resolution_coarse, resolution_coarse)
])

mesh_z = np.concatenate([
    np.arange(-8.0, -1.6, resolution_coarse),
    np.linspace(-1.6, 0.0, 5),
    [0.035],
    np.arange(0.5, 10.0, resolution_coarse)
])

freq = np.linspace(0, 1e9, 401)
num_ports = 4
port_impedance = 50.0
S = np.zeros((num_ports, num_ports, len(freq)), dtype=complex)

# Puertos volumétricos dinámicos
port_coords = [
    ([p1_center - trace_width/2, 0.0, -1.6],          [p1_center + trace_width/2, 0.0, 0.0]),          # Puerto 1
    ([p1_center - trace_width/2, trace_length, -1.6], [p1_center + trace_width/2, trace_length, 0.0]), # Puerto 2
    ([p2_center - trace_width/2, 0.0, -1.6],          [p2_center + trace_width/2, 0.0, 0.0]),          # Puerto 3
    ([p2_center - trace_width/2, trace_length, -1.6], [p2_center + trace_width/2, trace_length, 0.0])  # Puerto 4
]

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

for k in range(num_ports):
    print(f"\n--- Ejecutando FDTD (Sep: {sep_str} mm): Excitando Puerto {k+1} ---")
    
    FDTD = openEMS(EndCriteria=1e-4)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)

    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)
    mesh.AddLine('x', mesh_x)
    mesh.AddLine('y', mesh_y)
    mesh.AddLine('z', mesh_z)
    mesh.SmoothMeshLines('x', 1.4)
    mesh.SmoothMeshLines('y', 1.4)
    mesh.SmoothMeshLines('z', 1.4)

    # Sustrato FR4
    material_fr4 = CSX.AddMaterial('FR4', epsilon=eps_r)
    material_fr4.AddBox(priority=10, start=[-18.0, -2.0, -1.6], stop=[18.0, trace_length + 2.0, 0.0])

    # Plano de masa inferior (PEC en Z = -1.6 mm)
    metal = CSX.AddMetal('PEC')
    metal.AddBox(priority=20, start=[-18.0, -2.0, -1.6], stop=[18.0, trace_length + 2.0, -1.6])

    # Pistas conductoras superiores
    copper = CSX.AddMetal('Copper')
    copper.AddBox(priority=30, start=[p1_center - trace_width/2, 0.0, 0.0], stop=[p1_center + trace_width/2, trace_length, 0.035])
    copper.AddBox(priority=30, start=[p2_center - trace_width/2, 0.0, 0.0], stop=[p2_center + trace_width/2, trace_length, 0.035])

    # Crear los 4 puertos lumped
    current_ports = []
    for p_idx, (p_start, p_stop) in enumerate(port_coords):
        is_excited = 1 if p_idx == k else 0
        cp = FDTD.AddLumpedPort(p_idx + 1, port_impedance, 
                               start=p_start, stop=p_stop, 
                               p_dir='z', excite=is_excited, priority=100)
        current_ports.append(cp)

    FDTD.SetGaussExcite(500e6, 500e6)
    FDTD.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])

    run_dir = os.path.join(base_dir, f"tmp_sep_{sep_str}mm_p{k+1}")
    os.makedirs(run_dir, exist_ok=True)
    FDTD.Run(run_dir)

    for cp in current_ports:
        cp.CalcPort(run_dir, freq)

    inc_k = current_ports[k].uf_inc
    for i in range(num_ports):
        if i == k:
            S[i, k, :] = current_ports[i].uf_ref / (inc_k + 1e-15)
        else:
            S[i, k, :] = current_ports[i].uf_tot / (inc_k + 1e-15)

# Guardar archivo Touchstone estandarizado
touchstone_path = os.path.join(data_dir, output_filename)
with open(touchstone_path, 'w') as f:
    f.write("# GHz S RI R 50\n")
    for idx, f_val in enumerate(freq):
        line = f"{f_val/1e9:.6f} "
        for row in range(num_ports):
            for col in range(num_ports):
                val = S[row, col, idx]
                line += f"{val.real:.6f} {val.imag:.6f} "
        f.write(line.strip() + "\n")

print(f"\n[OK] Matriz S4p exportada en: {touchstone_path}")

# Resumen estandarizado en terminal
freq_points = [100e6, 500e6, 1e9]
print(f"\n--- RESUMEN PARÁMETROS S (Sep = {sep_str} mm) ---")
print(f"{'Frecuencia':<12} | {'S11 (dB)':<12} | {'S21 (dB)':<12} | {'S31 (dB)':<12} | {'S41 (dB)':<12}")
print("-" * 68)

for f_target in freq_points:
    idx = np.argmin(np.abs(freq - f_target))
    f_actual = freq[idx]
    
    s11_db = 20 * np.log10(np.abs(S[0, 0, idx]) + 1e-12)
    s21_db = 20 * np.log10(np.abs(S[1, 0, idx]) + 1e-12)
    s31_db = 20 * np.log10(np.abs(S[2, 0, idx]) + 1e-12)
    s41_db = 20 * np.log10(np.abs(S[3, 0, idx]) + 1e-12)
    
    print(f"{f_actual/1e6:6.1f} MHz   | {s11_db:10.2f} | {s21_db:10.2f} | {s31_db:10.2f} | {s41_db:10.2f}")
print("-" * 68)
