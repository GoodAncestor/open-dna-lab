"""Offline OpenLab record validation and bounded calibration analysis."""
from pathlib import Path
import argparse,csv,datetime,hashlib,json,math,statistics,sys
import yaml

class RecordError(ValueError): pass
def require(ok,message):
 if not ok: raise RecordError(message)
def number(value,label):
 try:x=float(value)
 except (ValueError,TypeError):raise RecordError(label+': finite numeric value required')
 require(math.isfinite(x),label+': finite numeric value required');return x
def timestamp(value):
 try:t=datetime.datetime.fromisoformat(str(value).replace('Z','+00:00'))
 except ValueError:raise RecordError('Invalid ISO timestamp: '+str(value))
 require(t.tzinfo is not None,'Timestamp requires timezone: '+str(value));return t
def unique(rows,key):
 out={}
 for r in rows:
  k=r.get(key);require(k and k not in out,'Missing or duplicate '+key+': '+str(k));out[k]=r
 return out
def local_artifact(base,name,checksum):
 require(bool(name),'Missing artifact')
 p=Path(name);require(not p.is_absolute() and '..' not in p.parts,'Artifact must be a relative local path')
 q=(base/p).resolve();require(q.is_relative_to(base.resolve()),'Artifact leaves record directory')
 require(q.is_file(),'Missing artifact: '+name)
 require(checksum=='sha256:'+hashlib.sha256(q.read_bytes()).hexdigest(),'Artifact checksum mismatch: '+name)

