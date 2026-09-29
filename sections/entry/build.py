"""Builds index.html (standalone) and artifact.html (body-only) from the package data + template.html."""
import csv, json, sys, zipfile, io, glob, os
here = os.path.dirname(os.path.abspath(__file__))
zpath = glob.glob(os.path.join(here, '..', '..', 'World_Future_Model_Codex_Package_*.zip'))[0]
z = zipfile.ZipFile(zpath)
def rd(name):
    p = [n for n in z.namelist() if n.endswith('/data/' + name)][0]
    return list(csv.DictReader(io.StringIO(z.read(p).decode('utf-8'))))
reg, sc, th, imp = rd('country_registry_197.csv'), rd('core_scenarios.csv'), rd('priority_country_theses.csv'), rd('scenario_country_impacts_major.csv')
ids = [s['scenario_id'] for s in sc]
thesis = {r['country']: r['base_case_thesis'] for r in th}
impact = {r['country']: [int(r[i]) for i in ids] for r in imp}
priors = [int(s['subjective_prior_pct']) for s in sc]
def score(c): return sum(p * v for p, v in zip(priors, impact[c])) / 100
countries = []
for r in reg:
    c = r['country']
    countries.append({'n': c, 'i': r['iso3'], 'r': r['region'], 't': thesis.get(c), 'm': impact.get(c)})
countries.sort(key=lambda c: (c['m'] is None, -score(c['n']) if c['m'] else 0, c['n']))
data = {'asOf': '2026-08-26', 'scenarios': [{'id': s['scenario_id'], 'name': s['name'], 'prior': int(s['subjective_prior_pct']), 'desc': s['description'], 'win': s['relative_winners'], 'lose': s['relative_losers']} for s in sc], 'countries': countries}
tpl = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
body = tpl.replace('/*DATA*/', 'const DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';')
open(os.path.join(here, 'artifact.html'), 'w', encoding='utf-8').write(body)
full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<style>html,body{margin:0;height:100%}</style>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
open(os.path.join(here, 'index.html'), 'w', encoding='utf-8').write(full)
print(len(countries), 'countries;', sum(1 for c in countries if c['m']), 'modeled')
