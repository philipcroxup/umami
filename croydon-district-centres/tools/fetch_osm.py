"""Download OpenStreetMap highways around every district centre (same query the page uses) and save
   both the raw Overpass JSON and the compact form embedded in the HTML."""
import json, math, sys, time, requests
# usage: python3 fetch_osm.py [boundaries.geojson] [out_compact.json] [out_raw.json]
BND=sys.argv[1] if len(sys.argv)>1 else 'district_centres.geojson'
OUT=sys.argv[2] if len(sys.argv)>2 else 'osm_compact.json'
RAW=sys.argv[3] if len(sys.argv)>3 else 'osm_raw.json'
fc=json.load(open(BND))
PAD=250
def llbox(ring,pad):
    lons=[p[0] for p in ring]; lats=[p[1] for p in ring]; s,n,w,e=min(lats),max(lats),min(lons),max(lons)
    dlat=pad/110574.2; dlon=pad/(111319.49*math.cos(math.radians((s+n)/2)))
    return s-dlat,w-dlon,n+dlat,e+dlon
parts=['  way["highway"](%s); // %s'%(','.join('%.6f'%v for v in llbox(f['geometry']['coordinates'][0],PAD)),f['properties']['name']) for f in fc['features']]
q='[out:json][timeout:120];\n(\n'+'\n'.join(parts)+'\n);\nout geom;'
print(q)
EPS=['https://overpass-api.de/api/interpreter','https://lz4.overpass-api.de/api/interpreter','https://z.overpass-api.de/api/interpreter']
for ep in EPS:
    try:
        r=requests.post(ep,data={'data':q},timeout=180,headers={'User-Agent':'croydon-district-centre-streets/1.0 (planning map build)'})
        print(ep,r.status_code,len(r.content))
        if r.status_code==200:
            j=r.json()
            if j.get('remark'): print('REMARK',j['remark'])
            if j.get('elements'): break
    except Exception as e: print(ep,'ERR',e)
    time.sleep(5)
else:
    sys.exit('no data: every Overpass endpoint failed')
json.dump(j,open(RAW,'w'))
ways=[]; seen=set()
for el in j['elements']:
    t=el.get('tags') or {}
    if el.get('type')!='way' or 'highway' not in t or not el.get('geometry') or t.get('area')=='yes' or el['id'] in seen: continue
    g=[]
    for p in el['geometry']:
        if p: g+= [round(p['lat'],7),round(p['lon'],7)]
    if len(g)<4: continue
    seen.add(el['id'])
    ways.append(dict(id=el['id'],h=t['highway'],n=t.get('name',''),r=t.get('ref',''),s=t.get('service',''),g=g))
base=(j.get('osm3s') or {}).get('timestamp_osm_base')
json.dump(dict(source='OpenStreetMap via Overpass API (overpass-api.de)',fetched=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),osmBase=base,query=q,ways=ways),open(OUT,'w'),separators=(',',':'))
print(len(ways),'ways; osm base',base)