def validate(run,rows,plan,base):
 require(plan.get('source_kind') in ['fictional','standards_session'],'source_kind must be fictional or standards_session')
 require(run.get('run_id')==plan.get('run_id'),'Plan/run ID mismatch')
 start=timestamp(run['timestamps']['start']);end=timestamp(run['timestamps']['end']);require(start<=end,'Session ends before start')
 instruments={(x['instrument_id'],x['configuration_id']) for x in run['instruments']}
 require(timestamp(plan['declared_at'])<=start,'Analysis plan declared after session start')
 standards=unique(run['standards'],'standard_id');criteria=unique(run['acceptance_criteria'],'criterion_id');measurements=unique(rows,'measurement_id')
 preps=plan['preparations'];calibrations=plan['calibrations'];samples=plan.get('sample_events',{})
 adaptations={a['adaptation_id'] for a in run.get('adaptations',[])}
 for std in standards.values():
  require(std['role'] in ['blank','calibration_standard','independent_check'],'Unknown standard role')
  require(std['unit']=='ng/uL','Standard concentration unit must be ng/uL')
  require(number(std['assigned_value'],'assigned concentration')>=0,'Negative standard concentration')
 calstocks={s.get('stock_id') for s in standards.values() if s['role']=='calibration_standard'}
 for std in standards.values():
  if std.get('independent_of_calibration_stock'):
   require(std.get('stock_id') and std['stock_id'] not in calstocks,'Check stock is shared with calibrators')
 units={'raw_fluorescence':'RFU','concentration':'ng/uL','scale_span_pixels':'pixel','absorbance':'1'}
 for c in criteria.values():require(timestamp(c['declared_at'])<=start,'Criterion declared after session start: '+c['criterion_id'])
 for a in run.get('artifacts',[]):local_artifact(base,a['artifact'],a['checksum'])
 for r in rows:
  id=r['measurement_id'];require(r['run_id']==run['run_id'],id+': wrong run')
  require((r['instrument_id'],r['configuration_id']) in instruments,id+': unknown instrument/configuration')
  require((r['protocol_id'],r['protocol_version'])==(str(run['protocol_id']),str(run['protocol_version'])),id+': protocol mismatch')
  require(start<=timestamp(r['timestamp'])<=end,id+': timestamp outside session')
  require(r['measurement'] in units and r['unit']==units[r['measurement']],id+': unsupported measurement/unit')
  require(r['status'] in ['measured','derived','not_measured','below_range','above_range','invalid'],id+': unknown status')
  require(r['qc_status'] in ['pass','fail','limited','pending','not_applicable'],id+': unknown QC status')
  if r['status'] in ['measured','derived']:number(r['value'],id)
  else:require(r['value']=='' and bool(r['notes']),id+': censored/missing/invalid value must be empty with a reason')
  require(r['criterion_id'] in criteria,id+': unknown acceptance criterion')
  if r['sample_id']:require(samples.get(r['sample_id'])==r['event_id'] and bool(r['event_id']),id+': unknown specimen/event join')
  elif r['event_id']:require(r['event_id'] in samples.values(),id+': unknown event')
  local_artifact(base,r['artifact'],r['checksum'])
  if r['adaptation_id']:require(r['adaptation_id'] in adaptations,id+': unknown adaptation')
  if r['standard_id']:require(r['standard_id'] in standards,id+': unknown standard')
  if r['standard_id']:require(r['matrix']==standards[r['standard_id']]['matrix'],id+': matrix differs from standard')
  if r['measurement'] in ['raw_fluorescence','concentration']:
   require(r['preparation_id'] in preps,id+': unknown preparation')
   prep=preps[r['preparation_id']]
   pre=number(prep['pre_dilution'],id);volume=number(prep['assay_volume_ul'],id);aliquot=number(prep['sample_aliquot_ul'],id)
   require(pre>=1 and volume>0 and aliquot>0 and aliquot<=volume,id+': physical dilution quantities require pre_dilution>=1 and 0<aliquot<=assay volume')
   dilution=pre*volume/aliquot
   require(dilution>=1 and math.isclose(number(r['dilution_factor'],id),dilution,rel_tol=1e-9),id+': total dilution mismatch; avoid double application')
   require(r['calibration_id'] in calibrations,id+': unknown calibration')
   cal=calibrations[r['calibration_id']]
   require((r['instrument_id'],r['configuration_id'],r['matrix'])==(cal['instrument_id'],cal['configuration_id'],cal['matrix']),id+': calibration configuration/matrix mismatch')
   if r['blank_id']:
    require(r['blank_id'] in measurements,id+': unknown blank')
    blank=measurements[r['blank_id']];require(blank['calibration_id']==r['calibration_id'],id+': blank belongs to another calibration');require(standards.get(blank['standard_id'],{}).get('role')=='blank',id+': blank link is not a blank')
  sources=[x for x in r['derived_from'].split(';') if x]
  require(all(x in measurements and x!=id for x in sources),id+': unknown/self derived source')
  if r['status']=='derived':require(bool(sources),id+': derived value needs source IDs')
  if r['measurement']=='concentration' and r['status']=='derived':
   require(len(sources)==1,id+': concentration requires one raw check source')
   src=measurements[sources[0]]
   require(src['measurement']=='raw_fluorescence' and standards[src['standard_id']]['role']=='independent_check',id+': concentration source must be raw withheld check')
   require(all(r[k]==src[k] for k in ['calibration_id','preparation_id','dilution_factor','standard_id']),id+': concentration/source metadata mismatch')
 for calid,c in calibrations.items():
  fluorescence=any(r['calibration_id']==calid and r['measurement'] in ['raw_fluorescence','concentration'] for r in rows)
  microscopy=any(x['calibration_id']==calid for x in plan.get('scale_spans',[]))
  require(c['criterion_id'] in criteria,'Unknown calibration criterion')
  keys=[]
  if fluorescence:
   require(c['concentration_unit']=='ng/uL','Only ng/uL concentration calibration supported')
   keys+=['blank_drift_max_rfu','check_recovery_min_pct','check_recovery_max_pct','repeatability_max_cv_pct']
  if microscopy:keys+=['scale_error_max_pct']
  for k in keys:
   require(number(c[k],k)>=0,'Acceptance limits must be nonnegative: '+k)
   require(criteria[c['criterion_id']]['limit'].get(k)==c[k],'Plan limit differs from predeclared criterion: '+k)
  if fluorescence:require(c['check_recovery_min_pct']<=c['check_recovery_max_pct'],'Recovery limits reversed')
 require(len({s['measurement_id'] for s in plan.get('scale_spans',[])})==len(plan.get('scale_spans',[])),'Duplicate microscope span')
 for span in plan.get('scale_spans',[]):
  require(span['calibration_id'] in calibrations,'Unknown span calibration')
  require(span['measurement_id'] in measurements,'Unknown microscope span')
  require(span['role'] in ['calibration','withheld_check'],'Unknown span role')
  require(number(span['known_um'],'known_um')>0,'Scale length must be positive')
 return standards

