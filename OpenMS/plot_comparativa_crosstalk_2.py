import os
import numpy as np
import matplotlib.pyplot as plt

def leer_s4p(filepath):
    freq = []
    s_data = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('!') or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 33:
                continue
            freq.append(float(parts[0]))
            vals = [float(x) for x in parts[1:33]]
            s_matrix = np.zeros((4, 4), dtype=complex)
            idx = 0
            for r in range(4):
                for c in range(4):
                    s_matrix[r, c] = complex(vals[idx], vals[idx + 1])
                    idx += 2
            s_data.append(s_matrix)
    return np.array(freq), np.array(s_data)

def to_db(s_complex):
    return 20 * np.log10(np.abs(s_complex) + 1e-12)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, 'data')

# Ajusta los prefijos si tus archivos en data/ tienen otro nombre exacto
casos = [
    ("2 mm - Guarda", "crosstalk_guard_sep_2mm.s4p", "tab:blue", "-"),
    ("2 mm - Vías",   "crosstalk_fencing_sep_2mm.s4p", "tab:blue", "--"),
    ("2 mm - Ambos",  "crosstalk_shielded_sep_2mm.s4p", "tab:blue", "-."),
    ("4 mm - Guarda", "crosstalk_guard_sep_4mm.s4p", "tab:orange", "-"),
    ("4 mm - Vías",   "crosstalk_fencing_sep_4mm.s4p", "tab:orange", "--"),
    ("4 mm - Ambos",  "crosstalk_shielded_sep_4mm.s4p", "tab:orange", "-."),
]

datos_cargados = []
for etiqueta, filename, color, estilo in casos:
    ruta = os.path.join(data_dir, filename)
    if os.path.exists(ruta):
        f, s = leer_s4p(ruta)
        datos_cargados.append((etiqueta, f, s, color, estilo))
        print(f"[OK] Cargado: {etiqueta} -> {ruta}")
    else:
        print(f"[Aviso] Falta el archivo: {ruta}")

if not datos_cargados:
    raise FileNotFoundError("No se encontraron archivos .s4p de mitigación en 'data/'. Revisa los nombres con: ls data/")

fig, axs = plt.subplots(2, 2, figsize=(13, 9), sharex=True)

for etiqueta, f, s, color, estilo in datos_cargados:
    axs[0, 0].plot(f, to_db(s[:, 2, 0]), label=etiqueta, color=color, linestyle=estilo, linewidth=2)  # S31 (NEXT)
    axs[0, 1].plot(f, to_db(s[:, 3, 0]), label=etiqueta, color=color, linestyle=estilo, linewidth=2)  # S41 (FEXT)
    axs[1, 0].plot(f, to_db(s[:, 0, 0]), label=etiqueta, color=color, linestyle=estilo, linewidth=2)  # S11 (Reflexión)
    axs[1, 1].plot(f, to_db(s[:, 1, 0]), label=etiqueta, color=color, linestyle=estilo, linewidth=2)  # S21 (Transmisión)

titulos = [
    ('Crosstalk Extremo Cercano - NEXT ($S_{31}$)', 'Magnitud $S_{31}$ [dB]'),
    ('Crosstalk Extremo Lejano - FEXT ($S_{41}$)', 'Magnitud $S_{41}$ [dB]'),
    ('Pérdida de Retorno - Reflexión ($S_{11}$)', 'Magnitud $S_{11}$ [dB]'),
    ('Pérdida de Inserción - Transmisión ($S_{21}$)', 'Magnitud $S_{21}$ [dB]'),
]

for ax, (titulo, ylabel) in zip(axs.flat, titulos):
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(fontsize=8.5, ncol=2)

axs[1, 0].set_xlabel('Frecuencia [GHz]', fontsize=10)
axs[1, 1].set_xlabel('Frecuencia [GHz]', fontsize=10)

plt.suptitle('Comparativa de Mitigación: Guarda, Via Fencing y Ambos (2 mm y 4 mm)', fontsize=14, fontweight='bold')
plt.tight_layout()

output_img = os.path.join(data_dir, 'comparativa_mitigacion_2mm_4mm.png')
plt.savefig(output_img, dpi=300)
print(f"\n[OK] Gráfica exportada en: {output_img}")
plt.show()
