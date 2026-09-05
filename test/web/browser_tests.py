from playwright.sync_api import sync_playwright
from pathlib import Path
import json,sys,time
out=Path(__file__).resolve().parent
failed=False
with sync_playwright() as p:
 for engine in (sys.argv[1:] or ['chromium','firefox','webkit']):
  options={'headless':True}
  browser=getattr(p,engine).launch(**options)
  for test in ['precision','report']:
   page=browser.new_page(viewport={'width':1200,'height':900});errors=[];logs=[]
   page.on('pageerror',lambda err:(errors.append(str(err)),print('ERROR: '+str(err),flush=True)))
   page.on('console',lambda msg:(logs.append(msg.type+': '+msg.text),print(msg.type+': '+msg.text,flush=True)))
   page.on('dialog',lambda d:(logs.append('DIALOG: '+d.message),d.dismiss()))
   try:
    page.goto('http://127.0.0.1:8765/'+test+'.html',wait_until='load',timeout=30000)
    deadline=time.monotonic()+30
    while time.monotonic()<deadline and not errors:
     if 'Passed:' in page.locator('body').inner_text() or any('AssertionError' in line for line in logs):break
     page.wait_for_timeout(100)
   except Exception as e:errors.append(str(e))
   body=page.locator('body').inner_text()
   if 'Passed:' not in body:errors.append('No passing test completion')
   failed = failed or bool(errors)
   (out/(engine+'-'+test+'.json')).write_text(json.dumps({'body':body,'errors':errors,'console':logs},indent=2))
   print(engine,test,body[-400:],errors,flush=True)
   page.close()
  browser.close()

sys.exit(1 if failed else 0)
