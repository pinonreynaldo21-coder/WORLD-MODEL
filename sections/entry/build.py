"""Builds index.html (standalone) and artifact.html (body-only) from the package zip + template.html."""
import csv, json, zipfile, io, glob, os, collections
here = os.path.dirname(os.path.abspath(__file__))
z = zipfile.ZipFile(glob.glob(os.path.join(here, '..', '..', 'World_Future_Model_Codex_Package_*.zip'))[0])
def raw(name): return z.read([n for n in z.namelist() if n.endswith('/data/' + name)][0]).decode('utf-8')
def rd(name): return list(csv.DictReader(io.StringIO(raw(name))))
reg, sc, th, imp = rd('country_registry_197.csv'), rd('core_scenarios.csv'), rd('priority_country_theses.csv'), rd('scenario_country_impacts_major.csv')
ids = [s['scenario_id'] for s in sc]
thesis = {r['country']: r['base_case_thesis'] for r in th}
impact = {r['country']: [int(r[i]) for i in ids] for r in imp}
# approximate centroids (lat, lon) used only to aim the engraved globe on each card
LL = {'USA':(39,-98),'CHN':(35,104),'IND':(22,79),'MEX':(23,-102),'DEU':(51,10),'FRA':(46.5,2.5),'GBR':(54,-2),'ITA':(42.5,12.5),'ESP':(40,-4),'POL':(52,19),'RUS':(60,90),'UKR':(49,32),'JPN':(36,138),'KOR':(36.5,128),'TWN':(23.7,121),'VNM':(16,106.5),'MYS':(4,102),'IDN':(-2,118),'THA':(15,101),'PHL':(12,122),'SGP':(1.3,103.8),'AUS':(-25,134),'CAN':(58,-100),'BRA':(-10,-52),'ARG':(-35,-64),'CHL':(-33,-71),'TUR':(39,35),'SAU':(24,45),'ARE':(24,54),'ISR':(31.5,35),'IRN':(32,53),'EGY':(26.5,30),'MAR':(32,-6),'NGA':(9.5,8),'ZAF':(-29,25),'KEN':(0.5,38),'ETH':(9,39.5),'COD':(-3,23),'PAK':(30,70),'BGD':(24,90)}
RLL = {'Central & Eastern Europe':(49,22),'Central Africa':(0,18),'Central America & Caribbean':(15,-80),'Central Asia':(43,65),'East Africa':(-2,36),'East Asia':(38,115),'Middle East':(28,45),'North Africa':(28,10),'North America':(45,-95),'Oceania':(-12,165),'Russia & Caucasus':(45,45),'South America':(-15,-60),'South Asia':(24,80),'Southeast Asia':(10,108),'Southern Africa':(-22,25),'Southern Europe':(41,15),'West Africa':(10,-5),'Western & Northern Europe':(52,5)}
countries = []
for r in reg:
    c = r['country']; ll = LL.get(r['iso3'], RLL.get(r['region'], (20, 0)))
    countries.append({'n': c, 'i': r['iso3'], 'r': r['region'], 't': thesis.get(c), 'm': impact.get(c), 'll': ll})
alias = {'Türkiye': 'Turkey'}
projects = []
for p in rd('development_projects_seed.csv'):
    projects.append({'c': alias.get(p['country'], p['country']), 'name': p['project'], 'kind': 'Development', 'domain': p['sector'], 'stage': p['stage'], 'scale': p['scale'], 'prob': int(p['model_execution_probability_pct'] or 0) or None, 'effect': p['strategic_effect'], 'caution': p['caution']})
for p in rd('global_strategic_technology_projects.csv'):
    projects.append({'c': alias.get(p['country'], p['country']), 'name': p['initiative'], 'kind': 'Technology', 'domain': p['domain'], 'stage': p['stage'], 'maturity': p['maturity'], 'real': p['what_is_real'], 'effect': p['why_it_matters'], 'caution': p['main_caution'], 'url': p['source_url']})
blocs = [{'id': b['id'], 'name': b['name'], 'type': b['type'], 'core': b['core'], 'bridge': b.get('bridge_nodes', []), 'assets': b.get('assets', []), 'vuln': b.get('vulnerabilities', []), 'dir': b.get('2035_direction', '')} for b in json.loads(raw('future_influence_blocs.json'))]
src = rd('source_ledger.csv')
overlays = [{'id': o['overlay_id'], 'p': int(o['subjective_probability_pct']), 'd': o['description'], 'win': o['likely_beneficiaries'], 'lose': o['likely_negative_exposure']} for o in rd('scenario_overlays.csv')]
short = {'multipolar_technology_blocs': 'Multipolar Blocs', 'us_led_ai_capital': 'U.S.-Led AI', 'broad_ai_abundance': 'AI Abundance', 'china_industrial_open_models': 'China-Centered', 'fragmentation_shocks': 'Fragmentation'}
data = {'asOf': '2026-08-26',
        'scenarios': [{'id': s['scenario_id'], 'name': s['name'], 'short': short[s['scenario_id']], 'prior': int(s['subjective_prior_pct']), 'desc': s['description'], 'win': s['relative_winners'], 'lose': s['relative_losers']} for s in sc],
        'countries': countries, 'projects': projects, 'blocs': blocs, 'overlays': overlays,
        'groups': [{'n': g['name'], 'd': g['description']} for g in rd('population_beneficiary_groups.csv')],
        'sources': {'total': len(src), 'domains': collections.Counter(s['domain'] for s in src).most_common(25)}}
tpl = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
body = tpl.replace('/*DATA*/', 'const DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';')
open(os.path.join(here, 'artifact.html'), 'w', encoding='utf-8').write(body)
open(os.path.join(here, 'index.html'), 'w', encoding='utf-8').write(
    '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}</style>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
print(len(countries), 'countries,', len(projects), 'projects,', len(blocs), 'blocs')
