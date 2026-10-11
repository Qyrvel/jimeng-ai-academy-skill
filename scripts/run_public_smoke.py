from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]; PY=sys.executable; S=ROOT/'.agents/skills/ai-academy/scripts'
K=ROOT/'academy-data/jimeng/knowledge/pilot-knowledge-registry.json'; SR=ROOT/'academy-data/jimeng/sources/source-registry.json'; N=ROOT/'academy-data/jimeng/knowledge/normalization-review.json'
CUR=ROOT/'academy-data/jimeng/curriculum/jimeng-creator-academy-v1.json'; READY=ROOT/'academy-data/jimeng/curriculum/curriculum-readiness.json'; BP=ROOT/'academy-data/jimeng/curriculum/jimeng-creator-academy-v1-blueprint.json'
CM=ROOT/'academy-data/jimeng/course/jimeng-creator-academy-v1/course-manifest.json'; MAP=ROOT/'academy-data/jimeng/assessment/full-assessment-mapping.json'; M=ROOT/'academy-data/jimeng/assessment/mastery-map.json'; SET=ROOT/'academy-data/jimeng/assessment/full-assessments/full-assessment-set.json'
E=ROOT/'academy-data/jimeng/assessment/course-evaluation'; C=E/'course-evaluation-contract.json'; CMD=E/'course-evaluation-contract.md'; SNAP=E/'course-evaluation-canonical-snapshot.json'
G=[ROOT/'academy-data/jimeng/graph/seedance-pilot-graph-r2.json',ROOT/'academy-data/jimeng/graph/policy-pilot-graph-r1.json',ROOT/'academy-data/jimeng/graph/curriculum-readiness-core-graph-r2.json']
def run(label,args,timeout=90):
    try:p=subprocess.run([PY,'-X','utf8','-B',*map(str,args)],cwd=ROOT,text=True,capture_output=True,encoding='utf-8',errors='replace',timeout=timeout)
    except subprocess.TimeoutExpired: print(f'[FAIL] {label}: timeout'); return False
    first=next((x for x in p.stdout.splitlines() if x.strip()),'')
    ok=p.returncode==0; print(f"[{'PASS' if ok else 'FAIL'}] {label}: {first}")
    if not ok: print(p.stdout); print(p.stderr)
    return ok
ok=True
ok &= run('source registry',[S/'validate_source_registry.py',SR])
ok &= run('knowledge registry',[S/'validate_knowledge_registry.py',K,SR])
ok &= run('graph contract baseline',[S/'validate_graph_contract_baseline.py'])
ok &= run('curriculum',[S/'validate_curriculum.py',CUR,K,READY,*G])
ok &= run('lesson blueprint',[S/'validate_lesson_blueprints.py',BP,CUR,K,*G])
ok &= run('course assembly',[S/'validate_course_assembly.py',CM,CUR,BP,K,*G])
ok &= run('assessment mapping',[S/'validate_assessment_mapping.py',MAP,CM,K,*G])
ok &= run('mastery',[S/'validate_mastery.py',M,MAP,CM,*G])
ok &= run('full assessment set',[S/'validate_full_assessment_set.py',SET,'--course',CM,'--graphs',*G,'--knowledge',K,'--mapping',MAP,'--mastery-map',M],120)
ok &= run('course evaluation',[S/'validate_course_evaluation.py',C,SNAP,M,CM,*G,'--markdown',CMD])
ok &= run('materialization fixture',[S/'validate_materialization_registry.py',ROOT/'tests/evidence-materialization/valid-materialization-registry.json',SR])
man=json.loads(CM.read_text('utf-8')); full=json.loads(SET.read_text('utf-8')); mas=json.loads(M.read_text('utf-8')); actual=(len(man['module_order']),len(man['lesson_files']),len(full.get('assessments',full.get('assessment_files',[]))),len(mas['units'])); expected=(8,24,23,24)
counts=actual==expected; print(f"[{'PASS' if counts else 'FAIL'}] counts {actual}"); ok &= counts
print('PUBLIC_SMOKE: PASS' if ok else 'PUBLIC_SMOKE: FAIL'); raise SystemExit(0 if ok else 1)
