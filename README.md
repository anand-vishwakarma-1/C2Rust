# 🚀 CRUST-bench Fine-Tuning Pipeline

This repository demonstrates a minimal end-to-end pipeline to fine-tune OpenAI’s `o3` language model for translating C code into memory-safe Rust code. It leverages the [CRUST-bench dataset](https://github.com/anirudhkhatry/CRUST-bench), a curated collection of parallel C and Rust source code samples.

The goal is to build an AI-assisted system capable of automating the migration of legacy C codebases to Rust—a memory-safe language—thus improving software safety and maintainability.

---

## 📚 Project Overview

Many critical systems worldwide run on legacy C code, which is vulnerable to memory safety issues like buffer overflows and dangling pointers. Rust offers a safer alternative with its strict ownership model and compile-time guarantees. However, translating large C codebases to Rust manually is labor-intensive and error-prone.

This project focuses on building a pipeline that:

✅ Loads and pairs C and Rust files from CRUST-bench  
✅ Formats training data for instruction-style fine-tuning  
✅ Uploads data and launches fine-tuning via OpenAI’s API  
✅ Tests the fine-tuned model for C→Rust translation

---

## 📂 Dataset: CRUST-bench

- **Source:** [CRUST-bench GitHub Repository](https://github.com/anirudhkhatry/CRUST-bench)
- **Content:** Parallel implementations of identical programs in C and Rust.
- **Folder Structure:**

  ```
  CBench/
    Project_1/
      file1.c
      file2.c
      ...
  RBench/
    Project_1/
      file1.rs
      file2.rs
      ...
  ```

Each C file in `CBench` has a matching Rust file in `RBench` under the same project folder. This dataset provides ideal supervised examples for training a translation model.

---

## ⚙️ Pipeline Overview

The Jupyter notebook implements the following pipeline stages:

### 1. Data Pairing

- Scans the CRUST-bench dataset folders to identify matching pairs of C and Rust files.
- Ensures only valid pairs are used by:
  - Excluding missing or empty files.
  - Matching files based on identical filenames and project directories.

### 2. Data Preparation

- For each C–Rust file pair, extracts:
  - Raw C source code.
  - Corresponding Rust translation.
- Formats each pair into a structured instruction-style dataset suitable for fine-tuning OpenAI’s conversational models.

Each training example is framed as a dialogue:

- **System message:** Provides context, instructing the model to translate C code into memory-safe Rust.
- **User message:** Contains the C code snippet.
- **Assistant message:** Contains the corresponding Rust translation.

This conversational format aligns with the design of modern LLMs and improves performance on task-specific instructions.

### 3. Dataset Serialization

- Compiles all translation pairs into a JSONL (JSON Lines) file:
  - Each line represents a separate training example.
  - Required format for OpenAI’s fine-tuning API.
- Cleans up excess whitespace and optionally filters out very short or excessively large examples to maintain data quality.

### 4. Fine-Tuning Preparation

- After preparing the dataset, the notebook provides the foundation for:
  - Uploading the JSONL file to OpenAI’s API.
  - Launching a fine-tuning job targeting the `o3` model.

While the notebook’s main focus is on data preparation, it includes the necessary steps to integrate with the fine-tuning pipeline.

### 5. Inference Workflow

- Once fine-tuning is complete, the notebook defines the workflow for:
  - Sending new C code snippets as user inputs.
  - Receiving translated Rust code as model responses.

This allows practical testing and validation of the fine-tuned model.

---

# 🛠️ Installation & Setup Instructions

Follow these steps to replicate the full pipeline:

### 1. Clone This Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Download CRUST-bench Dataset

Clone the CRUST-bench dataset separately:

```bash
git clone https://github.com/anirudhkhatry/CRUST-bench.git
```

This will create folders `CBench/` and `RBench/` used by the notebook.

### 3. Install Conda (if not already installed)

If you don’t have Conda or Miniconda installed, download it here:  
[Miniconda Download](https://docs.conda.io/en/latest/miniconda.html)

### 4. Set Up Conda Environment

Create and activate the Conda environment defined in the provided `environment.yml` file:

```bash
# Create the environment
conda env create -f environment.yml

# Activate the environment
conda activate crustbench
```

This environment includes all required Python libraries to run the notebook:

- jupyter
- openai
- tqdm
- matplotlib
- and any additional dependencies

### 5. Set Your OpenAI API Key

Before running the notebook, ensure your OpenAI API key is set as an environment variable.

On macOS/Linux:

```bash
export OPENAI_API_KEY="sk-xxxx..."
```

On Windows (PowerShell):

```powershell
$Env:OPENAI_API_KEY = "sk-xxxx..."
```

On Windows (Command Prompt):

```cmd
set OPENAI_API_KEY=sk-xxxx...
```

### 6. Launch Jupyter Notebook

Start Jupyter:

```bash
jupyter notebook
```

Then open:

```
crust_finetune_pipeline.ipynb
```

Follow the notebook cells step by step.

### 7. Running the Pipeline

Inside the notebook, you can:

- Load and pair files from the CRUST-bench dataset.
- Prepare and serialize the JSONL dataset for OpenAI fine-tuning.
- Upload your training data to OpenAI.
- Launch fine-tuning of the o3 model.
- Test inference by sending C code snippets and retrieving Rust translations.

### 8. Optional: Install Rust for Agentic AI Extensions

To extend the notebook with agentic AI capabilities (e.g. compiling generated Rust code), install the Rust toolchain.

On macOS/Linux:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

On Windows, download and install Rust from [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install).

---

## 🔮 Future Improvements

Potential enhancements for this project include:

- Chunking large C files into smaller translation units.
- Using AST-based transformations for more precise code migration.
- Automating compilation and testing of translated Rust code.
- Exploring reinforcement learning to reward successful compilations and runtime correctness.
- Integrating agentic AI approaches for multi-step translation, compiler error handling, and automated corrections to improve translation reliability and safety.

---

## License

This project is intended for educational and research purposes, respecting the license terms of the CRUST-bench dataset.

---

## Acknowledgements

- [CRUST-bench Dataset](https://github.com/anirudhkhatry/CRUST-bench)
- OpenAI API documentation
