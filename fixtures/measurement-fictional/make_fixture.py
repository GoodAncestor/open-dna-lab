"""Generate explicitly fictional standards records; never real instrument evidence."""
from pathlib import Path
import csv,hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
raw=HERE/'raw/readings.txt';raw.write_text('FICTIONAL readings generated for software validation. No physical measurement.\nFluorescence model: RFU = 10 + 100 * assay concentration, with stated small offsets.\nMicroscope spans are fictional pixel distances.\n')
sha='sha256:'+hashlib.sha256(raw.read_bytes()).hexdigest();fields=next(csv.reader((ROOT/'templates/openlab-measurements.csv').open()));rows=[];std=[];preps={}
limits=dict(blank_drift_max_rfu=2,check_recovery_min_pct=90,check_recovery_max_pct=110,repeatability_max_cv_pct=5,scale_error_max_pct=2)
run=dict(record_version=1,run_id='FICTIONAL-001',purpose='Fictional software validation only',sample_id=None,event_id=None,operator='fictional',timestamps=dict(start='2026-09-18T09:00:00+00:00',end='2026-09-18T12:00:00+00:00'),protocol_id='FICTIONAL-STANDARDS',protocol_version='1',instruments=[dict(instrument_id='fluorometer',configuration_id='optics1',configuration=dict(LED='fictional',gain=1)),dict(instrument_id='microscope',configuration_id='objective1',configuration=dict(objective='fictional',camera='fictional'))],standards=std,acceptance_criteria=[dict(criterion_id='limits1',measurement='fictional_session_checks',limit=limits,unit='see named limit units',rationale_or_source='Fictional software test limits; not acceptance for a physical assay',declared_at='2026-09-17T09:00:00+00:00')],artifacts=[dict(artifact_id='raw1',artifact='raw/readings.txt',checksum=sha,role='fictional_raw_readings')],qc=dict(status='pending',limitations=['No real instrument measurement']))
plan=dict(source_kind='fictional',run_id=run['run_id'],declared_at='2026-09-17T09:00:00+00:00',preparations=preps,sample_events={},calibrations={'curve1':dict(concentration_unit='ng/uL',criterion_id='limits1',instrument_id='fluorometer',configuration_id='optics1',matrix='buffer',**limits)},scale_spans=[])
def add(id,standard,prep,value,dilution=1,repeat=1,measurement='raw_fluorescence',unit='RFU',instrument='fluorometer',config='optics1',time='2026-09-18T10:00:00+00:00',**kwargs):
 r=dict.fromkeys(fields,'');r.update(run_id=run['run_id'],measurement_id=id,protocol_id=run['protocol_id'],protocol_version='1',instrument_id=instrument,configuration_id=config,operator='fictional',timestamp=time,measurement=measurement,value=value,unit=unit,status='measured',qc_status='pending',criterion_id='limits1',standard_id=standard,preparation_id=prep,replicate=prep,read_repeat=repeat,matrix='buffer',dilution_factor=dilution,blank_id='blank-start' if standard!='blank' else '',calibration_id='curve1',artifact='raw/readings.txt',checksum=sha,notes='FICTIONAL generated observation',**kwargs);rows.append(r);return r
std.append(dict(standard_id='blank',role='blank',matrix='buffer',assigned_value=0,unit='ng/uL',stock_id='reagent',independent_of_calibration_stock=False))
preps['blankprep']=dict(pre_dilution=1,assay_volume_ul=200,sample_aliquot_ul=200)
add('blank-start','blank','blankprep',10,time='2026-09-18T09:05:00+00:00');add('blank-end','blank','blankprep',11,repeat=2,time='2026-09-18T11:50:00+00:00')
for level in [1,3,6]:
 sid=f'cal{level}';std.append(dict(standard_id=sid,role='calibration_standard',matrix='buffer',assigned_value=level,unit='ng/uL',stock_id='cal-stock',independent_of_calibration_stock=False))
 for prepnum,offset in enumerate([-1,0,1],1):
  prep=f'{sid}-prep{prepnum}';preps[prep]=dict(pre_dilution=1,assay_volume_ul=200,sample_aliquot_ul=200)
  for repeat,read_offset in enumerate([-.25,.25],1):add(f'{prep}-read{repeat}',sid,prep,10+100*level+offset+read_offset,repeat=repeat)
std.append(dict(standard_id='check50',role='independent_check',matrix='buffer',assigned_value=50,unit='ng/uL',stock_id='check-stock',independent_of_calibration_stock=True))
for dilution in [10,20]:
 for prepnum,offset in enumerate([-1,1],1):
  prep=f'check-d{dilution}-prep{prepnum}';preps[prep]=dict(pre_dilution=1,assay_volume_ul=200,sample_aliquot_ul=200/dilution)
  for repeat in [1,2]:add(f'{prep}-read{repeat}','check50',prep,10+100*50/dilution+offset,dilution=dilution,repeat=repeat)
for id,pixels,known,axis,position,role in [('span1',2000,100,'x','center','calibration'),('span2',4000,200,'y','center','calibration'),('span3',1990,100,'x','edge','withheld_check'),('span4',2010,100,'y','edge','withheld_check')]:
 add(id,'','',pixels,measurement='scale_span_pixels',unit='pixel',instrument='microscope',config='objective1')
 plan['scale_spans'].append(dict(measurement_id=id,known_um=known,axis=axis,position=position,role=role,calibration_id='curve1'))
(HERE/'run.json').write_text(json.dumps(run,indent=2)+'\n');(HERE/'analysis-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
with (HERE/'measurements.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
