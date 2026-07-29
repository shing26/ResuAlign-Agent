import os

root = r'D:\ResuAlign\backend\resume_align'

# 1. Copy untracked __init__.py files
init_pairs = [
    (r'D:\ResuAlign\backend\resume_align\agents\__init__.py', r'D:\ResuAlign\backend\resume_align\services\agents\__init__.py'),
    (r'D:\ResuAlign\backend\resume_align\parsers\__init__.py', r'D:\ResuAlign\backend\resume_align\services\parsers\__init__.py'),
    (r'D:\ResuAlign\backend\resume_align\llm\__init__.py', r'D:\ResuAlign\backend\resume_align\infra\llm\__init__.py'),
]
for src, dst in init_pairs:
    if os.path.exists(src):
        c = open(src, 'r', encoding='utf-8').read()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(c)
        print(f'Copied {os.path.basename(dst)}')

# 2. Rewrite domain/resume.py (Pydantic-only)
open(os.path.join(root, 'domain', 'resume.py'), 'w', encoding='utf-8').write('''"""Resume context model (Pydantic)."""

from pydantic import BaseModel


class ResumeContext(BaseModel):
    raw_text: str = ""
''')
print('domain/resume.py: Pydantic only')

# 3. Rewrite domain/job.py (Pydantic-only)
open(os.path.join(root, 'domain', 'job.py'), 'w', encoding='utf-8').write('''"""Job context model (Pydantic)."""

from pydantic import BaseModel


class JobContext(BaseModel):
    raw_text: str = ""
    title: str = ""
    company: str = ""
''')
print('domain/job.py: Pydantic only')

# 4. Update domain/__init__.py
open(os.path.join(root, 'domain', '__init__.py'), 'w', encoding='utf-8').write('''from .diff import DiffDelta, DiffItem, DiffType, ConfidenceLevel
from .resume import ResumeContext
from .job import JobContext

__all__ = ["DiffDelta", "DiffItem", "DiffType", "ConfidenceLevel", "ResumeContext", "JobContext"]
''')
print('domain/__init__.py updated')

# 5. Update infra/orm/__init__.py (SQLAlchemy exports)
open(os.path.join(root, 'infra', 'orm', '__init__.py'), 'w', encoding='utf-8').write('''from .base import Base, engine, async_session, get_session, init_db
from .resume import Resume, ResumeSection
from .job import JobDescription, JobEmbedding
from .diagnostic import DiagnosticReport, TailoringResult

__all__ = ["Base", "engine", "async_session", "get_session", "init_db",
           "Resume", "ResumeSection", "JobDescription", "JobEmbedding",
           "DiagnosticReport", "TailoringResult"]
''')
print('infra/orm/__init__.py updated')

# 6. Update all imports across all Python files
import_mappings = [
    ('resume_align.config', 'resume_align.core.config'),
    ('resume_align.pipeline', 'resume_align.core.pipeline'),
    ('resume_align.session_store', 'resume_align.core.session_store'),
    ('resume_align.models.diff', 'resume_align.domain.diff'),
    ('resume_align.models.resume', 'resume_align.domain.resume'),
    ('resume_align.models.job', 'resume_align.domain.job'),
    ('resume_align.models.base', 'resume_align.infra.orm.base'),
    ('resume_align.models.diagnostic', 'resume_align.infra.orm.diagnostic'),
    ('resume_align.agents.', 'resume_align.services.agents.'),
    ('resume_align.parsers.', 'resume_align.services.parsers.'),
    ('resume_align.llm.', 'resume_align.infra.llm.'),
    ('resume_align.shield.redis_cache', 'resume_align.infra.redis_cache'),
    ('resume_align.shield.rate_limiter', 'resume_align.infra.rate_limiter'),
]

all_py_files = []
for dirpath, dirnames, filenames in os.walk(root):
    for f in filenames:
        if f.endswith('.py') and '__pycache__' not in dirpath:
            all_py_files.append(os.path.join(dirpath, f))

# Also include tests
tests_dir = r'D:\ResuAlign\tests'
for dirpath, dirnames, filenames in os.walk(tests_dir):
    for f in filenames:
        if f.endswith('.py') and '__pycache__' not in dirpath:
            all_py_files.append(os.path.join(dirpath, f))

changed = 0
for fp in all_py_files:
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    original = c
    for old, new in import_mappings:
        c = c.replace(old, new)
    if c != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        changed += 1

print(f'Updated imports in {changed} files')

# 7. Delete old empty source directories
import shutil
for d in ['agents', 'parsers', 'llm']:
    dp = os.path.join(root, d)
    if os.path.isdir(dp):
        remaining = os.listdir(dp)
        if not remaining or all(f == '__pycache__' for f in remaining):
            shutil.rmtree(dp)
            print(f'Removed empty {d}/')

print('All done!')