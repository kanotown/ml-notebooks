"""Sync published code and exercises from ml-web without reading TeX.

Run: python scripts/sync_from_web.py [chapter ...] [--check]
The default is chapters 1-14. The manually maintained appendix is excluded.
Existing notebook headings, cell IDs, metadata and exercise setup are retained.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import textwrap
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEB = ROOT.parent / "ml-web"

# Colab で上から実行できるよう、タイトルの直後に置く準備セル（章ごと）。
# 第3章は本文の入力3.2で、第12章は本文で MeCab をインストールするので不要。
SETUP_HEADING = "## 準備"
FONTJA = (
    "# グラフの日本語を表示するためのフォント\n"
    "!pip install -q matplotlib-fontja\n"
    "import matplotlib_fontja"
)
SETUP = {n: FONTJA for n in (4, 5, 6, 7, 8, 9, 10, 11)}
SETUP[13] = (
    "# MeCab（形態素解析）と辞書のインストール\n"
    "!pip install -q mecab-python3 unidic-lite"
)
SETUP[14] = FONTJA + "\n\n# OpenAI API のライブラリ（14.5節で使用）\n!pip install -q openai"

# 演習のテンプレートが読み込むデータ（本文のコードではダウンロードしないもの）。
# 「## 演習問題」の直後にダウンロードのセルを置く。
EXERCISE_DATA = {
    11: ["cifar_1000_color.npz"],
    13: ["emails.csv"],
}
EXERCISE_INTRO = "まず、演習で使うデータを準備します。"
DATA_MARKER = "# 演習で使うデータのダウンロード"


def source(cell):
    value = cell["source"]
    return value if isinstance(value, str) else "".join(value)


def set_source(cell, text):
    if source(cell) != text:
        cell["source"] = text.splitlines(keepends=True)
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []


def listings(markdown):
    pattern = re.compile(
        r"^## 入力 (\d+\.\d+): (.*?) \{#list-[^}]+\}\n"
        r"\s*```python\n(.*?)^```", re.M | re.S
    )
    result = {}
    for number, caption, code in pattern.findall(markdown):
        if number in result:
            raise ValueError(f"Duplicate listing: {number}")
        code = code.rstrip()
        # Input 4.5 is a schematic API example, not an executable model.
        if "from sklearn.モジュール名 import モデル名" in code:
            code = "\n".join("# " + line if line else "#" for line in code.splitlines())
        result[number] = (caption, code)
    if not result:
        raise ValueError("No numbered code listings found")
    return result


def exercises(markdown):
    """Extract exercise prose and Python templates; omit answer includes."""
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        match = re.match(
            r"^###\s+(演習\s+\d+-\d+[:：].+?|発展課題[:：]?.*?)\s*"
            r"(?:\{#(exercise-[\w-]+)\})?\s*$", lines[i]
        )
        if not match:
            i += 1
            continue
        title, anchor = match.groups()
        blocks, prose = [], []

        def flush():
            content = "\n".join(prose).strip()
            if content:
                blocks.append(("markdown", content))
            prose.clear()

        i += 1
        while i < len(lines) and not re.match(r"^#{2,3} ", lines[i]):
            line = lines[i]
            if line.startswith("??? "):
                i += 1
                while i < len(lines) and (lines[i].startswith("    ") or not lines[i].strip()):
                    i += 1
                continue
            if line.startswith("!!! "):
                i += 1
                continue
            content = line[4:] if line.startswith("    ") else line
            if re.match(r"^\s*```python", content):
                flush()
                i += 1
                code_lines = []
                while i < len(lines) and not re.match(r"^\s*```\s*$", lines[i]):
                    code_lines.append(lines[i][4:] if lines[i].startswith("    ") else lines[i])
                    i += 1
                if i == len(lines):
                    raise ValueError(f"Unclosed code fence: {title}")
                code = textwrap.dedent("\n".join(code_lines)).rstrip()
                if "___" in code:
                    code = "\n".join("# " + row if row else "#" for row in code.splitlines())
                blocks.append(("code", code))
            else:
                prose.append(content)
            i += 1
        flush()
        yield title.strip(), anchor, blocks


def apply_setup(cells, chapter):
    """Keep exactly one setup section right after the title cell."""
    while len(cells) > 1 and source(cells[1]).strip() == SETUP_HEADING:
        end = 3 if len(cells) > 2 and cells[2]["cell_type"] == "code" else 2
        del cells[1:end]
    code = SETUP.get(chapter)
    if code is None:
        return
    def new(kind, text):
        cell_id = hashlib.sha256(f"setup:{chapter}:{kind}".encode()).hexdigest()[:12]
        cell = {"cell_type": kind, "id": cell_id, "metadata": {}, "source": text.splitlines(keepends=True)}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        return cell
    cells[1:1] = [new("markdown", SETUP_HEADING), new("code", code)]


def synchronize(original, web, chapter):
    nb = copy.deepcopy(original)
    cells = nb["cells"]
    apply_setup(cells, chapter)
    expected = listings((web / "docs" / "code" / f"{chapter}.md").read_text(encoding="utf-8"))
    seen = set()
    for index, cell in enumerate(cells):
        match = re.match(r"\*\*入力 (\d+\.\d+)\*\*", source(cell))
        if not match:
            continue
        number = match[1]
        if number in seen or number not in expected:
            raise ValueError(f"Unexpected/duplicate notebook listing: {number}")
        if index + 1 == len(cells) or cells[index + 1]["cell_type"] != "code":
            raise ValueError(f"No code cell after input {number}")
        caption, code = expected[number]
        set_source(cell, f"**入力 {number}**　{caption}")
        set_source(cells[index + 1], code)
        seen.add(number)
    if seen != expected.keys():
        raise ValueError(f"Notebook missing inputs: {sorted(expected.keys() - seen)}")

    markdown = (web / "docs" / "chapters" / f"{chapter}.md").read_text(encoding="utf-8")
    parsed = list(exercises(markdown))
    if not parsed:
        return nb
    start = next((i for i, c in enumerate(cells) if source(c).strip() == "## 演習問題"), None)
    if start is None:
        raise ValueError(f"Chapter {chapter}: exercise section missing")
    first_ex = next((i for i in range(start + 1, len(cells)) if source(cells[i]).startswith("### ")), None)
    if first_ex is None:
        raise ValueError(f"Chapter {chapter}: no existing exercises")
    # Retain setup cells such as downloads before the first exercise.
    result = cells[:first_ex]
    if chapter in EXERCISE_DATA:
        code = DATA_MARKER + "\nfrom urllib.request import urlretrieve\n\n" + "\n".join(
            f'urlretrieve("https://ml.kano.ac/chapters/data/{f}", "{f}")' for f in EXERCISE_DATA[chapter]
        )
        tail = result[start + 1:]
        if not (len(tail) >= 2 and source(tail[0]).strip() == EXERCISE_INTRO
                and source(tail[1]).startswith(DATA_MARKER)):
            ids = [hashlib.sha256(f"exdata:{chapter}:{k}".encode()).hexdigest()[:12] for k in ("md", "code")]
            result[start + 1:start + 1] = [
                {"cell_type": "markdown", "id": ids[0], "metadata": {}, "source": []},
                {"cell_type": "code", "id": ids[1], "metadata": {}, "source": [],
                 "execution_count": None, "outputs": []},
            ]
        set_source(result[start + 1], EXERCISE_INTRO)
        set_source(result[start + 2], code)
    pool = defaultdict(deque)
    for cell in cells[first_ex:]:
        pool[(cell["cell_type"], source(cell))].append(cell)
    used_ids = {c.get("id") for c in result}

    def append(kind, content):
        available = pool[(kind, content)]
        if available:
            cell = available.popleft()
        else:
            cell_id = hashlib.sha256(f"{chapter}:{len(result)}:{kind}:{content}".encode()).hexdigest()[:12]
            cell = {"cell_type": kind, "id": cell_id, "metadata": {}, "source": content.splitlines(keepends=True)}
            if kind == "code":
                cell.update(execution_count=None, outputs=[])
        if cell["id"] in used_ids:
            raise ValueError("Duplicate cell ID")
        used_ids.add(cell["id"])
        result.append(cell)

    for title, anchor, blocks in parsed:
        append("markdown", f"### {title}")
        for kind, content in blocks:
            append(kind, content)
        link = f"https://ml.kano.ac/solutions/{chapter}/"
        if anchor:
            link += "#" + anchor.replace("exercise", "solution", 1)
        append("markdown", f"[解答例を見る]({link})")
    nb["cells"] = result
    return nb


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chapters", nargs="*", type=int)
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    parser.add_argument("--web", type=Path, default=DEFAULT_WEB)
    args = parser.parse_args()
    chapters = args.chapters or list(range(1, 15))
    if any(n < 1 or n > 14 for n in chapters):
        parser.error("Only chapters 1-14 are supported; appendix 15 is maintained separately")
    pending = []
    # Validate all requested chapters before writing any notebook.
    for chapter in chapters:
        path = ROOT / f"chapter{chapter:02d}.ipynb"
        original = json.loads(path.read_text(encoding="utf-8"))
        updated = synchronize(original, args.web, chapter)
        if original != updated:
            pending.append((path, updated))
    for path, updated in pending:
        print(("OUT OF SYNC " if args.check else "UPDATED ") + path.name)
        if not args.check:
            path.write_text(json.dumps(updated, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    if not pending:
        print(f"All {len(chapters)} notebooks match the Web code and exercises.")
    return int(args.check and bool(pending))


if __name__ == "__main__":
    raise SystemExit(main())
