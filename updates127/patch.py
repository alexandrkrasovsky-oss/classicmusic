from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Keep the large now-playing block coherent for both Yandex tracks and the independent radio player.
# Radio gets the station name instead of "ничего не играет", plus a small symbolic antenna cover.
helper='''    private void updateNowPlayingIdentity(){
        if(title==null||artist==null||cover==null)return;
        boolean has=service!=null&&service.current!=null;
        boolean radioActive=radioState==1||radioState==2;
        if(radioActive){
            String station=(radioIndex>=0&&radioIndex<radioNames.length)?radioNames[radioIndex].toLowerCase(Locale.ROOT):"радио";
            title.setText(station);
            artist.setText(radioState==1?"радио · загрузка…":"радио");
            cover.setPadding(dp(24),dp(24),dp(24),dp(24));
            cover.setImageResource(ru.classic.music.R.drawable.ic_radio_cover);
            cover.setContentDescription("Радио: "+station);
        }else{
            title.setText(has?lower(service.current.name()):"ничего не играет");
            artist.setText(has?lower(service.current.artist):"");
            if(has&&service.artwork!=null){cover.setPadding(0,0,0,0);cover.setImageBitmap(service.artwork);}
            else{cover.setPadding(dp(26),dp(26),dp(26),dp(26));cover.setImageResource(ru.classic.music.R.drawable.ic_music);}
            cover.setContentDescription(has?"Обложка текущего трека":"Музыка");
        }
        cover.setColorFilter(activeTheme.albumTint,PorterDuff.Mode.SRC_ATOP);
    }

'''
s=one(s,
'''    private android.graphics.drawable.GradientDrawable radioGlow(int color){
''',
helper+'''    private android.graphics.drawable.GradientDrawable radioGlow(int color){
''',
'now playing identity helper')

# Every radio state transition refreshes the player text/cover immediately.
s=one(s,
'''        setRadioPowerState(radioState);
    }
''',
'''        setRadioPowerState(radioState);
        updateNowPlayingIdentity();
    }
''',
'radio refreshes player identity')

# The normal service UI updater also prefers active radio identity over the idle Yandex state.
s=one(s,
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;title.setText(has?lower(service.current.name()):"ничего не играет");artist.setText(has?lower(service.current.artist):"");
''',
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;updateNowPlayingIdentity();
''',
'radio aware title and artist')

# Artwork is now updated together with title/artist so radio cannot be overwritten by the generic music placeholder.
s=one(s,
'''        if(has&&service.artwork!=null){cover.setPadding(0,0,0,0);cover.setImageBitmap(service.artwork);}else{cover.setPadding(dp(26),dp(26),dp(26),dp(26));cover.setImageResource(ru.classic.music.R.drawable.ic_music);}cover.setColorFilter(activeTheme.albumTint,PorterDuff.Mode.SRC_ATOP);
''',
'''        updateNowPlayingIdentity();
''',
'radio aware artwork')

p.write_text(s)
