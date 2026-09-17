from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Rebuild radio as one centered card with a small power control layered at the right edge.
s=one(s,
'''        radioButton=button("поймать радиоволну",this::tuneNextRadio);
        radioButton.setTextSize(16);
        radioButton.setTypeface(uiFontStrong());
        radioButton.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams radioLp=new LinearLayout.LayoutParams(-1,dp(50));
        radioLp.setMargins(dp(4),dp(2),dp(4),dp(4));
        // radioButton is attached next to the main player by showPage()
''',
'''        radioButton=button("",this::tuneNextRadio);
        radioButton.setTextSize(16);
        radioButton.setTypeface(uiFontStrong());
        radioButton.setGravity(Gravity.CENTER);
        if(radioIndex<0)radioIndex=0;
        FrameLayout radioCard=new FrameLayout(this);
        radioButton.setTag(radioCard);
        radioCard.addView(radioButton,new FrameLayout.LayoutParams(-1,-1));
        TextView radioPower=text("⏻",21,activeTheme.muted);radioPower.setGravity(Gravity.CENTER);radioPower.setTypeface(uiFontStrong());radioPower.setContentDescription("Включить или остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(5),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
        radioPower.setOnClickListener(v->{v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);toggleRadio();});
        final float[] radioTouchX={0f};
        radioButton.setOnTouchListener((v,e)->{
            if(e.getActionMasked()==MotionEvent.ACTION_DOWN){radioTouchX[0]=e.getX();return false;}
            if(e.getActionMasked()==MotionEvent.ACTION_UP){float dx=e.getX()-radioTouchX[0];if(Math.abs(dx)>=dp(36)){v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);if(dx>0)tunePreviousRadio();else tuneNextRadio();return true;}}
            return false;
        });
        updateRadioUi();
        LinearLayout.LayoutParams radioLp=new LinearLayout.LayoutParams(-1,dp(50));
        radioLp.setMargins(dp(4),dp(2),dp(4),dp(4));
        // radio card is attached next to the main player by showPage()
''',
'radio card with power')

# Keep the card together while switching pages.
s=one(s,
'''        detach(controls);detach(status);detach(radioButton);
''',
'''        detach(controls);detach(status);View radioCard=radioButton==null?null:(View)radioButton.getTag();detach(radioCard);
''',
'detach radio card')

s=one(s,
'''            radioButton.setVisibility(View.VISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);body.addView(radioButton,rp);
''',
'''            radioButton.setVisibility(View.VISIBLE);View radioCardView=(View)radioButton.getTag();radioCardView.setVisibility(View.VISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);body.addView(radioCardView,rp);
''',
'attach radio card')

# Stop no longer forgets the selected station. The power icon simply turns off.
s=one(s,
'''        if(resetLabel&&radioButton!=null){
            radioIndex=-1;
            radioButton.setText("поймать радиоволну");
        }
''',
'''        if(radioButton!=null)updateRadioUi();
''',
'preserve radio station on stop')

# Tapping the card or swiping chooses stations. If radio is already playing, selection retunes immediately.
s=one(s,
'''    private void tuneNextRadio(){
        int next=(radioIndex+1)%radioNames.length;
        tuneRadio(next);
    }
''',
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
    private void updateRadioUi(){
        if(radioButton==null||radioNames.length==0)return;
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        boolean on=radioPlayer!=null;
        radioButton.setText(radioNames[radioIndex].toLowerCase(Locale.ROOT));
        radioButton.setTextColor(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f));
        radioButton.setContentDescription("Радио: "+radioNames[radioIndex]+". Нажми для следующей станции или свайпни вправо-влево");
        Object cardTag=radioButton.getTag();
        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof TextView){TextView power=(TextView)powerTag;power.setTextColor(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f));power.setAlpha(on?1f:.72f);power.setBackground(shape(mixColor(activeTheme.paper,on?activeTheme.accent:activeTheme.line,on?.08f:.18f),on?activeTheme.accent:activeTheme.line,12));power.setContentDescription(on?"Остановить радио":"Включить радио");}}
    }
''',
'radio selection and power toggle')

# Radio label remains the station name while loading/playing; power tint indicates on/off.
s=one(s,
'''        radioIndex=index;
        if(radioButton!=null)radioButton.setText("ловлю: "+radioNames[index].toLowerCase(Locale.ROOT)+"…");
''',
'''        radioIndex=index;
        updateRadioUi();
''',
'clean radio loading label')

s=one(s,
'''                if(radioButton!=null)radioButton.setText("играет: "+radioNames[index].toLowerCase(Locale.ROOT));
''',
'''                updateRadioUi();
''',
'clean radio playing label')

s=one(s,
'''            p.setOnErrorListener((mp,what,extra)->{
                if(ticket==radioGeneration&&radioButton!=null)radioButton.setText("не поймал: "+radioNames[index].toLowerCase(Locale.ROOT)+" · нажми ещё");
                if(mp==radioPlayer)radioPlayer=null;
                try{mp.release();}catch(Exception ignored){}
                return true;
            });
''',
'''            p.setOnErrorListener((mp,what,extra)->{
                if(mp==radioPlayer)radioPlayer=null;
                if(ticket==radioGeneration)updateRadioUi();
                try{mp.release();}catch(Exception ignored){}
                return true;
            });
''',
'radio error state')

s=one(s,
'''        }catch(Exception e){
            if(ticket==radioGeneration&&radioButton!=null)radioButton.setText("не поймал: "+radioNames[index].toLowerCase(Locale.ROOT)+" · нажми ещё");
            if(p==radioPlayer)radioPlayer=null;
            try{p.release();}catch(Exception ignored){}
        }
''',
'''        }catch(Exception e){
            if(p==radioPlayer)radioPlayer=null;
            if(ticket==radioGeneration)updateRadioUi();
            try{p.release();}catch(Exception ignored){}
        }
''',
'radio catch state')

# Theme changes also refresh the selected-station and power styling.
s=one(s,
'''        if(adapter!=null)adapter.notifyDataSetChanged();
    }
''',
'''        if(adapter!=null)adapter.notifyDataSetChanged();
        updateRadioUi();
    }
''',
'radio theme refresh')

p.write_text(s)
