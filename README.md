# odor_pipeline_bonsai

Bonsai workflows to run an **8-odor shuffled-block** odor delivery experiment using the **Harp Olfactometer**.

Repo: https://github.com/PMC6274/odor_pipeline_bonsai/tree/main :contentReference[oaicite:0]{index=0}  
Harp Olfactometer docs: https://fchampalimaud.github.io/olfactometer-docs/docs/overview :contentReference[oaicite:1]{index=1}

---

## Protocol implemented

- **Odors per block:** 8 (IDs 1–8)
- **Blocks:** 25
- **Within each block:** shuffle order (no replacement)
- **Timing per trial:**
  - **Charge:** 25 s
  - **Deliver:** 4 s
  - **ISI / ITI:** random uniform **25–45 s**
  - Total trial period ≈ **50–70 s** (charge + ITI)

These timing constants appear directly in the main workflow (e.g., `PT25S`, `PT4S`, and `randITI 25 45`). :contentReference[oaicite:2]{index=2}
