from pathlib import Path
import re


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Live vintage-style dual segment meters. Android's Visualizer gives a real low-quality
# waveform capture; adjacent samples feed the two display rows for a subtly different,
# signal-correlated L/R motion without changing the audio path.
s=one(s,
'''    private ImageView cover,footerMark;
''',
'''    private ImageView cover,footerMark;
    private VuMeterView vuMeter;
    private android.media.audiofx.Visualizer vuVisualizer;
    private byte[] vuWave;
    private int vuSession=-1;
    private boolean compactControls=false;
''',
'vu fields')

s=one(s,
'''    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private LinearLayout column(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}
''',
'''    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}

    private final class VuMeterView extends View {
        private final android.graphics.Paint paint=new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
        private float left=0f,right=0f;
        VuMeterView(){super(MainActivity.this);setWillNotDraw(false);setContentDescription("Индикаторы уровня левого и правого каналов");}
        private float smooth(float old,float target){return target>old?old*.28f+target*.72f:old*.84f+target*.16f;}
        void setLevels(float l,float r){left=smooth(left,Math.max(0f,Math.min(1f,l)));right=smooth(right,Math.max(0f,Math.min(1f,r)));invalidate();}
        void reset(){left=right=0f;invalidate();}
        @Override protected void onDraw(android.graphics.Canvas c){
            super.onDraw(c);
            final int segments=12;
            float labelW=dp(13),gap=dp(2),rightPad=dp(2);
            float usable=Math.max(dp(72),getWidth()-labelW-rightPad);
            float segW=(usable-gap*(segments-1))/segments;
            float segH=dp(5),top=dp(2),rowGap=dp(5);
            paint.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));paint.setTextSize(dp(8));paint.setTextAlign(android.graphics.Paint.Align.LEFT);paint.setColor(mixColor(activeTheme.ink,activeTheme.muted,.58f));paint.setAlpha(150);
            c.drawText("L",0,top+segH,paint);c.drawText("R",0,top+segH+segH+rowGap,paint);paint.setAlpha(255);
            drawRow(c,labelW,top,segW,segH,gap,left,segments);
            drawRow(c,labelW,top+segH+rowGap,segW,segH,gap,right,segments);
        }
        private void drawRow(android.graphics.Canvas c,float x,float y,float segW,float segH,float gap,float level,int segments){
            int active=Math.max(0,Math.min(segments,Math.round(level*segments)));
            for(int i=0;i<segments;i++){
                boolean overload=i>=segments-2;
                int live=overload?0xffB95E55:0xff55936A;
                int idle=overload?0x20B95E55:0x2055936A;
                paint.setColor(i<active?live:idle);
                android.graphics.RectF r=new android.graphics.RectF(x+i*(segW+gap),y,x+i*(segW+gap)+segW,y+segH);
                c.drawRoundRect(r,dp(1),dp(1),paint);
            }
        }
    }

    private LinearLayout column(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}
''',
'vu view class')

s=one(s,
'''        title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);title.setPadding(0,0,0,0);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);artist.setAlpha(.72f);copy.addView(artist);now.addView(copy,new LinearLayout.LayoutParams(0,-2,1));controls.addView(now);
''',
'''        title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);title.setPadding(0,0,0,0);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);artist.setAlpha(.72f);copy.addView(artist);
        vuMeter=new VuMeterView();vuMeter.setVisibility(View.GONE);LinearLayout.LayoutParams vuLp=new LinearLayout.LayoutParams(-1,dp(22));vuLp.topMargin=dp(4);copy.addView(vuMeter,vuLp);
        now.addView(copy,new LinearLayout.LayoutParams(0,-2,1));controls.addView(now);
''',
'add meters under artist')

s=one(s,
'''        if(adapter!=null)adapter.notifyDataSetChanged();
        updateRadioUi();
''',
'''        if(adapter!=null)adapter.notifyDataSetChanged();
        if(vuMeter!=null)vuMeter.invalidate();
        updateRadioUi();
''',
'vu follows theme')

