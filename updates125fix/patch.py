from pathlib import Path

# Execute the 1.25 patch with a corrected, escape-safe manifest tail.
source_path=Path('../../current/updates125/patch.py')
code=source_path.read_text()
marker='# Android Visualizer requires RECORD_AUDIO permission, even for a non-zero app-owned session.'
if marker not in code:
    raise SystemExit('1.25 manifest marker not found')
head=code[:code.index(marker)]
fixed=r'''# Android Visualizer requires RECORD_AUDIO permission, even for a non-zero app-owned session.
mp=Path('app/src/main/AndroidManifest.xml')
ms=mp.read_text()
if 'android.permission.RECORD_AUDIO' not in ms:
    import re
    m=re.search(r'<manifest[^>]*>',ms)
    if not m: raise SystemExit('manifest root not found')
    insertion=m.group(0)+'\n    <uses-permission android:name="android.permission.RECORD_AUDIO"/>'
    ms=ms[:m.start()]+insertion+ms[m.end():]
mp.write_text(ms)
'''
exec(compile(head+fixed,'updates125-fixed','exec'))
