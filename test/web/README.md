# Browser validation of the curve-fit PR

This test setup invokes the repository's bundled SwingJS visitor with Eclipse JDT
outside Eclipse. It transpiles OSP source, serves the bundled runtime locally, and
uses Playwright. It tests Data Tool, not the complete Tracker video application.

Prerequisites: JDK 21, Maven, Python with Playwright and its browsers installed.
Commands below use a POSIX shell from the repository root. Output stays in this
test checkout; do not commit generated assets.

```sh
python test/ci/platform_tests.py build
mvn -f test/web/pom.xml dependency:copy-dependencies -DoutputDirectory=deps
python test/web/prepare_site.py
javac -cp 'test/web/deps/*:swingjs/j2s.core.jar' test/web/Transpile.java
java -Xmx2g -cp 'test/web:test/web/deps/*:swingjs/j2s.core.jar' Transpile src test/web/site/swingjs/j2s ALL
java -cp 'test/web:test/web/deps/*:swingjs/j2s.core.jar' Transpile src test/web/site/swingjs/j2s test/org/opensourcephysics/tools/CurveFitPrecisionTest.java test/org/opensourcephysics/tools/CurveFitReportTest.java test/web/BrowserFitTest.java test/org/opensourcephysics/tools/CurveFitConstraintTest.java
python -m playwright install chromium firefox webkit
python -m http.server 8765 --bind 127.0.0.1 --directory test/web/site
```

With the server running, in another terminal:

```sh
python test/web/browser_tests.py
python test/web/browser_fit.py
```

The first script expects 19 precision, 62 report, and 40 constraint assertions per engine. The
second exercises the Data Tool at 950x700, 1600x1000, and 950x700 again, selecting
16, 1, 2, 3, 8, 15, and 16 points at each size. It checks stable plot allocation,
parameter orientation and count, report column structure, and a real copy-button
click. Chromium also compares the clipboard contents to the generated report.
JSON logs and screenshots are written beside these scripts. Firefox and WebKit
clipboard contents are not read back. WebKit automation is not a Safari or iOS
device test. No mobile touch behavior or video decoding is covered.

The numerical constraint fixture uses model updates in SwingJS because its tables
are not attached to a DOM. The separate browser UI test edits the actual checkbox
in the visible Data Tool and checks the updated free-parameter count and report.
