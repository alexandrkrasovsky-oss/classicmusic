from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# The central content starts immediately after the tabs. No elastic hole between navigation and content.
s=one(s,
'''        LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=0;bp.weight=1f;body.setLayoutParams(bp);body.setGravity(favoritesPage?Gravity.TOP:Gravity.CENTER_VERTICAL);contentArea.setGravity(Gravity.TOP);mainContent.setGravity(Gravity.TOP);
''',
'''        LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=0;bp.weight=1f;body.setLayoutParams(bp);body.setGravity(Gravity.TOP);contentArea.setGravity(Gravity.TOP);mainContent.setGravity(Gravity.TOP);
''',
'no elastic gap below tabs')

# The status line duplicated information and made the bottom look as if it jumped. Keep it as an internal object for messages, but never allocate layout height for it.
s=one(s,
'''            radioButton.setVisibility(View.VISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);body.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.setMargins(dp(4),dp(6),dp(4),0);body.addView(status,sp);
''',
'''            radioButton.setVisibility(View.VISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);body.addView(radioButton,rp);
            status.setVisibility(View.GONE);
''',
'remove main status row')

s=one(s,
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);body.addView(controls,cp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(20));sp.setMargins(dp(4),dp(6),dp(4),0);body.addView(status,sp);
''',
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);body.addView(controls,cp);
            status.setVisibility(View.GONE);
''',
'remove favorites status row')

# Center the complete MAIN composition as one object while preserving the strict 6dp rhythm inside it.
# We move the shared header by responsive top padding, not by inserting a variable gap between tabs and content.
s=one(s,
'''        stage.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{if((b-t)!=(ob-ot))applyResponsivePlayer();});
''',
'''        stage.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{if((b-t)!=(ob-ot)){applyResponsivePlayer();if(!favoritesPage)stage.post(this::balanceMainLayout);}});
''',
'rebalance on size change')

s=one(s,
'''    private void applyResponsivePlayer(){
        if(stage==null||stage.getHeight()<=0)return;
        configureControls(favoritesPage||stage.getHeight()<dp(470));
    }
''',
'''    private void applyResponsivePlayer(){
        if(stage==null||stage.getHeight()<=0)return;
        configureControls(favoritesPage||stage.getHeight()<dp(470));
    }
    private void balanceMainLayout(){
        if(favoritesPage||mainContent==null||stage==null||body==null||body.getChildCount()==0)return;
        int contentBottom=0;
        for(int i=0;i<body.getChildCount();i++){
            View child=body.getChildAt(i);
            if(child.getVisibility()!=View.GONE)contentBottom=Math.max(contentBottom,child.getBottom());
        }
        if(contentBottom<=0)return;
        int oldTop=mainContent.getPaddingTop();
        int headerHeight=stage.getTop()-oldTop;
        int total=headerHeight+contentBottom;
        int desired=Math.max(0,(mainContent.getHeight()-total)/2);
        if(Math.abs(desired-oldTop)>1){
            mainContent.setPadding(mainContent.getPaddingLeft(),desired,mainContent.getPaddingRight(),mainContent.getPaddingBottom());
        }
    }
''',
'balance full main composition')

# Replace the simple dissolve with a subtle Apple-like compress/expand morph.
s=one(s,
'''        showPage(target);
        contentArea.setAlpha(0f);contentArea.setScaleX(.99f);contentArea.setScaleY(.99f);
        ghost.bringToFront();
        android.view.animation.DecelerateInterpolator ease=new android.view.animation.DecelerateInterpolator(1.4f);
        ghost.animate().alpha(0f).setDuration(175).setInterpolator(ease).withEndAction(()->{
            if(ghost.getParent()==stage)stage.removeView(ghost);
            try{snapshot.recycle();}catch(Exception ignored){}
        }).start();
        contentArea.animate().alpha(1f).scaleX(1f).scaleY(1f).setStartDelay(12).setDuration(175).setInterpolator(ease).start();
''',
'''        boolean toFavorites=target;
        showPage(target);
        contentArea.setPivotX(stage.getWidth()/2f);contentArea.setPivotY(stage.getHeight()/2f);
        ghost.setPivotX(stage.getWidth()/2f);ghost.setPivotY(stage.getHeight()/2f);
        contentArea.setAlpha(0f);contentArea.setScaleX(.995f);contentArea.setScaleY(toFavorites?1.025f:.975f);
        ghost.bringToFront();
        android.view.animation.DecelerateInterpolator ease=new android.view.animation.DecelerateInterpolator(1.55f);
        ghost.animate().alpha(0f).scaleX(.995f).scaleY(toFavorites?.975f:1.025f).setDuration(235).setInterpolator(ease).withEndAction(()->{
            if(ghost.getParent()==stage)stage.removeView(ghost);
            try{snapshot.recycle();}catch(Exception ignored){}
        }).start();
        contentArea.animate().alpha(1f).scaleX(1f).scaleY(1f).setStartDelay(8).setDuration(235).setInterpolator(ease).withEndAction(()->{if(!favoritesPage)stage.post(this::balanceMainLayout);}).start();
''',
'compress expand crossfade')

# Balance once the main page has its actual measured player height. Favorites retains that same header position.
s=one(s,
'''        applyTheme(activeTheme);stage.post(this::applyResponsivePlayer);
''',
'''        applyTheme(activeTheme);stage.post(()->{applyResponsivePlayer();if(!favoritesPage)stage.post(this::balanceMainLayout);});
''',
'post layout balance')

p.write_text(s)
