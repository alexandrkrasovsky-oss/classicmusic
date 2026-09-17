from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Fixed central stage: header and footer never move; page content owns a stable flexible area.
s=one(s,
'''    private boolean favoritesPage=false;
    private String uiStatus="";
''',
'''    private boolean favoritesPage=false;
    private String uiStatus="";
    private FrameLayout stage;
    private LinearLayout contentArea;
''',
'stage fields')

s=one(s,
'''        mainContent=column();mainContent.setGravity(Gravity.CENTER_VERTICAL);root.addView(mainContent,new LinearLayout.LayoutParams(-1,0,1));
''',
'''        mainContent=column();mainContent.setGravity(Gravity.TOP);root.addView(mainContent,new LinearLayout.LayoutParams(-1,0,1));
''',
'fixed header gravity')

s=one(s,
'''        body=column();mainContent.addView(body,new LinearLayout.LayoutParams(-1,-2));
''',
'''        stage=new FrameLayout(this);mainContent.addView(stage,new LinearLayout.LayoutParams(-1,0,1));
        contentArea=column();contentArea.setGravity(Gravity.TOP);stage.addView(contentArea,new FrameLayout.LayoutParams(-1,-1));
        body=column();contentArea.addView(body,new LinearLayout.LayoutParams(-1,0,1));
        stage.addOnLayoutChangeListener((v,l,t,r,b,ol,ot,or,ob)->{if((b-t)!=(ob-ot))applyResponsivePlayer();});
''',
'central stage')

# Responsive player: same geometry on both pages; compact only when the physical screen is short.
s=one(s,
'''    private void selectPage(boolean target){
''',
'''    private void applyResponsivePlayer(){
        if(stage==null||stage.getHeight()<=0)return;
        configureControls(stage.getHeight()<dp(500));
    }
    private void selectPage(boolean target){
''',
'responsive player helper')

# Apple-like cross dissolve: snapshot old stage, reveal new content through it; header stays still.
old_switch='''    private void switchPage(boolean target){
        if(target==favoritesPage||mainContent==null){if(target!=favoritesPage)showPage(target);return;}
        mainContent.animate().cancel();
        mainContent.animate().alpha(0f).setDuration(85).withEndAction(()->{
            if(dead)return;
            showPage(target);
            mainContent.setAlpha(0f);
            mainContent.animate().alpha(1f).setDuration(115).start();
        }).start();
    }
'''
new_switch='''    private void switchPage(boolean target){
        if(target==favoritesPage||stage==null||contentArea==null){if(target!=favoritesPage)showPage(target);return;}
        contentArea.animate().cancel();
        int w=stage.getWidth(),h=stage.getHeight();
        if(w<=0||h<=0){showPage(target);return;}
        final android.graphics.Bitmap snapshot;
        try{
            snapshot=android.graphics.Bitmap.createBitmap(w,h,android.graphics.Bitmap.Config.ARGB_8888);
            stage.draw(new android.graphics.Canvas(snapshot));
        }catch(Throwable e){showPage(target);return;}
        final ImageView ghost=new ImageView(this);
        ghost.setImageBitmap(snapshot);ghost.setScaleType(ImageView.ScaleType.FIT_XY);ghost.setAlpha(1f);
        stage.addView(ghost,new FrameLayout.LayoutParams(-1,-1));
        showPage(target);
        contentArea.setAlpha(0f);contentArea.setScaleX(.99f);contentArea.setScaleY(.99f);
        ghost.bringToFront();
        android.view.animation.DecelerateInterpolator ease=new android.view.animation.DecelerateInterpolator(1.4f);
        ghost.animate().alpha(0f).setDuration(175).setInterpolator(ease).withEndAction(()->{
            if(ghost.getParent()==stage)stage.removeView(ghost);
            try{snapshot.recycle();}catch(Exception ignored){}
        }).start();
        contentArea.animate().alpha(1f).scaleX(1f).scaleY(1f).setStartDelay(12).setDuration(175).setInterpolator(ease).start();
    }
'''
s=one(s,old_switch,new_switch,'cross dissolve')

# Stable page geometry: both pages use the same full stage. The list flexes; player stays anchored.
s=one(s,
'''        detach(controls);detach(status);detach(radioButton);
        controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(loggedIn?View.VISIBLE:View.GONE);if(footerMark!=null)footerMark.setVisibility(loggedIn?View.VISIBLE:View.INVISIBLE);configureControls(favoritesPage);
''',
'''        detach(controls);detach(status);detach(radioButton);
        controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(loggedIn?View.VISIBLE:View.GONE);if(footerMark!=null)footerMark.setVisibility(loggedIn?View.VISIBLE:View.INVISIBLE);applyResponsivePlayer();
''',
'responsive controls')

s=one(s,
'''        LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=favoritesPage?0:-2;bp.weight=favoritesPage?1f:0f;body.setLayoutParams(bp);mainContent.setGravity(Gravity.TOP);
''',
'''        LinearLayout.LayoutParams bp=(LinearLayout.LayoutParams)body.getLayoutParams();bp.height=0;bp.weight=1f;body.setLayoutParams(bp);body.setGravity(favoritesPage?Gravity.TOP:Gravity.CENTER_VERTICAL);contentArea.setGravity(Gravity.TOP);mainContent.setGravity(Gravity.TOP);
''',
'fixed body slot')

s=one(s,
'''            mainContent.setGravity(Gravity.CENTER_VERTICAL);bp.height=-2;bp.weight=0;body.setLayoutParams(bp);authBox=column();body.addView(authBox);''',
'''            body.setGravity(Gravity.CENTER_VERTICAL);bp.height=0;bp.weight=1f;body.setLayoutParams(bp);authBox=column();body.addView(authBox);''',
'auth in stage')

s=one(s,
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(controls,cp);
            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);mainContent.addView(status,sp);
''',
'''            radioButton.setVisibility(View.VISIBLE);
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(controls,cp);
            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);contentArea.addView(status,sp);
''',
'main anchored player')

s=one(s,
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(controls,cp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(20));sp.topMargin=dp(6);mainContent.addView(status,sp);
''',
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(controls,cp);
            radioButton.setVisibility(View.INVISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);contentArea.addView(status,sp);
''',
'favorites anchored player')

# Re-evaluate compact mode after the new page has been laid out.
s=one(s,
'''        applyTheme(activeTheme);
    }
    private void updateList(){
''',
'''        applyTheme(activeTheme);stage.post(this::applyResponsivePlayer);
    }
    private void updateList(){
''',
'post responsive layout')

p.write_text(s)