s=one(s,
'''    private void configureControls(boolean compact){
        if(controls==null)return;
''',
'''    private void configureControls(boolean compact){
        if(controls==null)return;
        compactControls=compact;
''',
'remember compact state')

s=one(s,
'''            artist.setTextSize(12);artist.setMaxLines(1);artist.setGravity(Gravity.CENTER);
            seek.setVisibility(View.GONE);time.setVisibility(View.GONE);
''',
'''            artist.setTextSize(12);artist.setMaxLines(1);artist.setGravity(Gravity.CENTER);
            if(vuMeter!=null)vuMeter.setVisibility(View.GONE);
            seek.setVisibility(View.GONE);time.setVisibility(View.GONE);
''',
'hide meters in compact player')

s=one(s,
'''            artist.setTextSize(14);artist.setMaxLines(2);artist.setGravity(Gravity.START);
            seek.setVisibility(View.VISIBLE);time.setVisibility(View.VISIBLE);
''',
'''            artist.setTextSize(14);artist.setMaxLines(2);artist.setGravity(Gravity.START);
            if(vuMeter!=null)vuMeter.setVisibility(service!=null&&service.current!=null?View.VISIBLE:View.GONE);
            seek.setVisibility(View.VISIBLE);time.setVisibility(View.VISIBLE);
''',
'show meters in full player')

# Permission is requested only once, and only when a real track actually starts playing.
# Visualizer requires RECORD_AUDIO even for the app's own MediaPlayer session.
insert='''    private boolean hasVuPermission(){return Build.VERSION.SDK_INT<23||checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)==android.content.pm.PackageManager.PERMISSION_GRANTED;}
    private void maybeRequestVuPermission(){
        if(hasVuPermission()||service==null||service.current==null||!service.playing()||compactControls)return;
        android.content.SharedPreferences prefs=getSharedPreferences("ui",MODE_PRIVATE);
        if(prefs.getBoolean("vu_permission_asked",false))return;
        prefs.edit().putBoolean("vu_permission_asked",true).apply();
        Toast.makeText(this,"для живых L/R-индикаторов Android попросит доступ к аудио",Toast.LENGTH_LONG).show();
        if(Build.VERSION.SDK_INT>=23)requestPermissions(new String[]{android.Manifest.permission.RECORD_AUDIO},620);
    }
    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] grantResults){
        super.onRequestPermissionsResult(requestCode,permissions,grantResults);
        if(requestCode==620){if(grantResults.length>0&&grantResults[0]==android.content.pm.PackageManager.PERMISSION_GRANTED)ensureVuVisualizer();else{releaseVuVisualizer();if(vuMeter!=null)vuMeter.reset();}}
    }
    private void releaseVuVisualizer(){
        android.media.audiofx.Visualizer v=vuVisualizer;vuVisualizer=null;vuWave=null;vuSession=-1;
        if(v!=null){try{v.setEnabled(false);}catch(Throwable ignored){}try{v.release();}catch(Throwable ignored){}}
    }
    private void ensureVuVisualizer(){
        if(service==null||service.current==null||!service.playing()||!hasVuPermission())return;
        int session=service.audioSessionId();if(session<=0)return;
        if(vuVisualizer!=null&&vuSession==session)return;
        releaseVuVisualizer();
        try{
            android.media.audiofx.Visualizer v=new android.media.audiofx.Visualizer(session);
            int[] range=android.media.audiofx.Visualizer.getCaptureSizeRange();int size=256;if(size<range[0])size=range[0];if(size>range[1])size=range[1];
            v.setCaptureSize(size);if(Build.VERSION.SDK_INT>=16)v.setScalingMode(android.media.audiofx.Visualizer.SCALING_MODE_NORMALIZED);v.setEnabled(true);
            vuVisualizer=v;vuSession=session;vuWave=new byte[size];
        }catch(Throwable ignored){releaseVuVisualizer();}
    }
    private float vuLevel(long sum,int count){if(count<=0)return 0f;float rms=(float)Math.sqrt(sum/(double)count)/128f;return Math.max(0f,Math.min(1f,(rms-.025f)*2.75f));}
    private final Runnable vuTick=new Runnable(){public void run(){
        if(dead)return;
        try{
            if(vuMeter!=null&&vuMeter.getVisibility()==View.VISIBLE&&service!=null&&service.current!=null){
                if(service.playing()){
                    maybeRequestVuPermission();ensureVuVisualizer();
                    if(vuVisualizer!=null&&vuWave!=null&&vuVisualizer.getWaveForm(vuWave)==android.media.audiofx.Visualizer.SUCCESS){
                        long ls=0,rs=0;int lc=0,rc=0;
                        for(int i=0;i<vuWave.length;i++){int x=(vuWave[i]&255)-128;long q=(long)x*x;if((i&1)==0){ls+=q;lc++;}else{rs+=q;rc++;}}
                        vuMeter.setLevels(vuLevel(ls,lc),vuLevel(rs,rc));
                    }
                }
            }else{releaseVuVisualizer();if(vuMeter!=null)vuMeter.reset();}
        }catch(Throwable ignored){}
        handler.postDelayed(this,80);
    }};

'''
s=one(s,
'''    private void configureControls(boolean compact){
''',
insert+'''    private void configureControls(boolean compact){
''',
'vu capture methods')

