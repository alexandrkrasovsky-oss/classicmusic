from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# The radio card itself starts radio when stopped; while active, each tap advances to the next station.
s=one(s,
'''        radioButton=button("",this::tuneNextRadio);
''',
'''        radioButton=button("",this::radioCardTap);
''',
'radio card tap behavior')

# Use a bare vector glyph with a 40dp invisible touch target. The glyph's visual right edge
# follows the radio card's right edge, matching the right edge of the player's right-hand controls.
s=one(s,
'''        ImageView radioPower=new ImageView(this);radioPower.setImageResource(R.drawable.ic_radio_power);radioPower.setScaleType(ImageView.ScaleType.CENTER);radioPower.setPadding(dp(9),dp(9),dp(9),dp(9));radioPower.setContentDescription("Включить или остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.START|Gravity.CENTER_VERTICAL);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
        radioCard.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{int w=r-l;if(w>0)radioPower.setX(w*5f/6f-dp(20));});
''',
'''        ImageView radioPower=new ImageView(this);radioPower.setImageResource(R.drawable.ic_radio_power);radioPower.setScaleType(ImageView.ScaleType.FIT_END);radioPower.setPadding(dp(18),dp(10),0,dp(10));radioPower.setContentDescription("Остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'bare aligned power icon')

# Power is stop-only. The main card is the only way to start radio.
s=one(s,
'''        radioPower.setOnClickListener(v->{v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);toggleRadio();});
        final float[] radioTouchX={0f};
        radioButton.setOnTouchListener((v,e)->{
            if(e.getActionMasked()==MotionEvent.ACTION_DOWN){radioTouchX[0]=e.getX();return false;}
            if(e.getActionMasked()==MotionEvent.ACTION_UP){float dx=e.getX()-radioTouchX[0];if(Math.abs(dx)>=dp(36)){v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);if(dx>0)tunePreviousRadio();else tuneNextRadio();return true;}}
            return false;
        });
''',
'''        radioPower.setOnClickListener(v->{if(radioPlayer!=null){v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);stopRadio(false);}});
''',
'remove swipe and make power stop-only')

# Straightforward tap behavior: first tap starts the selected/default station; later taps retune forward.
s=one(s,
'''    private void tuneNextRadio(){stepRadio(1);}
    private void tunePreviousRadio(){stepRadio(-1);}
    private void stepRadio(int direction){
        if(radioNames.length==0)return;
        final boolean wasOn=radioPlayer!=null;
        int current=radioIndex<0?0:radioIndex;
        final int next=(current+direction+radioNames.length)%radioNames.length;
        if(radioButton==null){radioIndex=next;if(wasOn)tuneRadio(next);return;}
        radioButton.animate().cancel();
        float exit=direction>0?-dp(8):dp(8);
        radioButton.animate().alpha(.48f).translationX(exit).setDuration(70).withEndAction(()->{
            radioIndex=next;
            if(wasOn)tuneRadio(next);else updateRadioUi();
            radioButton.setTranslationX(direction>0?dp(8):-dp(8));
            radioButton.animate().alpha(1f).translationX(0f).setDuration(95).start();
        }).start();
    }
    private void toggleRadio(){
        if(radioPlayer!=null){stopRadio(false);return;}
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        tuneRadio(radioIndex);
    }
''',
'''    private void radioCardTap(){
        if(radioNames.length==0)return;
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        if(radioPlayer==null)tuneRadio(radioIndex);else tuneNextRadio();
    }
    private void tuneNextRadio(){stepRadio(1);}
    private void tunePreviousRadio(){stepRadio(-1);}
    private void stepRadio(int direction){
        if(radioNames.length==0)return;
        int current=radioIndex<0?0:radioIndex;
        int next=(current+direction+radioNames.length)%radioNames.length;
        radioIndex=next;
        if(radioPlayer!=null)tuneRadio(next);else updateRadioUi();
    }
    private void toggleRadio(){if(radioPlayer!=null)stopRadio(false);}
''',
'tap-to-start then tap-to-cycle')

# No framed button: while radio is loading/playing, show the stop icon; while stopped, hide it.
s=one(s,
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;power.setColorFilter(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f),android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(on?1f:.72f);power.setBackground(shape(mixColor(activeTheme.paper,on?activeTheme.accent:activeTheme.line,on?.08f:.18f),on?activeTheme.accent:activeTheme.line,12));power.setContentDescription(on?"Остановить радио":"Включить радио");}}
''',
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;power.setColorFilter(activeTheme.accent,android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(1f);power.setBackground(null);power.setVisibility(on?View.VISIBLE:View.INVISIBLE);power.setEnabled(on);power.setContentDescription("Остановить радио");}}
''',
'frameless stop-only power styling')

# Explain network wait explicitly while a station stream is preparing.
s=one(s,
'''        radioIndex=index;
        updateRadioUi();
''',
'''        radioIndex=index;
        updateRadioUi();
        if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · загрузка…");
''',
'loading label')

# Preserve a visible error state instead of looking like a silent hang.
s=one(s,
'''            p.setOnErrorListener((mp,what,extra)->{
                if(mp==radioPlayer)radioPlayer=null;
                if(ticket==radioGeneration)updateRadioUi();
                try{mp.release();}catch(Exception ignored){}
                return true;
            });
''',
'''            p.setOnErrorListener((mp,what,extra)->{
                if(mp==radioPlayer)radioPlayer=null;
                if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
                try{mp.release();}catch(Exception ignored){}
                return true;
            });
''',
'radio error label')

s=one(s,
'''        }catch(Exception e){
            if(p==radioPlayer)radioPlayer=null;
            if(ticket==radioGeneration)updateRadioUi();
            try{p.release();}catch(Exception ignored){}
        }
''',
'''        }catch(Exception e){
            if(p==radioPlayer)radioPlayer=null;
            if(ticket==radioGeneration){updateRadioUi();if(radioButton!=null)radioButton.setText(radioNames[index].toLowerCase(Locale.ROOT)+" · не удалось");}
            try{p.release();}catch(Exception ignored){}
        }
''',
'radio catch error label')

# Accessibility text reflects the actual interaction model.
s=one(s,
'''        radioButton.setContentDescription("Радио: "+radioNames[radioIndex]+". Нажми для следующей станции или свайпни вправо-влево");
''',
'''        radioButton.setContentDescription(on?"Радио: "+radioNames[radioIndex]+". Нажми для следующей станции":"Радио: "+radioNames[radioIndex]+". Нажми, чтобы включить");
''',
'radio accessibility text')

p.write_text(s)
