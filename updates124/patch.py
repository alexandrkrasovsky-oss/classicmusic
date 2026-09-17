from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Track three explicit radio states: off, loading, playing.
s=one(s,
'''    private int radioIndex=-1,radioGeneration=0;
''',
'''    private int radioIndex=-1,radioGeneration=0,radioState=0;
''',
'radio state field')

# Keep a generous invisible touch target, but make the actual glyph small. With a 44dp slot,
# 8dp outer margin and 4dp right padding, the glyph itself ends exactly 12dp inside the radio card,
# matching the right edge of the player's right-hand controls.
s=one(s,
'''        ImageView radioPower=new ImageView(this);radioPower.setImageResource(R.drawable.ic_radio_power);radioPower.setScaleType(ImageView.ScaleType.FIT_END);radioPower.setPadding(dp(18),dp(10),0,dp(10));radioPower.setContentDescription("Остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(12),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'''        ImageView radioPower=new ImageView(this);radioPower.setImageResource(R.drawable.ic_radio_power);radioPower.setScaleType(ImageView.ScaleType.FIT_END);radioPower.setPadding(dp(16),dp(12),dp(4),dp(12));radioPower.setContentDescription("Включить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(44),dp(44),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(8),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'smaller aligned lamp glyph')

# Releasing a radio player always returns the lamp state to off.
s=one(s,
'''        MediaPlayer p=radioPlayer;
        radioPlayer=null;
        if(p==null)return;
''',
'''        MediaPlayer p=radioPlayer;
        radioPlayer=null;
        radioState=0;
        if(p==null)return;
''',
'reset radio state on release')

# Replace the hard circular background with a soft radial halo around the glyph.
# Red = off, amber = connecting, green = playing.
s=one(s,
'''    private void updateRadioUi(){
        if(radioButton==null||radioNames.length==0)return;
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        boolean on=radioPlayer!=null;
        radioButton.setText(radioNames[radioIndex].toLowerCase(Locale.ROOT));
        radioButton.setTextColor(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f));
        radioButton.setContentDescription(on?"Радио: "+radioNames[radioIndex]+". Нажми для следующей станции":"Радио: "+radioNames[radioIndex]+". Нажми, чтобы включить");
        Object cardTag=radioButton.getTag();
        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;int powerColor=on?0xff5F9669:0xffB95E55;power.setColorFilter(powerColor,android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(on?1f:.90f);power.setBackground(on?shape(0x185F9669,0x005F9669,20):null);power.setVisibility(View.VISIBLE);power.setEnabled(true);power.setContentDescription(on?"Остановить радио":"Включить радио");}}
    }
''',
'''    private android.graphics.drawable.GradientDrawable radioGlow(int color){
        android.graphics.drawable.GradientDrawable glow=new android.graphics.drawable.GradientDrawable();
        glow.setShape(android.graphics.drawable.GradientDrawable.RECTANGLE);
        glow.setGradientType(android.graphics.drawable.GradientDrawable.RADIAL_GRADIENT);
        glow.setGradientCenter(.68f,.50f);
        int core=(color&0x00ffffff)|0x38000000;
        int mid=(color&0x00ffffff)|0x18000000;
        glow.setColors(new int[]{core,mid,0x00000000});
        glow.setGradientRadius(dp(16));
        return glow;
    }
    private void setRadioPowerState(int state){
        if(radioButton==null)return;
        Object cardTag=radioButton.getTag();
        if(!(cardTag instanceof FrameLayout))return;
        Object powerTag=((FrameLayout)cardTag).getTag();
        if(!(powerTag instanceof ImageView))return;
        ImageView power=(ImageView)powerTag;
        int color=state==2?0xff55936A:(state==1?0xffC38A3D:0xffB95E55);
        power.setColorFilter(color,android.graphics.PorterDuff.Mode.SRC_IN);
        power.setAlpha(state==0?.86f:1f);
        power.setBackground(radioGlow(color));
        power.setVisibility(View.VISIBLE);
        power.setEnabled(true);
        power.setContentDescription(state==0?"Включить радио":(state==1?"Остановить загрузку радио":"Остановить радио"));
    }
    private void updateRadioUi(){
        if(radioButton==null||radioNames.length==0)return;
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        String station=radioNames[radioIndex].toLowerCase(Locale.ROOT);
        if(radioState==1)radioButton.setText(station+" · загрузка…");else radioButton.setText(station);
        radioButton.setTextColor(radioState==2?activeTheme.accent:(radioState==1?0xffB77B31:mixColor(activeTheme.ink,activeTheme.muted,.42f)));
        radioButton.setContentDescription(radioState==0?"Радио: "+radioNames[radioIndex]+". Нажми, чтобы включить":(radioState==1?"Радио: "+radioNames[radioIndex]+". Загрузка потока":"Радио: "+radioNames[radioIndex]+". Нажми для следующей станции"));
        setRadioPowerState(radioState);
    }
''',
'lamp radio power states')

# Enter loading state before updating the UI, so the lamp turns amber immediately.
s=one(s,
'''        radioIndex=index;
        updateRadioUi();
        if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · загрузка…");
        final MediaPlayer p=new MediaPlayer();
        radioPlayer=p;
''',
'''        radioIndex=index;
        final MediaPlayer p=new MediaPlayer();
        radioPlayer=p;
        radioState=1;
        updateRadioUi();
''',
'loading state before prepare')

# Prepared stream turns the lamp green.
s=one(s,
'''                try{mp.start();}catch(Exception e){return;}
                updateRadioUi();
''',
'''                try{mp.start();}catch(Exception e){if(mp==radioPlayer){radioPlayer=null;radioState=0;}updateRadioUi();try{mp.release();}catch(Exception ignored){}return;}
                radioState=2;
                updateRadioUi();
''',
'playing state after prepare')

# Errors and synchronous failures return the lamp to red.
s=one(s,
'''                if(mp==radioPlayer)radioPlayer=null;
                if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
''',
'''                if(mp==radioPlayer){radioPlayer=null;radioState=0;}
                if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
''',
'error returns red')

s=one(s,
'''            if(p==radioPlayer)radioPlayer=null;
            if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
''',
'''            if(p==radioPlayer){radioPlayer=null;radioState=0;}
            if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
''',
'catch returns red')

p.write_text(s)
