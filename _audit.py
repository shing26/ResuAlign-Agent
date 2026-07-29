import os, sys

root = r'D:\ResuAlign'

files = {
    'Backend routes': r'D:\ResuAlign\backend\resume_align\api\routes.py',
    'Backend schemas': r'D:\ResuAlign\backend\resume_align\api\schemas.py',
    'Backend pipeline': r'D:\ResuAlign\backend\resume_align\pipeline.py',
    'Backend diff model': r'D:\ResuAlign\backend\resume_align\models\diff.py',
    'Backend assertion': r'D:\ResuAlign\backend\resume_align\shield\assertion_checker.py',
    'Backend LLM client': r'D:\ResuAlign\backend\resume_align\llm\client.py',
    'Frontend App.vue': r'D:\ResuAlign\frontend\src\App.vue',
    'Frontend tailorStore': r'D:\ResuAlign\frontend\src\stores\tailorStore.ts',
    'Frontend types': r'D:\ResuAlign\frontend\src\types\diff.ts',
    'Frontend JobTargetSidebar': r'D:\ResuAlign\frontend\src\components\JobTargetSidebar.vue',
    'Frontend DiffCard': r'D:\ResuAlign\frontend\src\components\DiffCard.vue',
    'Frontend LivePreview': r'D:\ResuAlign\frontend\src\components\LivePreview.vue',
    'Frontend TargetHeader': r'D:\ResuAlign\frontend\src\components\TargetHeader.vue',
    'Frontend CreateTargetModal': r'D:\ResuAlign\frontend\src\components\CreateTargetModal.vue',
    'Frontend CyberTerminalHero': r'D:\ResuAlign\frontend\src\components\CyberTerminalHero.vue',
}

for name, path in files.items():
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            c = f.read()
        print(f'{name}: {len(c.split(chr(10)))} lines')
    else:
        print(f'{name}: MISSING')