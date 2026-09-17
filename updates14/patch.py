from pathlib import Path

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

def one(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

# One compact vertical rhythm everywhere.
one('private static final int GAP=10;','private static final int GAP=6;','global gap')
s=s.replace('dp(8)','dp(6)')
one('''LinearLayout.LayoutParams gp=(LinearLayout.LayoutParams)controlsGap.getLayoutParams();gp.height=dp(10);controlsGap.setLayoutParams(gp);''','''LinearLayout.LayoutParams gp=(LinearLayout.LayoutParams)controlsGap.getLayoutParams();gp.height=dp(6);controlsGap.setLayoutParams(gp);''','compact controls gap')
one('''LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(4);mainContent.addView(status,sp);''','''LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);mainContent.addView(status,sp);''','main status gap')
one('''LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(20));sp.topMargin=dp(2);mainContent.addView(status,sp);''','''LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(20));sp.topMargin=dp(6);mainContent.addView(status,sp);''','favorites status gap')

# Keep the top control at the same Y coordinate on both pages.
one('''LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=favoritesPage?0:-2;bp.weight=favoritesPage?1f:0f;body.setLayoutParams(bp);mainContent.setGravity(favoritesPage?Gravity.TOP:Gravity.CENTER_VERTICAL);''','''LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=favoritesPage?0:-2;bp.weight=favoritesPage?1f:0f;body.setLayoutParams(bp);mainContent.setGravity(Gravity.TOP);''','fixed top geometry')

# Short fade-out/fade-in hides the page reflow without adding heavy transitions.
one('''private void showPage(boolean favoritesPage){''','''private void switchPage(boolean target){
        if(target==favoritesPage||mainContent==null){if(target!=favoritesPage)showPage(target);return;}
        mainContent.animate().cancel();
        mainContent.animate().alpha(0f).setDuration(85).withEndAction(()->{
            if(dead)return;
            showPage(target);
            mainContent.setAlpha(0f);
            mainContent.animate().alpha(1f).setDuration(115).start();
        }).start();
    }
    private void showPage(boolean favoritesPage){''','page fade method')
one('''tabs=row();waveTab=button("моя волна",()->showPage(false));favoritesTab=button("любимые",()->showPage(true));''','''tabs=row();waveTab=button("моя волна",()->switchPage(false));favoritesTab=button("любимые",()->switchPage(true));''','tab fade callbacks')
one('''if(favoritesPage&&Math.abs(dx)<dp(10)){
                    v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    showPage(false);''','''if(favoritesPage&&Math.abs(dx)<dp(10)){
                    v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    switchPage(false);''','brand return fade')

# A small, pale Dark Marga broken-ring mark lives between the main content and Exit.
one('''private ImageView cover;''','''private ImageView cover,footerMark;''','footer mark field')
one('''account=text("выйти",12,activeTheme.accent);account.setTypeface(uiFontStrong());account.setGravity(Gravity.CENTER);account.setPadding(dp(8),dp(7),dp(8),dp(7));account.setOnClickListener(v->logout());root.addView(account,new LinearLayout.LayoutParams(-1,dp(32)));''','''footerMark=new ImageView(this);footerMark.setImageResource(ru.classic.music.R.drawable.ic_tm_mark);footerMark.setScaleType(ImageView.ScaleType.CENTER_INSIDE);footerMark.setAlpha(.12f);LinearLayout.LayoutParams markLp=new LinearLayout.LayoutParams(-1,dp(26));markLp.setMargins(0,dp(2),0,0);root.addView(footerMark,markLp);
        account=text("выйти",12,activeTheme.accent);account.setTypeface(uiFontStrong());account.setGravity(Gravity.CENTER);account.setPadding(dp(8),dp(7),dp(8),dp(7));account.setOnClickListener(v->logout());root.addView(account,new LinearLayout.LayoutParams(-1,dp(32)));''','add footer mark')
one('''controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(loggedIn?View.VISIBLE:View.GONE);configureControls(favoritesPage);''','''controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(loggedIn?View.VISIBLE:View.GONE);if(footerMark!=null)footerMark.setVisibility(loggedIn&&!favoritesPage?View.VISIBLE:View.INVISIBLE);configureControls(favoritesPage);''','footer mark visibility')

p.write_text(s)
