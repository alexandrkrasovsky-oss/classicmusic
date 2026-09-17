from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Drop Android Visualizer state. The deck meters are now permissionless UI meters driven by
# actual playback state (Yandex player or radio), so the app never asks for capture access.
s=one(s,
'''    private VuMeterView vuMeter;
    private android.media.audiofx.Visualizer vuVisualizer;
    private byte[] vuWave;
    private int vuSession=-1;
    private boolean compactControls=false;
''',
'''    private VuMeterView vuMeter;
    private boolean compactControls=false;
''',
'permissionless vu fields')

old_methods='''    private boolean hasVuPermission(){return Build.VERSION.SDK_INT<23||checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)==android.content.pm.PackageManager.PERMISSION_GRANTED;}
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
new_methods='''    private boolean vuAudioActive(){
        boolean music=service!=null&&service.current!=null&&service.playing();
        boolean radio=radioState==2&&radioPlayer!=null;
        if(radio){try{radio=radioPlayer.isPlaying();}catch(Throwable e){radio=false;}}
        return music||radio;
    }
    private float vuSyntheticLevel(long now,int channel){
        int seed=radioState==2?radioIndex+37:17;
        if(service!=null&&service.current!=null){try{seed=31*seed+service.current.name().hashCode();}catch(Throwable ignored){}}
        double t=now/1000.0;
        double phase=seed*.013+channel*.83;
        double a=Math.sin(t*5.7+phase);
        double b=Math.sin(t*8.9+phase*1.7);
        double c=Math.sin(t*3.1+phase*2.4);
        double d=Math.sin(t*13.7+phase*.6);
        double v=.48+.19*a+.13*b+.10*c+.07*d;
        if(channel==1)v+=.035*Math.sin(t*2.3+phase);
        return (float)Math.max(.08,Math.min(.98,v));
    }
    private final Runnable vuTick=new Runnable(){public void run(){
        if(dead)return;
        try{
            if(vuMeter!=null){
                boolean active=vuAudioActive()&&!compactControls;
                vuMeter.setVisibility(active?View.VISIBLE:View.GONE);
                if(active){long now=android.os.SystemClock.uptimeMillis();vuMeter.setLevels(vuSyntheticLevel(now,0),vuSyntheticLevel(now,1));}
                else vuMeter.reset();
            }
        }catch(Throwable ignored){}
        handler.postDelayed(this,80);
    }};

'''
s=one(s,old_methods,new_methods,'permissionless active-state vu engine')

# Full-player visibility follows actual audio output, including radio; pause/stop extinguishes immediately.
s=one(s,
'''            if(vuMeter!=null)vuMeter.setVisibility(service!=null&&service.current!=null?View.VISIBLE:View.GONE);
''',
'''            if(vuMeter!=null)vuMeter.setVisibility(vuAudioActive()?View.VISIBLE:View.GONE);
''',
'full player vu visibility')

s=one(s,
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;title.setText(has?lower(service.current.name()):"ничего не играет");artist.setText(has?lower(service.current.artist):"");
        if(vuMeter!=null){vuMeter.setVisibility(has&&!compactControls?View.VISIBLE:View.GONE);if(!has){vuMeter.reset();releaseVuVisualizer();}}
        if(has&&!compactControls&&service.playing())maybeRequestVuPermission();
''',
'''        if(dead||play==null)return;boolean has=service!=null&&service.current!=null;title.setText(has?lower(service.current.name()):"ничего не играет");artist.setText(has?lower(service.current.artist):"");
        if(vuMeter!=null){boolean active=vuAudioActive()&&!compactControls;vuMeter.setVisibility(active?View.VISIBLE:View.GONE);if(!active)vuMeter.reset();}
''',
'pause stop radio vu state')

s=one(s,
'''    @Override protected void onDestroy(){stopRadio(false);dead=true;++authGeneration;++loadGeneration;releaseVuVisualizer();handler.removeCallbacksAndMessages(null);worker.shutdownNow();if(service!=null&&service.listener==this)service.listener=null;if(bound)unbindService(connection);super.onDestroy();}
''',
'''    @Override protected void onDestroy(){stopRadio(false);dead=true;++authGeneration;++loadGeneration;handler.removeCallbacksAndMessages(null);worker.shutdownNow();if(service!=null&&service.listener==this)service.listener=null;if(bound)unbindService(connection);super.onDestroy();}
''',
'no visualizer teardown')

p.write_text(s)
