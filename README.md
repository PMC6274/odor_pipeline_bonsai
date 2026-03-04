# odor_pipeline_bonsai

Bonsai workflows to run an **8-odor shuffled-block** odor delivery experiment using the **Harp Olfactometer**.

- Main repo: https://github.com/PMC6274/odor_pipeline_bonsai/tree/main  
- Harp Olfactometer docs: https://fchampalimaud.github.io/olfactometer-docs/docs/overview  

## Protocol

- **Odors per block:** 8 (IDs 1–8)  
- **Blocks:** 25  
- **Order within each block:** shuffled, no replacement  
- **Per-trial timing:**
  - Charge: 25 s  
  - Deliver: 4 s  
  - ISI / ITI: 25–45 s (uniform random)  
  - Total: ~50–70 s per trial  

Total: **200 trials** (8 odors × 25 blocks) with randomized odor order within each block.

## How to generate stim list

1. **Run the Python script to create the sequence**  
   From the repository root:

   ```bash
   cd generate_stim_list
   python gen_trials_d1.py
   ```

   This will create two files in `generate_stim_list/`:
   - `odor_sequence_numbers.csv`  
   - `odor_sequence_D1_format.txt`  

2. **Copy the D1-format sequence into the Bonsai main workflow**  
   - Open `generate_stim_list/odor_sequence_D1_format.txt` in a text editor.  
   - Select and copy all lines (from `it == 1  ? "D1:X" :` … to the final `"D1:0"`).  
   - In Bonsai, open the main workflow (e.g. `8random_25block_dev_endbutton_logging_nocsv_webhook.bonsai`).  
   - Find the expression/node where the trial counter (`it`) is mapped to `D1:<odor_id>`.  
   - Paste the copied lines there, replacing the existing `D1` mapping.

Whenever you want a new randomized odor order, rerun `python gen_trials_d1.py` and repeat step 2.
