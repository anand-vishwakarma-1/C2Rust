# from dotenv import load_dotenv
from openai import OpenAI
import os, json, re
from pathlib import Path

# Load environment variables and initialize client
# load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_c_code(prompt: str) -> str:
    # Pull out the C snippet between ```c and ```
    m = re.search(r"```c(.*?)```", prompt, re.DOTALL)
    return m.group(1) if m else prompt


def transpile(ctext: str) -> str:
    messages = [
        {"role": "system", "content": "You are a Rust expert."},
        {"role": "user",   "content": (
            f"Translate the following C code into fully implemented, idiomatic, and compilable Rust\n```c{ctext}```"
        )}
    ]
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2048,
        temperature=0
    )
    return resp.choices[0].message.content


def main():
    input_path  = Path("train_stage1.jsonl")
    output_path = Path("full_transpile.jsonl")
    examples = []

    for line in input_path.read_text().splitlines():
        ex = json.loads(line)
        c_chunk = extract_c_code(ex["prompt"])
        r_full  = transpile(c_chunk)
        # Update instruction to reflect full transpilation
        prompt = ex["prompt"].replace(
            "Translate this C code into compiles-ready Rust, filling out `unimplemented!()`.",
            "Translate the following C code into fully implemented, idiomatic, and compilable Rust."
        )
        completion = f"```rust{r_full}```<|endoftext|>"
        examples.append({"prompt": prompt, "completion": completion})

    with output_path.open("w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "")

    print(f"Wrote {len(examples)} examples to {output_path}")

if __name__ == "__main__":
    main()