from pathlib import Path

# Playback controls: from a cold start, any obvious playback action starts My Wave.
p=Path('app/src/main/java/ru/classic/music/PlaybackService.java')
s=p.read_text()

def one(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

one('''    void toggleShuffle(){shuffle=!shuffle;changed();}''','''    void toggleShuffle(){shuffle=!shuffle;if(current==null){startWave();return;}changed();}''','shuffle starts wave')
one('''    void resume(){\n        if(!ready){if(current!=null)load();return;}foreground();''','''    void resume(){\n        if(current==null){startWave();return;}\n        if(!ready){load();return;}foreground();''','play starts wave')
one('''    void previous(){\n        if(position()>3000){seek(0);return;}if(index>0){finishFeedback("skip");index--;load();}\n    }''','''    void previous(){\n        if(current==null){startWave();return;}\n        if(position()>3000){seek(0);return;}if(index>0){finishFeedback("skip");index--;load();}\n    }''','previous starts wave')
one('''    void next(boolean completed){\n        if(current==null)return;finishFeedback(completed?"trackFinished":"skip");''','''    void next(boolean completed){\n        if(current==null){startWave();return;}finishFeedback(completed?"trackFinished":"skip");''','next starts wave')
p.write_text(s)

# UI controls must stop Activity-level radio before cold-starting Yandex playback.
p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()
one_ui=lambda old,new,label: None

def ui(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

ui('''transport=row();addWeighted(transport,button("‹  назад",()->{if(service!=null)service.previous();}));play=primaryButton("▶  играть",()->{if(service!=null)service.toggle();});addWeighted(transport,play);addWeighted(transport,button("дальше  ›",()->{if(service!=null)service.next(false);}));controls.addView(transport);''','''transport=row();addWeighted(transport,button("‹  назад",()->{if(service!=null){if(service.current==null)stopRadio(true);service.previous();}}));play=primaryButton("▶  играть",()->{if(service!=null){if(service.current==null)stopRadio(true);service.toggle();}});addWeighted(transport,play);addWeighted(transport,button("дальше  ›",()->{if(service!=null){if(service.current==null)stopRadio(true);service.next(false);}}));controls.addView(transport);''','transport cold start')
ui('''shuffle=button("вразброс",()->{if(service!=null)service.toggleShuffle();});''','''shuffle=button("вразброс",()->{if(service!=null){if(service.current==null)stopRadio(true);service.toggleShuffle();}});''','shuffle cold start')
p.write_text(s)

# Dedicated launcher icon; keep ic_music as the notification small icon.
p=Path('app/src/main/AndroidManifest.xml')
s=p.read_text()
old='android:icon="@drawable/ic_music"'
new='android:icon="@drawable/ic_launcher"'
if s.count(old)!=1:
    raise SystemExit(f'launcher manifest: expected 1 match, got {s.count(old)}')
p.write_text(s.replace(old,new,1))