def fit_line(points):
 require(len(points)>=3 and len({x for x,y in points})>=3,'Calibration requires three distinct levels')
 xm=statistics.mean(x for x,y in points);ym=statistics.mean(y for x,y in points)
 slope=sum((x-xm)*(y-ym) for x,y in points)/sum((x-xm)**2 for x,y in points)
 require(slope>0,'Calibration slope must be positive');return slope,ym-slope*xm

def analyze(run,rows,plan,standards):
 results=[];calout=[];blanks=[];repeat=[];spans=[];excluded=[];prep_repeat=[];byid={r['measurement_id']:r for r in rows}
 for r in rows:
  if r['status'] not in ['measured','derived'] or r['qc_status']=='fail':excluded.append(dict(measurement_id=r['measurement_id'],status=r['status'],reason=r['notes'] or 'record QC fail'))
 for calid,c in plan['calibrations'].items():
  raw=[r for r in rows if r['calibration_id']==calid and r['measurement']=='raw_fluorescence' and r['status']=='measured' and r['qc_status']!='fail']
  if raw:
   groups={}
   for r in raw:groups.setdefault(r['preparation_id'],[]).append(r)
   points=[];cal_groups=[]
   for prep,rr in groups.items():
    ids={r['standard_id'] for r in rr};require(len(ids)==1,'Preparation mixed standards: '+prep)
    std=standards[rr[0]['standard_id']];ys=[number(r['value'],prep) for r in rr];mean=statistics.mean(ys)
    require(len({(r['instrument_id'],r['configuration_id'],r['matrix']) for r in rr})==1,'Preparation mixes configuration/matrix')
    cv=100*statistics.stdev(ys)/abs(mean) if len(ys)>1 and mean!=0 else None
    repeat.append(dict(source_qc_status=';'.join(sorted({r['qc_status'] for r in rr})),preparation_id=prep,standard_role=std['role'],read_repeats=len(ys),mean_signal=mean,sd_signal=statistics.stdev(ys) if len(ys)>1 else None,cv_pct=cv,criterion_result='pending' if cv is None else ('within_limit' if cv<=c['repeatability_max_cv_pct'] else 'outside_limit')))
    if std['role']=='calibration_standard':
     require(all(float(r['dilution_factor'])==1 for r in rr),'Calibrator values must name final assay concentration, dilution=1')
     points.append((number(std['assigned_value'],prep),mean));cal_groups.append((prep,number(std['assigned_value'],prep),mean))
   prep_groups={}
   for prep,rr in groups.items():
    key=(rr[0]['standard_id'],float(rr[0]['dilution_factor']))
    prep_groups.setdefault(key,[]).append(statistics.mean(float(r['value']) for r in rr))
   for (std,dilution),values in prep_groups.items():
    mean=statistics.mean(values);sd=statistics.stdev(values) if len(values)>1 else None
    prep_repeat.append(dict(source_qc_status=';'.join(sorted({r['qc_status'] for r in raw if r['standard_id']==std and float(r['dilution_factor'])==dilution})),calibration_id=calid,standard_id=std,dilution_factor=dilution,independent_preparations=len(values),mean_signal=mean,sd_signal=sd,cv_pct=100*sd/abs(mean) if sd is not None and mean!=0 else None))
   slope,intercept=fit_line(points);lo=min(x for x,y in points);hi=max(x for x,y in points)
   calout.append(dict(source_qc_status=';'.join(sorted({r['qc_status'] for r in raw if standards[r['standard_id']]['role']=='calibration_standard'})),calibration_id=calid,slope_rfu_per_ng_ul=slope,intercept_rfu=intercept,range_min_ng_ul=lo,range_max_ng_ul=hi,preparations=len(points)))
   for prep,x,y in cal_groups:results.append(dict(kind='calibration',source_qc_status=';'.join(sorted({r['qc_status'] for r in groups[prep]})),measurement_id=prep,assigned=x,estimated=(y-intercept)/slope,residual_rfu=y-(slope*x+intercept),recovery_pct=None,dilution_factor=1,criterion_result='calibration_only'))
   br=sorted([r for r in raw if standards[r['standard_id']]['role']=='blank'],key=lambda r:timestamp(r['timestamp']))
   if len(br)>=2:
    drift=float(br[-1]['value'])-float(br[0]['value'])
    blanks.append(dict(source_qc_status=';'.join(sorted({r['qc_status'] for r in br})),calibration_id=calid,first_rfu=float(br[0]['value']),last_rfu=float(br[-1]['value']),drift_rfu=drift,reads=len(br),criterion_result='within_limit' if abs(drift)<=c['blank_drift_max_rfu'] else 'outside_limit'))
   else:blanks.append(dict(source_qc_status=';'.join(sorted({r['qc_status'] for r in br})),calibration_id=calid,reads=len(br),criterion_result='pending'))
   for r in raw:
    std=standards[r['standard_id']]
    if std['role']!='independent_check':continue
    assay=(float(r['value'])-intercept)/slope;estimated=assay*float(r['dilution_factor']);assigned=number(std['assigned_value'],'check assigned')
    require(assigned>0,'Check concentration must be positive');recovery=100*estimated/assigned
    within=lo<=assay<=hi;independent=std.get('independent_of_calibration_stock') is True
    outcome='outside_calibrated_range' if not within else ('pending_stock_independence' if not independent else ('within_limit' if c['check_recovery_min_pct']<=recovery<=c['check_recovery_max_pct'] else 'outside_limit'))
    results.append(dict(kind='withheld_check',source_qc_status=r['qc_status'],measurement_id=r['measurement_id'],assigned=assigned,estimated=estimated,residual_rfu=None,recovery_pct=recovery,dilution_factor=float(r['dilution_factor']),criterion_result=outcome))
    for derived in rows:
     if derived['measurement']=='concentration' and derived['status']=='derived' and derived['derived_from']==r['measurement_id']:
      require(math.isclose(float(derived['value']),estimated,rel_tol=1e-6,abs_tol=1e-9),derived['measurement_id']+': derived concentration disagrees; possible double dilution')
  relevant=[s for s in plan.get('scale_spans',[]) if s['calibration_id']==calid and byid[s['measurement_id']]['status']=='measured' and byid[s['measurement_id']]['qc_status']!='fail']
  configurations={(byid[s['measurement_id']]['instrument_id'],byid[s['measurement_id']]['configuration_id']) for s in relevant}
  require(len(configurations)<=1,'Microscope spans mix optical configurations')
  cal_scales=[]
  for s in relevant:
   r=byid[s['measurement_id']]
   require(r['measurement']=='scale_span_pixels' and r['status']=='measured','Scale span must be measured pixels')
   pix=number(r['value'],'pixels');require(pix>0,'Pixel span must be positive')
   scale=float(s['known_um'])/pix
   if s['role']=='calibration':cal_scales.append(scale)
  ref=statistics.mean(cal_scales) if cal_scales else None
  for s in relevant:
   r=byid[s['measurement_id']];pix=float(r['value']);scale=float(s['known_um'])/pix
   err=100*(ref*pix/float(s['known_um'])-1) if ref else None
   spans.append(dict(source_qc_status=r['qc_status'],measurement_id=s['measurement_id'],axis=s['axis'],position=s['position'],role=s['role'],known_um=s['known_um'],pixels=pix,um_per_pixel=scale,reference_um_per_pixel=ref,check_error_pct=err,criterion_result='calibration_only' if s['role']=='calibration' else ('pending' if err is None else ('within_limit' if abs(err)<=c['scale_error_max_pct'] else 'outside_limit'))))
 return dict(source_kind=plan['source_kind'],run_id=run['run_id'],calibrations=calout,values=results,blank_drift=blanks,read_repeatability=repeat,microscope_spans=spans,preparation_repeatability=prep_repeat,excluded=excluded,interpretation='Calculation checks only. Reference agreement, matrix transfer and instrument fitness require review.')

