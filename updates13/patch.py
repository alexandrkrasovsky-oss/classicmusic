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
one('''cover.setVisibility(View.VISIBLE);\n            eyebrow.setVisibility(View.VISIBLE);''','''cover.setVisibility(View.VISIBLE);\n            eyebrow.setVisibility(View.GONE);''','normal eyebrow hidden')
one('''title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);title.setPadding(0,dp(10),0,0);''','''title.setTextSize(19);title.setMaxLines(2);title.setGravity(Gravity.START);title.setPadding(0,0,0,0);''','normal title padding')

# Unify the large page buttons at 50dp, matching the top brand and radio control.
s=s.replace('new LinearLayout.LayoutParams(-1,dp(48))','new LinearLayout.LayoutParams(-1,dp(50))')

# Make cold-start Play explicit instead of relying on toggle/resume indirection.
one('''play=primaryButton("▶  играть",()->{if(service!=null){if(service.current==null)stopRadio(true);service.toggle();}});''','''play=primaryButton("▶  играть",()->{if(service!=null){if(service.current==null){stopRadio(true);service.startWave();}else service.toggle();}});''','explicit cold-start play')

# The service knows how to start My Wave from a cold start; keep Play and Shuffle clickable once bound.
one('''play.setText(service!=null&&service.playing()?"Ⅱ  пауза":"▶  играть");play.setEnabled(has);like.setEnabled(has);seek.setEnabled(has&&service.duration()>0);boolean likedNow=service!=null&&service.isLiked();''','''play.setText(service!=null&&service.playing()?"Ⅱ  пауза":"▶  играть");play.setEnabled(service!=null&&loggedIn);like.setEnabled(has);seek.setEnabled(has&&service.duration()>0);boolean likedNow=service!=null&&service.isLiked();''','enable play cold start')
one('''shuffle.setSelected(service!=null&&service.isShuffle());shuffle.setEnabled(has);shuffle.setText("вразброс");repeat.setSelected(service!=null&&service.isRepeat());repeat.setText("повтор");''','''shuffle.setSelected(service!=null&&service.isShuffle());shuffle.setEnabled(service!=null&&loggedIn);shuffle.setText("вразброс");repeat.setSelected(service!=null&&service.isRepeat());repeat.setText("повтор");''','enable shuffle cold start')

# One consistent vertical rhythm for all major blocks on both pages: 8dp.
one('''LinearLayout.LayoutParams bgp=(LinearLayout.LayoutParams)brandGap.getLayoutParams();bgp.height=dp(favoritesPage?6:GAP);brandGap.setLayoutParams(bgp);''','''LinearLayout.LayoutParams bgp=(LinearLayout.LayoutParams)brandGap.getLayoutParams();bgp.height=dp(8);brandGap.setLayoutParams(bgp);''','brand gap')
one('''tabsGap=new Space(this);mainContent.addView(tabsGap,new LinearLayout.LayoutParams(1,dp(GAP)));''','''tabsGap=new Space(this);mainContent.addView(tabsGap,new LinearLayout.LayoutParams(1,dp(8)));''','tabs gap')
one('''Space g=new Space(this);body.addView(g,new LinearLayout.LayoutParams(1,dp(GAP)));''','''Space g=new Space(this);body.addView(g,new LinearLayout.LayoutParams(1,dp(8)));''','main button gap')
one('''LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(GAP),dp(4),0);mainContent.addView(controls,cp);''','''LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(8),dp(4),0);mainContent.addView(controls,cp);''','main player gap')
one('''LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(radioButton,rp);''','''LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(8),dp(4),0);mainContent.addView(radioButton,rp);''','radio gap')
one('''LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,dp(50));hp.setMargins(dp(4),0,dp(4),dp(4));body.addView(favoritesHeader,hp);''','''LinearLayout.LayoutParams hp=new LinearLayout.LayoutParams(-1,dp(50));hp.setMargins(dp(4),0,dp(4),dp(8));body.addView(favoritesHeader,hp);''','favorites header gap')
one('''list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});LinearLayout.LayoutParams listLp=new LinearLayout.LayoutParams(-1,0,1);listLp.setMargins(dp(4),dp(2),dp(4),dp(4));body.addView(list,listLp);''','''list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});LinearLayout.LayoutParams listLp=new LinearLayout.LayoutParams(-1,0,1);listLp.setMargins(dp(4),0,dp(4),dp(8));body.addView(list,listLp);''','favorites list gap')
one('''more=button("загрузить ещё",this::loadMore);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(-1,dp(50));mp.setMargins(dp(4),dp(4),dp(4),0);body.addView(more,mp);updateList();''','''more=button("загрузить ещё",this::loadMore);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(-1,dp(50));mp.setMargins(dp(4),0,dp(4),0);body.addView(more,mp);updateList();''','more top gap')
one('''LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(controls,cp);''','''LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(8),dp(4),0);mainContent.addView(controls,cp);''','favorites player gap')

p.write_text(s)
