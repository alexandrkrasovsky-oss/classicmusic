from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Replace the Unicode power glyph (missing in some Android fonts) with a real vector drawable.
s=one(s,
'''        TextView radioPower=text("⏻",21,activeTheme.muted);radioPower.setGravity(Gravity.CENTER);radioPower.setTypeface(uiFontStrong());radioPower.setContentDescription("Включить или остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(5),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'''        ImageView radioPower=new ImageView(this);radioPower.setImageResource(R.drawable.ic_radio_power);radioPower.setScaleType(ImageView.ScaleType.CENTER);radioPower.setPadding(dp(9),dp(9),dp(9),dp(9));radioPower.setContentDescription("Включить или остановить радио");
        FrameLayout.LayoutParams powerLp=new FrameLayout.LayoutParams(dp(40),dp(40),Gravity.END|Gravity.CENTER_VERTICAL);powerLp.setMargins(0,0,dp(5),0);radioCard.addView(radioPower,powerLp);radioCard.setTag(radioPower);
''',
'vector power control')

s=one(s,
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof TextView){TextView power=(TextView)powerTag;power.setTextColor(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f));power.setAlpha(on?1f:.72f);power.setBackground(shape(mixColor(activeTheme.paper,on?activeTheme.accent:activeTheme.line,on?.08f:.18f),on?activeTheme.accent:activeTheme.line,12));power.setContentDescription(on?"Остановить радио":"Включить радио");}}
''',
'''        if(cardTag instanceof FrameLayout){Object powerTag=((FrameLayout)cardTag).getTag();if(powerTag instanceof ImageView){ImageView power=(ImageView)powerTag;power.setColorFilter(on?activeTheme.accent:mixColor(activeTheme.ink,activeTheme.muted,.42f),android.graphics.PorterDuff.Mode.SRC_IN);power.setAlpha(on?1f:.72f);power.setBackground(shape(mixColor(activeTheme.paper,on?activeTheme.accent:activeTheme.line,on?.08f:.18f),on?activeTheme.accent:activeTheme.line,12));power.setContentDescription(on?"Остановить радио":"Включить радио");}}
''',
'vector power tint')

p.write_text(s)
