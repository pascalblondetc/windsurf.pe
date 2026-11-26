#!/usr/bin/env python3
"""Descarga el pronóstico de WindGuru para los spots del CPW y escribe pronostico.json."""
import json, subprocess, sys, datetime as dt
SPOTS={'negritos':209096,'pacasmayo':52627,'lima':1221049,'paracas':52615,'zarate':36374}
NAMES={'negritos':'Negritos','pacasmayo':'Pacasmayo','lima':'Chorrillos','paracas':'Bahía de Paracas','zarate':'Zárate'}
HOURS=list(range(7,20))   # 7h a 19h, hora de Lima
TZ=dt.timezone(dt.timedelta(hours=-5))
def get(q):
    out=subprocess.run(['curl','-sS','-m','25','-H','Referer: https://www.windguru.cz/','-H','User-Agent: Mozilla/5.0',
        'https://www.windguru.cz/int/iapi.php?'+q],capture_output=True,text=True,check=True).stdout
    return json.loads(out)
def series(fc,keys):
    base=fc['initstamp']; res={}
    for i,h in enumerate(fc['hours']):
        t=dt.datetime.fromtimestamp(base+h*3600,TZ)
        res[t.strftime('%Y-%m-%dT%H')]={k:(fc.get(k) or [None]*len(fc['hours']))[i] for k in keys}
    return res
def model_q(sid,m):
    return f"q=forecast&id_model={m['id_model']}&rundef={m['rundef']}&initstr={m['initstr']}&id_spot={sid}&cachefix={m['cachefix']}"
def r(v,n=0):
    return None if v is None else (round(v) if n==0 else round(v,n))
now=dt.datetime.now(TZ); today=now.date()
days=[(today+dt.timedelta(days=i)).isoformat() for i in range(3)]
doc={'src':'WindGuru','updated':now.isoformat(timespec='minutes'),'days':days,'spots':{}}
upd=[]
for key,sid in SPOTS.items():
    info=get(f'q=forecast_spot&id_spot={sid}')['tabs'][0]
    arr={m['id_model']:m for m in info['id_model_arr']}
    wind=get(model_q(sid,arr[3]))['fcst']; wid=info.get('id_model_wave') or 84
    wave=get(model_q(sid,arr[wid]))['fcst']
    upd.append(wind.get('update_last',''))
    W=series(wind,['WINDSPD','GUST','WINDDIR','TMPE']); V=series(wave,['HTSGW','PERPW','DIRPW'])
    out=[]
    for d in days:
        rows=[]
        for h in HOURS:
            k=f'{d}T{h:02d}'; w=W.get(k); v=V.get(k)
            if not w or w['WINDSPD'] is None: continue
            rows.append([h,r(w['WINDSPD']),r(w['GUST']),r(w['WINDDIR']),r(v and v['HTSGW'],1),r(v and v['PERPW']),r(v and v['DIRPW']),r(w['TMPE'])])
        out.append(rows)
    doc['spots'][key]={'id':sid,'name':NAMES[key],'rows':out}
last=max(u for u in upd if u) if any(upd) else ''
if last:
    t=dt.datetime.strptime(last,'%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).astimezone(TZ)
    meses=['ene','feb','mar','abr','may','jun','jul','ago','set','oct','nov','dic']
    doc['src']=f"WindGuru · GFS 13 km y GFS-Wave · {t.day} {meses[t.month-1]} {t:%H:%M}"
json.dump(doc,open(sys.argv[1] if len(sys.argv)>1 else 'pronostico.json','w'),ensure_ascii=False)
print(doc['src'],{k:[len(x) for x in v['rows']] for k,v in doc['spots'].items()})
