

# Diseño de PCB en KiCad — Técnicas de aislamiento electromagnético

## Descripción

Este repositorio contiene el diseño de cuatro placas de circuito impreso (PCB) desarrolladas en **KiCad 9** para estudiar diferentes técnicas pasivas de reducción del acoplamiento electromagnético (*crosstalk*) entre líneas de transmisión y recepción (TX/RX).

Se diseñaron cuatro configuraciones utilizando la misma geometría base, conectores SMA y sustrato dieléctrico, con el propósito de comparar las técnicas de aislamiento.

## Diseños de PCB

| PCB | Nombre | Descripción |
|---|---|---|
| 01 | PCB_01_Base | Dos pistas paralelas sin aislamiento adicional |
| 02 | PCB_02_ViaFencing | Pistas con barreras de vías conectadas a GND |
| 03 | PCB_03_Apantallamiento | Pistas con conexiones para una pantalla metálica |
| 04 | PCB_04_ViaFencing_Apantallamiento | Combinación de ambas técnicas |

### PCB 01 — Diseño base

- Dos líneas de transmisión: TX y RX.
- Cuatro conectores SMA de montaje en borde.
- Plano de tierra en B.Cu.
- Dos pistas con transiciones diagonales de 45°.
- Separación de 2 mm entre bordes en el tramo central.

### PCB 02 — Via Fencing

Se incorporaron barreras de vías conectadas a GND alrededor de las pistas.

- Tres filas longitudinales de vías.
- Nueve vías adicionales.
- Separación longitudinal de 7.84 mm entre centros.
- Diámetro de vía: 0.80 mm.
- Perforación: 0.40 mm.
- Franjas de conexión GND en F.Cu.

### PCB 03 — Apantallamiento

Se preparó una estructura para incorporar una pantalla metálica sobre la línea TX.

- Seis vías GND adicionales.
- Dos franjas de conexión GND.
- Contorno mecánico de referencia en User.Drawings.
- Longitud propuesta de pantalla: 23 mm.
- Ancho propuesto: 2.5 mm.
- Altura propuesta: 2 mm sobre F.Cu.

**Nota:** la cubierta metálica elevada todavía no está incorporada físicamente al diseño. El contorno de User.Drawings representa únicamente su ubicación propuesta.

### PCB 04 — Técnicas combinadas

Se integraron las conexiones del apantallamiento y las barreras de vías.

- Tres filas de vías GND.
- Separación longitudinal de 7.84 mm.
- Franjas de conexión en F.Cu.
- Contorno de referencia para la pantalla metálica.
- Plano de tierra común en B.Cu.

## Especificaciones de diseño

| Parámetro | Valor |
|---|---|
| Software | KiCad 9 |
| Dimensiones de PCB | 40 × 50 mm |
| Capas de cobre | 2 |
| Material del sustrato | Rogers RO4350B |
| Espesor del dieléctrico | 0.508 mm |
| Permitividad relativa | 3.66 |
| Espesor de cobre | 0.035 mm por capa |
| Ancho de pistas | 0.508 mm |
| Longitud objetivo de pistas | 40 mm |
| Separación central entre pistas | 2 mm entre bordes |
| Conectores | 4 SMA Edge Mount |
| Diámetro de vías | 0.80 mm |
| Perforación de vías | 0.40 mm |
| Separación longitudinal de vías | 7.84 mm |

## Organización de archivos

```text
KiCad_PCB/
├── README.md
├── PCB_01_Base/
│   ├── PCB_01_Base.kicad_pro
│   ├── PCB_01_Base.kicad_sch
│   └── PCB_01_Base.kicad_pcb
│
├── PCB_02_ViaFencing/
│   ├── PCB_02_ViaFencing.kicad_pro
│   ├── PCB_02_ViaFencing.kicad_sch
│   └── PCB_02_ViaFencing.kicad_pcb
│
├── PCB_03_Apantallamiento/
│   ├── PCB_03_Apantallamiento.kicad_pro
│   ├── PCB_03_Apantallamiento.kicad_sch
│   └── PCB_03_Apantallamiento.kicad_pcb
│
└── PCB_04_ViaFencing_Apantallamiento/
    ├── PCB_04_ViaFencing_Apantallamiento.kicad_pro
    ├── PCB_04_ViaFencing_Apantallamiento.kicad_sch
    └── PCB_04_ViaFencing_Apantallamiento.kicad_pcb
```

## Cómo abrir los diseños

1. Instalar KiCad 9.
2. Descargar o clonar este repositorio.
3. Abrir KiCad.
4. Seleccionar el archivo `.kicad_pro` de la PCB deseada.
5. Abrir el editor PCB para visualizar las pistas, los conectores y las estructuras de aislamiento.

Los diseños utilizan una biblioteca personalizada de huellas SMA denominada `RF_SubGHz`. Esta biblioteca debe estar disponible y correctamente vinculada al proyecto para editar o actualizar las huellas.

## Verificación de diseño

Los diseños fueron revisados mediante el comprobador de reglas de diseño (DRC) de KiCad.

Se verificaron las conexiones TX, RX y GND, así como la separación entre conductores.

Las violaciones asociadas al montaje en borde de los conectores SMA se trataron como exclusiones específicas. Su compatibilidad con los requisitos de fabricación debe confirmarse antes de producir las placas.

