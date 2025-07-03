# MoralAgents

This repository contains the code to replicate the paper, "Many LLMs are More Utilitarian than One".

## Repository Structure

```
├── data/                  # Raw data files (organized by dataset)
├── notebooks/             # analysis notebooks
│   ├── ManyLLMs_Analysis.Rmd
│   ├── ManyLLMs_Data Cleaning.Rmd
│   ├── ManyLLMs_ Analysis.pdf
│   └── ManyLLMs_ Data Cleaning.pdf
├── src/                   # Source code
│   ├── main.py
│   ├── prompts.py
│   ├── run.sh
│   ├── run.slurm
│   └── compile.ipynb
├── README.md              # Project overview and instructions
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Data Collection and Experimentation:
   ```bash
   cd src
   ./run.sh <model> <group_size> <dataset>
   ```
   - `<model>`: The LLM model to use (e.g., `qwen3:32b`, `llama3.3`)
   - `<group_size>`: The number of agents in the group (e.g., `1`, `2`, `3`)
   - `<dataset>`: The dataset to use (e.g., `greene`, `korner`, `keshmirian`, `cni`,  `oxford_utilitarianism_scale`)

   **Examples:**
   - Run Qwen3:32b on the Greene dataset with group size 3:
     ```bash
     bash run.sh qwen3:32b 3 greene
     ```
2. Compile Results:
   - Open and run `src/compile.ipynb` to aggregate and compile runs

3. Analysis:
   - Open and run the R Markdown files in the `notebooks/` directory

## How to Cite
If you use this code or data, please cite our paper:
```
@misc{keshmirian2025llmsutilitarian,
      title={Many LLMs Are More Utilitarian Than One}, 
      author={Anita Keshmirian and Razan Baltaji and Babak Hemmatian and Hadi Asghari and Lav R. Varshney},
      year={2025},
      eprint={2507.00814},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2507.00814}, 
}
```
