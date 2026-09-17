from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Keep a permanent 40dp touch target, but inset the visual icon to the same right edge
# as the player's right-hand controls (12dp inside the card).
s=one(s,
'''        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'''        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(12),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'align power to player right edge')

# Power is now a true toggle: always present, starts the selected/default station when off,
# and stops radio when on. The center of the radio card keeps its start-then-cycle behavior.
s=one(s,
'''        radioPower.setOnClickListener(v->{if(radioPlayer!=null){v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);stopRadio(false);}});
''',
'''        radioPower.setOnClickListener(v->{v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);toggleRadio();});
''',
'toggle power click')

s=one(s,
'''    private void toggleRadio(){if(radioPlayer!=null)stopRadio(false);}
''',
'''    private void toggleRadio(){
        if(radioPlayer!=null){stopRadio(false);return;}
        if(radioNames.length==0)return;
        if(radioIndex<0||radioIndex>=radioNames.length)radioIndex=0;
        tuneRadio(radioIndex);
    }
''',
'power starts and stops radio')

# Persistent state indicator: soft green with a faint halo while loading/playing,
# calm red while stopped. No border or framed button.
s=one(s,
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;power.setColorFilter(activeTheme.accent,android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(1f);power.setBackground(null);power.setVisibility(on?View.VISIBLE:View.INVISIBLE);power.setEnabled(on);power.setContentDescription("Остановить радио");}}
''',
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;int powerColor=on?0xff5F9669:0xffB95E55;power.setColorFilter(powerColor,android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(on?1f:.90f);power.setBackground(on?shape(0x185F9669,0x005F9669,20):null);power.setVisibility(View.VISIBLE);power.setEnabled(true);power.setContentDescription(on?"Остановить радио":"Включить радио");}}
''',
'persistent red green power state')

p.write_text(s)
