# odor_pipeline_bonsai

Bonsai workflows to run an **8-odor shuffled-block** odor delivery experiment using the **Harp Olfactometer**.

- Main repo: https://github.com/PMC6274/odor_pipeline_bonsai/tree/main  
- Harp Olfactometer docs: https://fchampalimaud.github.io/olfactometer-docs/docs/overview  

## Protocol

- **Odors per block:** 6 (IDs 1–6)  
- **Blocks:** 64 
- **Order within each block:** shuffled, no replacement  
- **Per-trial timing:**
  - Charge: 25 s  
  - Deliver: 4 s  
  - ITI: 25 ~ 45 s (uniform random)  
  - Total: ~50 ~ 70 s per trial  

Total: **640 trials** (64 odors × 10 blocks) with randomized odor order within each block.

## How to generate stim list

1. **Run the Python script to generate the sequence**  
   From the repository root:

   ```bash
   cd generate_stim_list
   python make_mix_trials_correct_bits.py
   ```

   This will use current time as random seed to generate two files in `generate_stim_list/`:
   - `trial_table.csv`  
   - `bonsai_conditions_shuffled.txt`  

2. **Copy the D1-format sequence into the Bonsai main workflow**  
   - Open `bonsai_conditions_shuffled.txt` in a text editor.  
   - Select and copy all lines.  
   - In Bonsai, open the main workflow.  
   - Find the expression/node where the trial counter (`it`) is mapped to `:<odor_id>`.  
   - Paste the copied lines there, replacing the existing mapping.

Whenever you want a new randomized odor order, rerun `make_mix_trials_correct_bits.py` and repeat step 2.
