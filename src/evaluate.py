# from dotenv import load_dotenv
from openai import OpenAI
import os, json, subprocess, tempfile
from nltk.translate.bleu_score import sentence_bleu

# # Load environment variables
# load_dotenv()

token = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=token)
FT_MODEL_STAGE2 = 'ft-o3-xxxxx'  # replace with your fine-tuned model ID

# Helper to check if Rust code compiles

def is_compilable(code: str) -> bool:
    with tempfile.NamedTemporaryFile(suffix='.rs', delete=False) as tmp:
        tmp.write(code.encode())
        tmp.flush()
        try:
            subprocess.run(
                ['rustc', '--emit=metadata', tmp.name],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False

# BLEU score for quality metric

def bleu(ref: str, pred: str) -> float:
    return sentence_bleu([ref.split()], pred.split(), weights=(0.25, 0.25, 0.25, 0.25))

if __name__ == '__main__':
    samples = [json.loads(l) for l in open('full_transpile.jsonl')]  # validation subset
    results = []
    for s in samples[:5]:
        # Generate with fine-tuned model
        resp = client.completions.create(
            model=FT_MODEL_STAGE2,
            prompt=s['prompt'],
            max_tokens=1024,
            temperature=0
        )
        gen = resp.choices[0].text.strip()
        results.append({
            'id': s['prompt'][:30],
            'compilable': is_compilable(gen),
            'bleu': bleu(s['completion'], gen)
        })
    print(json.dumps(results, indent=2))