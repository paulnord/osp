from playwright.sync_api import sync_playwright
from pathlib import Path
import json,time,sys
out=Path(__file__).resolve().parent
failed=False
with sync_playwright() as p:
 for engine in (sys.argv[1:] or ['chromium','firefox','webkit']):
  opts={'headless':True}
  browser=getattr(p,engine).launch(**opts);context=browser.new_context(viewport={'width':1800,'height':1100})
  if engine=='chromium':context.grant_permissions(['clipboard-read','clipboard-write'])
  page=context.new_page();errors=[];records=[]
  page.on('pageerror',lambda e:(errors.append(str(e)),print('ERROR',str(e),flush=True)))
  page.on('dialog',lambda d:d.dismiss())
  try:
   page.goto('http://127.0.0.1:8765/fit.html',wait_until='load')
   deadline=time.monotonic()+35
   while time.monotonic()<deadline and not errors:
    if 'BROWSER FIT READY' in page.locator('body').inner_text():break
    page.wait_for_timeout(100)
   if errors:raise RuntimeError(str(errors))
   page.wait_for_timeout(1000)
   for w,h in [(950,700),(1600,1000),(950,700)]:
    page.evaluate('([w,h])=>org.opensourcephysics.tools.BrowserFitTest.resize$I$I(w,h)',[w,h]);page.wait_for_timeout(300)
    baseline=None
    for n in [16,1,2,3,8,15,16]:
     page.evaluate('(n)=>org.opensourcephysics.tools.BrowserFitTest.select$I(n)',n);page.wait_for_timeout(200)
     snap=page.evaluate('org.opensourcephysics.tools.BrowserFitTest.snapshot$()')
     records.append({'width':w,'n':n,'snapshot':snap})
     layout=snap.split('|')[:3]
     if baseline is None:baseline=layout
     assert layout==baseline,('layout moved',baseline,layout)
    page.screenshot(path=str(out/(engine+'-fit-'+str(w)+'.png')))
   page.evaluate('org.opensourcephysics.tools.BrowserFitTest.setFixed$I$Z(0,true)');page.wait_for_timeout(200)
   constrained=page.evaluate('org.opensourcephysics.tools.BrowserFitTest.report$()')
   assert 'Free parameters: 2' in page.locator('body').inner_text().replace('\u00a0',' ')
   coefficient=next(row for row in constrained.splitlines() if row.startswith('A\t')).split('\t')
   assert coefficient[2:4]==['N/A','Yes'],coefficient
   page.evaluate('org.opensourcephysics.tools.BrowserFitTest.setFixed$I$Z(0,false)');page.wait_for_timeout(200)
   assert 'Free parameters: 3' in page.locator('body').inner_text().replace('\u00a0',' ')
   report=page.evaluate('org.opensourcephysics.tools.BrowserFitTest.report$()')
   assert report.startswith('SUMMARY OUTPUT\t'),report
   assert all(len(row.split('\t'))==5 for row in report.splitlines()),report
   # Exercise the actual copy button from a user gesture.
   page.get_by_text('Copy Fit Report',exact=True).click()
   page.wait_for_timeout(300)
   if engine=='chromium':
    clipboard=page.evaluate('navigator.clipboard.readText()')
    assert clipboard==report,('clipboard differs from report',clipboard[:100])
   print(engine,'UI selection/resize/report/copy click passed',flush=True)
  except Exception as e:errors.append(str(e))
  (out/(engine+'-fit.json')).write_text(json.dumps({'records':records,'errors':errors,'body':page.locator('body').inner_text()},indent=2))
  failed = failed or bool(errors)
  print(engine,errors,flush=True);browser.close()

sys.exit(1 if failed else 0)
