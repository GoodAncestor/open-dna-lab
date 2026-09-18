from pathlib import Path
import copy,csv,json,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'software/measurement_pipeline'))
from pipeline import validate,analyze,RecordError
FIX=ROOT/'fixtures/measurement-fictional'
class MeasurementPipeline(unittest.TestCase):
 def setUp(self):
  self.run=json.loads((FIX/'run.json').read_text());self.plan=json.loads((FIX/'analysis-plan.json').read_text());self.rows=list(csv.DictReader((FIX/'measurements.csv').read_text().splitlines()))
 def calc(self):return analyze(self.run,self.rows,self.plan,validate(self.run,self.rows,self.plan,FIX))
 def reject(self):
  with self.assertRaises(RecordError):self.calc()
 def test_known_curve_and_withheld_dilutions(self):
  r=self.calc();c=r['calibrations'][0];self.assertAlmostEqual(c['slope_rfu_per_ng_ul'],100);self.assertAlmostEqual(c['intercept_rfu'],10);self.assertEqual(c['preparations'],9)
  checks=[x for x in r['values'] if x['kind']=='withheld_check'];self.assertEqual(len(checks),8);self.assertTrue(all(99<=x['recovery_pct']<=101 for x in checks))
  self.assertAlmostEqual(r['blank_drift'][0]['drift_rfu'],1);
  for x,want in zip(r['microscope_spans'],[0,0,-.5,.5]):self.assertAlmostEqual(x['check_error_pct'],want)
 def test_missing_is_not_zero(self):self.rows[0].update(status='below_range',value='0');self.reject()
 def test_censored_empty_is_excluded(self):
  r=copy.deepcopy(self.rows[-5]);r.update(measurement_id='missing',status='below_range',value='',notes='Below predeclared range');self.rows.append(r);self.assertEqual(self.calc()['excluded'][0]['measurement_id'],'missing')
 def test_unknown_specimen_event(self):self.rows[0].update(sample_id='specimen1',event_id='event2');self.reject()
 def test_unit_mismatch(self):self.rows[0]['unit']='ng/mL';self.reject()
 def test_duplicate_id(self):self.rows.append(copy.deepcopy(self.rows[0]));self.reject()
 def test_nan(self):self.rows[0]['value']='NaN';self.reject()
 def test_declared_after_measurement(self):self.plan['declared_at']='2026-09-18T11:00:00Z';self.reject()
 def test_plan_limits_match_predeclared_record(self):self.plan['calibrations']['curve1']['blank_drift_max_rfu']=100;self.reject()
 def test_total_dilution_not_applied_twice(self):self.rows[20]['dilution_factor']='100';self.reject()
 def test_derived_double_dilution(self):
  source=self.rows[20];r=copy.deepcopy(source);r.update(measurement_id='derived-check',measurement='concentration',unit='ng/uL',status='derived',derived_from=source['measurement_id'],value='499');self.rows.append(r);self.reject()
 def test_shared_stock_not_independent(self):self.run['standards'][-1]['stock_id']='cal-stock';self.reject()
 def test_out_of_range_is_explicit(self):
  self.rows[20]['value']='901';r=self.calc();x=next(x for x in r['values'] if x['measurement_id']==self.rows[20]['measurement_id']);self.assertEqual(x['criterion_result'],'outside_calibrated_range')
 def test_configuration_mismatch(self):
  self.run['instruments'].append(dict(instrument_id='fluorometer',configuration_id='optics2'));self.rows[20]['configuration_id']='optics2';self.reject()
 def test_artifact_tamper(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'raw').mkdir();(p/'raw/readings.txt').write_text('changed')
   with self.assertRaises(RecordError):validate(self.run,self.rows,self.plan,p)
 def test_private_absolute_artifact_rejected(self):self.rows[0]['artifact']='/etc/passwd';self.reject()
 def test_repeats_do_not_multiply_preparations(self):
  r=self.calc();x=next(x for x in r['preparation_repeatability'] if x['standard_id']=='cal1');self.assertEqual(x['independent_preparations'],3)
 def test_qc_failed_scale_not_used(self):
  self.rows[-1]['qc_status']='fail';r=self.calc();self.assertEqual(len(r['microscope_spans']),3);self.assertEqual(r['excluded'][0]['measurement_id'],'span4')
 def test_mixed_microscope_configuration(self):
  self.run['instruments'].append(dict(instrument_id='microscope',configuration_id='objective2'));self.rows[-1]['configuration_id']='objective2';self.reject()
 def test_unknown_span_calibration(self):self.plan['scale_spans'][0]['calibration_id']='unknown';self.reject()
if __name__=='__main__':unittest.main()
