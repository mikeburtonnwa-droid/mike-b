"""Check local product-document links and basic installed-skill metadata (stdlib)."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.git', '.venv', 'node_modules', '__pycache__', 'development'}


def prose(text):
    output, fence = [], None
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(('~~~', chr(96) * 3)):
            mark = stripped[:3]
            if fence is None:
                fence = mark
            elif fence == mark:
                fence = None
            continue
        if fence is None:
            output.append(line)
    return '\n'.join(output)


def check():
    errors, links = [], 0
    documents = [p for p in ROOT.rglob('*.md')
                 if not EXCLUDED.intersection(p.relative_to(ROOT).parts)]
    for path in sorted(documents):
        text = prose(path.read_text(encoding='utf-8'))
        destinations = re.findall(r'\[[^\]]*\]\(([^)]+)\)', text)
        destinations += re.findall(r'^\[[^\]]+\]:\s*(.+)$', text, re.M)
        for value in destinations:
            value = value.strip()
            value = value[1:value.find('>')] if value.startswith('<') else value.split()[0]
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            links += 1
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(ROOT) or not target.exists():
                errors.append(str(path.relative_to(ROOT)) + ': missing/nonportable local link ' + value)
    skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
    for path in skills:
        text = path.read_text(encoding='utf-8')
        parts = text.split('---', 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append(str(path.relative_to(ROOT)) + ': missing frontmatter')
            continue
        fields = dict(re.findall(r'^([a-z_-]+):\s*(.+)$', parts[1], re.M))
        if fields.get('name') != path.parent.name or not fields.get('description'):
            errors.append(str(path.relative_to(ROOT)) + ': name/directory mismatch or missing description')
    return dict(status='pass' if not errors else 'fail', documents=len(documents),
                local_links=links, skills=len(skills), errors=errors,
                limits='Checks file destinations and basic name/description only; excludes fenced examples and historical development records. Does not verify external URLs, heading anchors or full YAML semantics.')


if __name__ == '__main__':
    result = check()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'pass' else 1)
