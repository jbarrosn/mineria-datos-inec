# Microdatos del INEC

Esta carpeta está vacía a propósito. Los archivos originales del INEC no se
distribuyen con el repositorio: pesan alrededor de 170 MB y su lugar es el
portal del INEC, no un repositorio de código.

## Qué descargar

De [ecuadorencifras.gob.ec](https://www.ecuadorencifras.gob.ec/):

| Archivo | Fuente | Uso |
|---|---|---|
| `BDDenemdu_personas_2025_anual.sav` | ENEMDU anual 2025 | bloques 3.1, 3.2 y 3.3 |
| `SINIESTROS_*_BDD.sav` (2018-2022) | Estadísticas de Transporte | bloque 3.4 |
| `2025_SINIESTROS_BDD_ITRIMESTRE_SPSS.zip` | Estadísticas de Transporte | control externo |

## Dónde ponerlos

En cualquier carpeta, con esta estructura:

```
DatosINEC/
├── 1_BDD_ENEMDU_2025_SPSS/
│   └── BDDenemdu_personas_2025_anual.sav
├── Diccionario_de_variables/
├── Sintaxis_anual_2025/
├── Transporte/
│   └── ESTRA_2018 … ESTRA_2022/
└── Siniestros_de_Transito/
    └── 2025_SINIESTROS_BDD_ITRIMESTRE_SPSS.zip
```

Y apuntar la variable de entorno:

```powershell
$env:INEC_DIR = "D:/DatosINEC"
```

## Nota sobre el zip de 2025

El archivo trae un nombre interno codificado en CP850 (`TRµNSITO`). `unzip()` de R
no puede decodificarlo; se extrae una vez con PowerShell:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$enc = [System.Text.Encoding]::GetEncoding(850)
[System.IO.Compression.ZipFile]::ExtractToDirectory(
  "DatosINEC/Siniestros_de_Transito/2025_SINIESTROS_BDD_ITRIMESTRE_SPSS.zip",
  "datos/_extraido", $enc)
```

El script `06_series.R` detecta si el `.sav` ya está extraído y sigue sin problema.
