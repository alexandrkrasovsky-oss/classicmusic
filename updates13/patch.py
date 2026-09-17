from pathlib import Path

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

def one(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

# Remove the "сейчас играет" eyebrow and vertically balance title/artist beside artwork.
one('''now=row();cover=new ImageView(this);cover.setScaleType(ImageView.ScaleType.CENTER_CROP);cover.setBackground(shape(mixColor(activeTheme.paper,activeTheme.accent,.10f),0,13));cover.setClipToOutline(true);cover.setImageResource(ru.classic.music.R.drawable.ic_music);cover.setPadding(dp(26),dp(26),dp(26),dp(26));now.addView(cover,new LinearLayout.LayoutParams(dp(96),dp(96)));''','''now=row();now.setGravity(Gravity.CENTER_VERTICAL);cover=new ImageView(this);cover.setScaleType(ImageView.ScaleType.CENTER_CROP);cover.setBackground(shape(mixColor(activeTheme.paper,activeTheme.accent,.10f),0,13));cover.setClipToOutline(true);cover.setImageResource(ru.classic.music.R.drawable.ic_music);cover.setPadding(dp(26),dp(26),dp(26),dp(26));now.addView(cover,new LinearLayout.LayoutParams(dp(96),dp(96)));''','center now-playing row')
one('''copy=column();copy.setPadding(dp(12),0,0,0);eyebrow=text("сейчас играет",12,activeTheme.accent);eyebrow.setTypeface(uiFontStrong());eyebrow.setLetterSpacing(0f);copy.addView(eyebrow);''','''copy=column();copy.setPadding(dp(12),0,0,0);eyebrow=text("",12,activeTheme.accent);eyebrow.setVisibility(View.GONE);''','remove now-playing eyebrow')
one('''title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);title.setPadding(0,dp(10),0,0);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);copy.addView(artist);''','''title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);title.setPadding(0,0,0,0);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);artist.setAlpha(.72f);copy.addView(artist);''','simplify now-playing text')

# Soften secondary information without reducing legibility.
one('''time=text("0:00 / 0:00",12,activeTheme.muted);time.setGravity(Gravity.CENTER);''','''time=text("0:00 / 0:00",12,activeTheme.muted);time.setGravity(Gravity.CENTER);time.setAlpha(.72f);''','soften time')
one('''status=text("",12,activeTheme.muted);status.setGravity(Gravity.CENTER);status.setMaxLines(2);''','''status=text("",12,activeTheme.muted);status.setGravity(Gravity.CENTER);status.setMaxLines(2);status.setAlpha(.72f);''','soften status')

# Keep the eyebrow hidden in both player modes and remove the old title top padding.
one('''cover.setVisibility(View.GONE);\n            eyebrow.setVisibility(View.GONE);''','''cover.setVisibility(View.GONE);\n            eyebrow.setVisibility(View.GONE);''','compact eyebrow stays hidden')
one('''cover.setVisibility(View.VISIBLE);\n            eyebrow.setVisibility(View.VISIBLE);''','''cover.setVisibility(View.VISIBLE);\n            eyebrow.setVisibility(View.GONE);''','normal eyebrow hidden')
one('''title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);title.setPadding(0,dp(10),0,0);''','''title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);title.setPadding(0,0,0,0);''','normal title padding')

# Unify the large page buttons at 50dp, matching the top brand and radio control.
s=s.replace('new LinearLayout.LayoutParams(-1,dp(48))','new LinearLayout.LayoutParams(-1,dp(50))')

p.write_text(s)