def plots(result,out):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(2,3,figsize=(13,7),constrained_layout=True)
 vals=result['values'];cal=[x for x in vals if x['kind']=='calibration'];checks=[x for x in vals if x['kind']=='withheld_check']
 axes[0,0].scatter([x['assigned'] for x in cal],[x['estimated'] for x in cal]);axes[0,0].set(title='Calibration preparations',xlabel='Assigned assay ng/µL',ylabel='Estimated assay ng/µL')
 axes[0,1].scatter([x['assigned'] for x in cal],[x['residual_rfu'] for x in cal]);axes[0,1].axhline(0,c='gray');axes[0,1].set(title='Calibration residuals',xlabel='Assigned assay ng/µL',ylabel='RFU')
 axes[0,2].scatter([x['dilution_factor'] for x in checks],[x['recovery_pct'] for x in checks]);axes[0,2].axhline(100,c='gray');axes[0,2].set(title='Withheld checks by total dilution',xlabel='Total dilution factor',ylabel='Recovery (%)')
 for i,x in enumerate(result['blank_drift']):
  if 'drift_rfu' in x:axes[1,0].plot([0,1],[x['first_rfu'],x['last_rfu']],'o-',label=x['calibration_id'])
 axes[1,0].set(title='Blank start/end drift',xticks=[0,1],xticklabels=['first','last'],ylabel='Raw RFU')
 rr=[x for x in result['read_repeatability'] if x['cv_pct'] is not None];axes[1,1].bar(range(len(rr)),[x['cv_pct'] for x in rr]);axes[1,1].set(title='Repeated reads within preparations',xlabel='Preparation index (CSV retains IDs)',ylabel='Signal CV (%)')
 ss=result['microscope_spans'];axes[1,2].scatter(range(len(ss)),[x['um_per_pixel'] for x in ss]);axes[1,2].set(title='Micrometer spans: axis and position',xticks=range(len(ss)),xticklabels=[x['axis']+'/'+x['position'] for x in ss],ylabel='µm/pixel');axes[1,2].tick_params(axis='x',rotation=30,labelsize=7)
 fig.suptitle(('FICTIONAL VALIDATION DATA · ' if result['source_kind']=='fictional' else 'Standards session · ')+result['run_id']);fig.savefig(out/'calibration-review.png',dpi=140);plt.close(fig)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',required=True,type=Path);p.add_argument('--measurements',required=True,type=Path);p.add_argument('--plan',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--no-plots',action='store_true');args=p.parse_args()
 try:
  run=yaml.safe_load(args.run.read_text());rows=list(csv.DictReader(args.measurements.read_text().splitlines()));plan=yaml.safe_load(args.plan.read_text())
  standards=validate(run,rows,plan,args.run.parent);result=analyze(run,rows,plan,standards)
 except (RecordError,KeyError,ZeroDivisionError,yaml.YAMLError) as e:raise SystemExit('Record validation failed: '+str(e))
 if args.out.resolve() in {p.resolve().parent for p in [args.run,args.measurements,args.plan]}:raise SystemExit('Use a separate output directory to preserve input records')
 args.out.mkdir(parents=True,exist_ok=True)
 result['input_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.run,args.measurements,args.plan]}
 (args.out/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 for key in ['values','blank_drift','read_repeatability','preparation_repeatability','microscope_spans','excluded']:
  rr=result[key]
  fields=list(dict.fromkeys(k for r in rr for k in r)) if rr else ['measurement_id','status','reason']
  with (args.out/(key+'.csv')).open('w') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rr)
 if not args.no_plots:plots(result,args.out)
 print(json.dumps(dict(status='calculated',source_kind=result['source_kind'],measurements=len(rows),excluded=len(result['excluded']),output=str(args.out))))
if __name__=='__main__':main()
