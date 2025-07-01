import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

class CRUSTLoader:
    def __init__(self, cbench_dir: str, rbench_dir: str):
        self.cbench = Path(cbench_dir)
        self.rbench = Path(rbench_dir)
        # only directories under CBench are projects
        self.projects = [p.name for p in self.cbench.iterdir() if p.is_dir()]

    @staticmethod
    def remove_comments(code: str) -> str:
        # strip single-line comments
        code = re.sub(r"//.*?\n", "\n", code)
        # strip block comments
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        # collapse multiple blank lines
        return re.sub(r"\n+", "\n", code)

    def get_c_files(self, project: str) -> List[Dict]:
        """
        Load all .c and .h files (excluding tests/examples/bin) for one project,
        return list of {'file_name': ..., 'content': ...}
        """
        records = []
        base = self.cbench / project
        for f in base.rglob("*"):
            if not f.is_file(): 
                continue
            if f.suffix not in {".c", ".h"}:
                continue
            if any(x in f.parts for x in ("test", "tests", "example", "examples", "bin", "unity")):
                continue
            raw = f.read_text(errors="ignore")
            txt = self.remove_comments(raw)
            records.append({"file_name": f.name, "content": txt})
        # sort for deterministic output
        return sorted(records, key=lambda d: d["file_name"])

    def process_c_and_h(self, c_records: List[Dict]) -> List[Dict]:
        """
        Merge headers into their corresponding .c where both exist.
        Returns a new list of records, with .h merged and renamed to .c.
        """
        c_map = {r["file_name"]: r["content"] for r in c_records}
        out = []
        visited = set()

        # iterate headers first, attach to .c
        for rec in sorted(c_records, key=lambda d: d["file_name"], reverse=True):
            name = rec["file_name"]
            if name.endswith(".h"):
                base = name[:-2] + ".c"
                if base in c_map:
                    # merge header+source
                    merged = (
                        "// from header\n/*\n"
                        + rec["content"]
                        + "\n*/\n"
                        + c_map[base]
                    )
                    out.append({"file_name": base, "content": merged})
                    visited.add(base)
                else:
                    out.append(rec)
            else:
                if name not in visited:
                    out.append(rec)

        # ensure sorted
        return sorted(out, key=lambda d: d["file_name"])

    def load_rust_interfaces(self, project: str) -> List[Dict]:
        """
        Load all stub interfaces (*.rs in src/interfaces) with their raw content.
        """
        recs = []
        intf_dir = self.rbench / project / "src" / "interfaces"
        if intf_dir.exists():
            for f in intf_dir.glob("*.rs"):
                recs.append({"file_name": f.name, "content": f.read_text()})
        return sorted(recs, key=lambda d: d["file_name"])

    def load_rust_bins(self, project: str) -> List[Dict]:
        """
        Load all test drivers (*.rs in src/bin) if you need them later.
        """
        recs = []
        bin_dir = self.rbench / project / "src" / "bin"
        if bin_dir.exists():
            for f in bin_dir.glob("*.rs"):
                recs.append({"file_name": f.name, "content": f.read_text()})
        return sorted(recs, key=lambda d: d["file_name"])

    def get_interface_pairs(self) -> List[Tuple[Path, Path]]:
        """
        For each project, returns list of (c_path, rust_interface_path)
        by matching stems.
        """
        pairs = []
        for proj in self.projects:
            c_recs = self.get_c_files(proj)
            c_recs = self.process_c_and_h(c_recs)
            rust_intfs = self.load_rust_interfaces(proj)

            # build a map from stem to C record
            cmap = {Path(r["file_name"]).stem: r for r in c_recs}
            for ri in rust_intfs:
                stem = Path(ri["file_name"]).stem
                if stem in cmap:
                    c_file = cmap[stem]["content"]
                    r_file = ri["content"]
                    pairs.append((c_file, r_file))
        return pairs

    def export_jsonl(self, out_train: str, out_valid: str, split: float = 0.9):
        """
        Write train/valid JSONL with instruction-style prompts & completions.
        """
        exs = []
        for ctext, rtext in self.get_interface_pairs():
            exs.append({"ctext": ctext, "rtext": rtext})

        cut = int(len(exs) * split)
        for path, batch in [(out_train, exs[:cut]), (out_valid, exs[cut:])]:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w") as f:
                for e in batch:
                    f.write(json.dumps(e) + "\n")


if __name__ == "__main__":
    loader = CRUSTLoader("datasets/CBench", "datasets/RBench")
    loader.export_jsonl("train.jsonl", "valid.jsonl")