s=one(s,
'''        handler.post(tick);
''',
'''        handler.post(tick);handler.post(vuTick);
''',
'start vu updates')

s=one(s,
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;title.setText(has?lower(service.current.name()):"ничего не играет");artist.setText(has?lower(service.current.artist):"");
''',
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;title.setText(has?lower(service.current.name()):"ничего не играет");artist.setText(has?lower(service.current.artist):"");
        if(vuMeter!=null){vuMeter.setVisibility(has&&!compactControls?View.VISIBLE:View.GONE);if(!has){vuMeter.reset();releaseVuVisualizer();}}
        if(has&&!compactControls&&service.playing())maybeRequestVuPermission();
''',
'update vu visibility and permission')

s=one(s,
'''    @Override protected void onDestroy(){stopRadio(false);dead=true;++authGeneration;++loadGeneration;handler.removeCallbacksAndMessages(null);worker.shutdownNow();if(service!=null&&service.listener==this)service.listener=null;if(bound)unbindService(connection);super.onDestroy();}
''',
'''    @Override protected void onDestroy(){stopRadio(false);dead=true;++authGeneration;++loadGeneration;releaseVuVisualizer();handler.removeCallbacksAndMessages(null);worker.shutdownNow();if(service!=null&&service.listener==this)service.listener=null;if(bound)unbindService(connection);super.onDestroy();}
''',
'release vu on destroy')

p.write_text(s)

# Expose only the active MediaPlayer's session id to the local activity for Visualizer attachment.
sp=Path('app/src/main/java/ru/classic/music/PlaybackService.java')
ss=sp.read_text()
ss=one(ss,
'''    int duration(){return ready&&player!=null?player.getDuration():0;}
''',
'''    int duration(){return ready&&player!=null?player.getDuration():0;}
    int audioSessionId(){try{return player==null?0:player.getAudioSessionId();}catch(Exception e){return 0;}}
''',
'audio session accessor')
sp.write_text(ss)

# Android Visualizer requires RECORD_AUDIO permission, even for a non-zero app-owned session.
mp=Path('app/src/main/AndroidManifest.xml')
ms=mp.read_text()
if 'android.permission.RECORD_AUDIO' not in ms:
    ms,n=re.subn(r'(<manifest[^>]*>)',r'\\1\n    <uses-permission android:name="android.permission.RECORD_AUDIO"/>',ms,count=1)
    if n!=1: raise SystemExit('manifest root not found')
mp.write_text(ms)
