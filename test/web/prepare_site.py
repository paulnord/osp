from pathlib import Path
import zipfile, shutil
root=Path('test/web/site')
with zipfile.ZipFile('swingjs/SwingJS-site.zip') as z:z.extractall(root)
for base in [Path('src'),Path('resources')]:
    for p in base.rglob('*'):
        if p.is_file() and p.suffix!='.java':
            d=root/'swingjs/j2s'/p.relative_to(base)
            d.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(p,d)
for archive in root.rglob('osp-assets.zip'):
    with zipfile.ZipFile(archive) as z:entries={name:z.read(name) for name in z.namelist()}
    for name in entries:
        source=Path('src')/name
        if source.is_file():entries[name]=source.read_bytes()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in entries.items():z.writestr(name,data)
core=root/'swingjs/j2s/core';core.mkdir(exist_ok=True);(core/'package.js').write_text('// No precompiled application core in this source test.\n')
for page,main in [('precision','CurveFitPrecisionTest'),('report','CurveFitReportTest'),('fit','BrowserFitTest')]:
    (root/(page+'.html')).write_text('''<!doctype html><html><head><meta charset="utf-8"><script src="swingjs/swingjs2.js"></script></head><body><div id="sysoutdiv"></div><script>
var Info={main:'org.opensourcephysics.tools.'''+main+'''',core:'NONE',width:950,height:700,j2sPath:'swingjs/j2s',console:'sysoutdiv',allowjavascript:true};
SwingJS.getApplet('testApplet',Info);
</script></body></html>''')
