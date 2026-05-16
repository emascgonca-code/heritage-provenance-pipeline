# Heritage Provenance & Integrity Pipeline
### Blender Addon — Version 0.1

**Author:** Ema Gonçalves  
**Date:** May 2026  
**Blender Compatibility:** 4.0+  
**Language:** Python 3.x  
**Licence:** MIT  

---

## Overview

The Heritage Provenance & Integrity Pipeline is a Blender addon that computes SHA-256 cryptographic hashes of digital heritage files — including 3D models, archival drawings, and photogrammetric outputs — and generates structured provenance logs in JSON format.

The system is designed to address a methodological gap in digital heritage practice: the absence of formal mechanisms for verifying the integrity and authenticity of 3D reconstruction files over time. Any modification to a certified file — however minimal — produces a completely different hash, making alterations immediately and irrefutably detectable.

This addon is the first module of a broader research pipeline under development, focused on the computational formalisation of 2D-to-3D reconstruction in historical nautical heritage.

---

## Motivation

Digital models of historical vessels and maritime objects represent unique and irreproducible research data. Their integrity, availability, and protection against unauthorised modification are not abstract concerns — they are conditions for archaeological knowledge to survive in the long term.

Current practice in digital heritage reconstruction rarely includes formal integrity verification. Decisions made during 3D modelling are often undocumented, alternative hypotheses are not systematically recorded, and exported files are not cryptographically anchored at the time of creation. This addon proposes a lightweight, practical solution to this problem, implemented directly within the standard 3D modelling environment.

---

## Features — Version 0.1

- SHA-256 hash computation of any file type (`.obj`, `.fbx`, `.blend`, `.jpg`, `.png`, `.tiff`, etc.)
- Structured metadata entry: archive reference, institution, document title, date, source URL
- Manual geometric parameter logging with certainty levels (High / Medium / Low) and optional notes
- Timestamped JSON provenance log export
- Hash copy to clipboard
- Human validator field for documented review

---

## Installation

1. Download `heritage_provenance_addon.py`
2. Open Blender
3. Go to **Edit → Preferences → Add-ons → Install**
4. Select the `.py` file and click **Install Add-on**
5. Enable the addon by clicking the checkbox next to **Heritage Provenance & Integrity Pipeline**
6. Open the **3D Viewport**, press **N** to open the sidebar
7. Select the **Heritage Provenance** tab

---

## Usage

### Step 1 — Source Document
Fill in the metadata fields:
- **Source File** — path to the file to be certified (any format)
- **Archive Reference** — institutional call number or internal identifier
- **Institution** — originating institution or `Independent Research`
- **Document Title** — descriptive title of the document or model
- **Document Date** — year of creation or digitalisation
- **Source URL** — URL of the original source if available

### Step 2 — Compute Hash
Click **Compute Hash**. The system reads the file in binary chunks and computes the SHA-256 digest. The hash and file size in bytes are displayed in the panel.

### Step 3 — Geometric Parameters
Add parameters using the **Add** button. For each parameter, specify:
- **Name** — parameter identifier (e.g. `vertices`, `length_between_perpendiculars`)
- **Value** — measured or extracted value
- **Unit** — unit of measurement (e.g. `count`, `feet`, `metres`)
- **Certainty** — `High` (read directly), `Medium` (partially legible), `Low` (inferred)
- **Note** — optional observation

### Step 4 — Export
Set the **Output Directory**, confirm the **Validator** name, and click **Export Provenance Log**. A JSON file is generated with a timestamp in the filename.

---

## Output Format

```json
{
  "pipeline_name": "Heritage Provenance & Integrity Pipeline",
  "pipeline_version": "0.1",
  "timestamp_utc": "2026-05-16T16:30:11.092875+00:00",
  "source": {
    "filepath": "C:\\Users\\User\\Desktop\\projeto_hash\\original\\ancora_almirante.obj",
    "filename": "ancora_almirante.obj",
    "sha256": "0ddb2f191bf411a5050b39fbdbcc0f33075519695efe14ca81f3449e416589c8",
    "file_size_bytes": 49566783,
    "archive_reference": "ancora_almirante_v0.1",
    "institution": "Independent Research",
    "document_title": "3D Model — Stock Anchor",
    "document_date": "2026",
    "source_url": ""
  },
  "parameters_extracted": [
    {
      "name": "vertices",
      "value": "330691",
      "unit": "count",
      "certainty": "high"
    },
    {
      "name": "faces",
      "value": "330757",
      "unit": "count",
      "certainty": "high"
    }
  ],
  "human_validator": "Ema Gonçalves",
  "validation_date_utc": "2026-05-16",
  "notes": "All parameter values were reviewed and confirmed by the human validator. The SHA-256 hash anchors the integrity of the source document at the time of this record. Any subsequent modification to the source file will produce a different hash, making alterations detectable."
}
```

---

## Proof of Concept — Stock Anchor Test

Two versions of the same 3D model were certified to validate the pipeline:

| | Original | Modified |
|---|---|---|
| **File** | `ancora_almirante.obj` | `ancora_almirante_alterada.obj` |
| **SHA-256** | `0ddb2f19...` | `6029aeb4...` |
| **Size** | 49,566,783 bytes | 49,568,074 bytes |
| **Vertices** | 330,691 | 330,691 |
| **Faces** | 330,757 | 330,757 |
| **Modification** | None | Single vertex displaced 1mm |
| **Status** | ✓ Integrity confirmed | ⚠ Alteration detected |

The modification was geometrically minimal and visually indistinguishable. The SHA-256 hash changed completely, demonstrating that the system detects alterations automatically and irrefutably.

---

## Tested File Types

| Type | Format | Notes |
|---|---|---|
| 3D model | `.obj` | Primary test case |
| Archival image | `.jpg` | Lloyd's Register Foundation, 1869 |

---

## Limitations — Version 0.1

- Detects **whether** a file was altered, but not **where**, **when**, or **how**
- Does not read EXIF metadata from image files
- Does not compare two files directly within the interface
- Parameters are entered manually — no automated geometric extraction
- No report generation — output is JSON only

These limitations are addressed in the development roadmap for Version 0.2.

---

## Roadmap — Version 0.2

- HTML report generation from JSON log
- EXIF metadata extraction from image files (date, software, camera)
- Two-file comparison operator with difference detection
- Integration with the broader 2D-to-3D reconstruction pipeline

---

## Research Context

This addon is part of a doctoral research proposal titled *Submerged Memories: Computational Formalisation of 2D-to-3D Reconstruction in Historical Nordic Vessels*, which proposes a constraint-based parametric system for the reconstruction of historical clinker-built vessels from 2D geometric documentation.

The provenance and integrity module corresponds to the **Traceability Module** (Module 4) of the proposed four-module software architecture, which records the complete sequence of inferential steps, constraints applied, parameters selected, and reconstruction scenarios generated.

---

## Dependencies

No external libraries required. Uses Python standard library only:

- `hashlib` — SHA-256 computation
- `json` — log serialisation
- `os` — file path handling
- `datetime` — UTC timestamp generation

---

## Citation

If you use this addon in your research, please cite:

> Gonçalves, E. (2026). *Heritage Provenance & Integrity Pipeline* (Version 0.1) [Blender Addon]. Independent Research.

---

## Contact

Ema Gonçalves  
emascgonca@gmail.com  
[linkedin.com/in/ema-goncalves-/](https://linkedin.com/in/ema-goncalves-/)
