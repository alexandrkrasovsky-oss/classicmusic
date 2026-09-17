from pathlib import Path

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

def one(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    s=s.replace(old,new,1)

# Favorites: only the top return control, no "моя волна / любимые" tabs.
one('''        this.favoritesPage=favoritesPage;\n        updateBrandText();body.removeAllViews();list=null;more=null;\n        detach(controls);detach(status);''','''        this.favoritesPage=favoritesPage;\n        updateBrandText();\n        tabs.setVisibility(favoritesPage?View.GONE:View.VISIBLE);\n        body.removeAllViews();list=null;more=null;\n        detach(controls);detach(status);detach(radioButton);''','favorites navigation')

# Radio lives by the main player; "выйти" remains the bottom root control.
one('''        root.addView(radioButton,radioLp);''','''        // radioButton is attached next to the main player by showPage()''','radio root placement')
one('''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(GAP),dp(4),0);mainContent.addView(controls,cp);\n            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(4);mainContent.addView(status,sp);''','''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(GAP),dp(4),0);mainContent.addView(controls,cp);\n            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);mainContent.addView(radioButton,rp);\n            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(4);mainContent.addView(status,sp);''','radio near player')

# No favorite-count status on the main screen.
one('''message(refs.isEmpty()?"Любимых песен пока нет":"Любимых песен: "+refs.size());updateList();''','''if(favoritesPage)message(refs.isEmpty()?"Любимых песен пока нет":"Любимых песен: "+refs.size());else{uiStatus="";if(status!=null)status.setText("");}updateList();''','favorite count on main')

# Compact favorites player.
one('''            controls.setPadding(dp(10),dp(8),dp(10),dp(8));''','''            controls.setPadding(dp(10),dp(10),dp(10),dp(10));''','compact player padding')
one('''            LinearLayout.LayoutParams gp=(LinearLayout.LayoutParams)controlsGap.getLayoutParams();gp.height=dp(4);controlsGap.setLayoutParams(gp);''','''            LinearLayout.LayoutParams gp=(LinearLayout.LayoutParams)controlsGap.getLayoutParams();gp.height=dp(10);controlsGap.setLayoutParams(gp);''','compact player gap')

# Favorites list card.
one('''        if(adapter!=null)adapter.notifyDataSetChanged();''','''        if(list!=null)list.setBackground(shape(t.paper,t.line,22));\n        if(adapter!=null)adapter.notifyDataSetChanged();''','list theme card')
one('''            list.setPadding(0,dp(6),0,dp(6));list.setClipToPadding(false);''','''            list.setPadding(dp(4),dp(6),dp(4),dp(6));list.setClipToPadding(false);list.setBackground(shape(activeTheme.paper,activeTheme.line,22));list.setClipToOutline(true);''','list card setup')
one('''            list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});body.addView(list,new LinearLayout.LayoutParams(-1,0,1));''','''            list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});LinearLayout.LayoutParams listLp=new LinearLayout.LayoutParams(-1,0,1);listLp.setMargins(dp(4),dp(2),dp(4),dp(4));body.addView(list,listLp);''','list card margins')

# Theme choice persists after restart.
s=s.replace('getPreferences(MODE_PRIVATE).edit().putInt("theme_index",themeIndex).apply();','getSharedPreferences("ui",MODE_PRIVATE).edit().putInt("theme_index",themeIndex).apply();')

p.write_text(s)
