# CELLO (CIIRC's version of GELLO) — Bearing-Isolated, Passive-Braked GELLO Variant for the Franka Emika Panda

**CELLO** is low-cost GELLO leader variant for the **Franka Emika Panda**, that improves joint stability via **frictional joint regularization** and offloads structure-borne loads from motors.

---

## Why

Stock GELLO joints for the Panda rely on springs/rubber bands that degrade, and many links load the motor output directly. In practice this leads to joint sag, play, and fragile handling. **CELLO replaces spring regularizers with compact, adjustable friction brakes** and moves structure-borne loads onto a **concentric ball bearing**, improving stability and longevity while preserving encoder fidelity.

---

## What’s new

- **Passive brake (non-decoupling).** Thin **ring brake** mounted in parallel with the joint axis (not in the drive path).  
  Two printed rings + **TPU pads** (≈ Shore 95A) + symmetric **preload** (2× M3×25) → **adjustable drag** so links “stay put.” **Encoder sync preserved.**

- **Bearing-isolated base joint.** Concentric **ball bearing** carries radial/axial loads; the motor primarily transmits torque. (Inspired by [**FACTR**](https://github.com/JasonJZLiu/FACTR_Hardware))

- **Printable trigger torsion spring.** Spiral spring biases the trigger open; easy to reprint/replace.

- **Tightened tolerances & reinforced interfaces.** Modern printers → snug fits, reduced backlash.

- **Parametric, modular brakes.** Same core geometry for **axial** (solid hub) and **radial** (hollow-center) variants.

---

## Key features

- **Six brakes total:** 3 axial (L1–L2, L3–L4, L5–L6) + 3 radial (Base–L1, L2–L3, L4–L5).  
- **Materials:** PETG (structure/brake shells) and **TPU 95A** (pads).  
- **Serviceability:** replaceable pads; tool-adjustable preload.  
- **Encoder-safe:** friction regularization is parallel to the joint—no clutch in series.

---

## Build notes

- Use the supplied `.3mf` projects (orientations, copy counts, painted supports).  
- Print **pads** in TPU with the seam at the **outer edge** to avoid contact ridges.  
- Tune each brake by tightening both M3×25 preload screws **symmetrically** until the link **holds its own weight** with minimal drift while still driving smoothly.

---

## Full assembly instructions & bill of materials

Assembly guide (with photos) and BOM:  
<https://docs.google.com/document/d/1AONti0UWSNlmaY5SlAWqmKt7b-Y6IRfGCKrLpYsYRNI/edit?usp=sharing>

---

## Acknowledgments

Built on the ideas and ecosystem of [**GELLO**](https://github.com/wuphilipp/gello_mechanical) . Load-path choices were informed by [**FACTR**](https://github.com/JasonJZLiu/FACTR_Hardware). Contributions and adapters for other robots are welcome.
