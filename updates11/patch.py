from pathlib import Path

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

def one(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

# Keep explicit controllable vertical gaps around the top navigation.
one('private View divider,controlsGap;','private View divider,controlsGap,brandGap,tabsGap;','gap fields')
one('''        LinearLayout.LayoutParams brandParams=new LinearLayout.LayoutParams(-1,dp(50));brandParams.setMargins(dp(4),0,dp(4),0);mainContent.addView(brand,brandParams);setupThemeSwipe();addGap(mainContent);''','''        LinearLayout.LayoutParams brandParams=new LinearLayout.LayoutParams(-1,dp(50));brandParams.setMargins(dp(4),0,dp(4),0);mainContent.addView(brand,brandParams);setupThemeSwipe();brandGap=new Space(this);mainContent.addView(brandGap,new LinearLayout.LayoutParams(1,dp(GAP)));''','brand gap')
one('''        tabs=row();waveTab=button("моя волна",()->showPage(false));favoritesTab=button("любимые",()->showPage(true));addWeighted(tabs,waveTab);addWeighted(tabs,favoritesTab);mainContent.addView(tabs);addGap(mainContent);\n        divider=new View(this);divider.setBackgroundColor(activeTheme.line);mainContent.addView(divider,new LinearLayout.LayoutParams(-1,dp(1)));addGap(mainContent);''','''        tabs=row();waveTab=button("моя волна",()->showPage(false));favoritesTab=button("любимые",()->showPage(true));addWeighted(tabs,waveTab);addWeighted(tabs,favoritesTab);mainContent.addView(tabs);tabsGap=new Space(this);mainContent.addView(tabsGap,new LinearLayout.LayoutParams(1,dp(GAP)));\n        divider=new View(this);divider.setVisibility(View.GONE);mainContent.addView(divider,new LinearLayout.LayoutParams(-1,0));''','remove divider and control tabs gap')
one('''        tabs.setVisibility(favoritesPage?View.GONE:View.VISIBLE);\n        body.removeAllViews();list=null;more=null;''','''        tabs.setVisibility(favoritesPage?View.GONE:View.VISIBLE);\n        tabsGap.setVisibility(favoritesPage?View.GONE:View.VISIBLE);\n        LinearLayout.LayoutParams bgp=(LinearLayout.LayoutParams)brandGap.getLayoutParams();bgp.height=dp(favoritesPage?6:GAP);brandGap.setLayoutParams(bgp);\n        body.removeAllViews();list=null;more=null;''','page gap visibility')

# Main player: equal visual rhythm around progress/time/transport.
one('''        seek=new SeekBar(this);seek.setMax(1000);LinearLayout.LayoutParams seekParams=new LinearLayout.LayoutParams(-1,dp(32));seekParams.topMargin=dp(6);controls.addView(seek,seekParams);''','''        seek=new SeekBar(this);seek.setMax(1000);LinearLayout.LayoutParams seekParams=new LinearLayout.LayoutParams(-1,dp(32));seekParams.topMargin=dp(8);controls.addView(seek,seekParams);''','seek top gap')
one('''        time=text("0:00 / 0:00",12,activeTheme.muted);time.setGravity(Gravity.CENTER);LinearLayout.LayoutParams timeParams=new LinearLayout.LayoutParams(-1,dp(24));controls.addView(time,timeParams);''','''        time=text("0:00 / 0:00",12,activeTheme.muted);time.setGravity(Gravity.CENTER);LinearLayout.LayoutParams timeParams=new LinearLayout.LayoutParams(-1,dp(20));timeParams.setMargins(0,dp(8),0,dp(8));controls.addView(time,timeParams);''','time symmetric gaps')

# Keep "сейчас играет" aligned with the cover top, move title/artist block down into a balanced center.
one('''        title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);copy.addView(artist);now.addView(copy,new LinearLayout.LayoutParams(0,-2,1));controls.addView(now);''','''        title=text("ничего не играет",19,activeTheme.ink);title.setTypeface(uiFontStrong());title.setMaxLines(2);title.setPadding(0,dp(10),0,0);copy.addView(title);artist=text("",14,activeTheme.muted);artist.setMaxLines(2);copy.addView(artist);now.addView(copy,new LinearLayout.LayoutParams(0,-2,1));controls.addView(now);''','main title spacing')
one('''            title.setTextSize(15);title.setMaxLines(1);title.setGravity(Gravity.CENTER);''','''            title.setTextSize(15);title.setMaxLines(1);title.setGravity(Gravity.CENTER);title.setPadding(0,0,0,0);''','compact title padding')
one('''            title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);''','''            title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);title.setPadding(0,dp(10),0,0);''','main title padding restore')

p.write_text(s)
