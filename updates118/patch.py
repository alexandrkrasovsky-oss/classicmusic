from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Favorites is always compact. Main keeps the full player unless the usable stage is genuinely short.
s=one(s,
'''    private void applyResponsivePlayer(){
        if(stage==null||stage.getHeight()<=0)return;
        configureControls(stage.getHeight()<dp(500));
    }
''',
'''    private void applyResponsivePlayer(){
        if(stage==null||stage.getHeight()<=0)return;
        configureControls(favoritesPage||stage.getHeight()<dp(470));
    }
''',
'page-aware compact player')

# Main page: one centered vertical composition. Every neighboring block uses the same 6dp rhythm.
s=one(s,
'''            waveButton=primaryButton("включить мою волну",()->{uiStatus="";if(service!=null)stopRadio(true);service.startWave();});LinearLayout.LayoutParams wp=new LinearLayout.LayoutParams(-1,dp(50));wp.setMargins(dp(4),0,dp(4),0);body.addView(waveButton,wp);
            Space g=new Space(this);body.addView(g,new LinearLayout.LayoutParams(1,dp(6)));
            dislikeButton=button("не нравится этот трек",()->{if(service!=null)service.dislike();});LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,dp(50));dpv.setMargins(dp(4),0,dp(4),0);body.addView(dislikeButton,dpv);
            radioButton.setVisibility(View.VISIBLE);
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(controls,cp);
            LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);contentArea.addView(status,sp);
''',
'''            waveButton=primaryButton("включить мою волну",()->{uiStatus="";if(service!=null)stopRadio(true);service.startWave();});LinearLayout.LayoutParams wp=new LinearLayout.LayoutParams(-1,dp(50));wp.setMargins(dp(4),0,dp(4),0);body.addView(waveButton,wp);
            dislikeButton=button("не нравится этот трек",()->{if(service!=null)service.dislike();});LinearLayout.LayoutParams dpv=new LinearLayout.LayoutParams(-1,dp(50));dpv.setMargins(dp(4),dp(6),dp(4),0);body.addView(dislikeButton,dpv);
            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);body.addView(controls,cp);
            radioButton.setVisibility(View.VISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);body.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.setMargins(dp(4),dp(6),dp(4),0);body.addView(status,sp);
''',
'centered main composition')

# Favorites: list gets all spare height; compact player sits below it inside the same stage.
s=one(s,
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(controls,cp);
            radioButton.setVisibility(View.INVISIBLE);LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(-1,dp(50));rp.setMargins(dp(4),dp(6),dp(4),0);contentArea.addView(radioButton,rp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(24));sp.topMargin=dp(6);contentArea.addView(status,sp);
''',
'''            LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(-1,-2);cp.setMargins(dp(4),dp(6),dp(4),0);body.addView(controls,cp);
            LinearLayout.LayoutParams sp=new LinearLayout.LayoutParams(-1,dp(20));sp.setMargins(dp(4),dp(6),dp(4),0);body.addView(status,sp);
''',
'favorites list priority')

# Slightly tighter compact player padding to preserve more list rows without changing button sizes.
s=one(s,
'''            controls.setPadding(dp(10),dp(10),dp(10),dp(10));
''',
'''            controls.setPadding(dp(8),dp(8),dp(8),dp(8));
''',
'compact player padding')

# Pagination is invisible: no technical "load more" button. Near the end of the list, fetch the next page automatically.
s=one(s,
'''            list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});LinearLayout.LayoutParams listLp=new LinearLayout.LayoutParams(-1,0,1);listLp.setMargins(dp(4),0,dp(4),dp(6));body.addView(list,listLp);
            more=button("загрузить ещё",this::loadMore);LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(-1,dp(50));mp.setMargins(dp(4),0,dp(4),0);body.addView(more,mp);updateList();
''',
'''            list.setAdapter(adapter);list.setOnItemClickListener((p,v,i,id)->{uiStatus="";if(service!=null)stopRadio(true);service.startFavorites(favorites,i);});
            list.setOnScrollListener(new AbsListView.OnScrollListener(){
                public void onScrollStateChanged(AbsListView view,int state){}
                public void onScroll(AbsListView view,int first,int visible,int total){if(total>0&&first+visible>=total-3&&!loading&&loaded<favorites.size())loadMore();}
            });
            LinearLayout.LayoutParams listLp=new LinearLayout.LayoutParams(-1,0,1);listLp.setMargins(dp(4),0,dp(4),dp(6));body.addView(list,listLp);updateList();
''',
'favorites auto pagination')

s=one(s,
'''        more.setVisibility(loaded<favorites.size()?View.VISIBLE:View.GONE);more.setEnabled(!loading);more.setText("загрузить ещё  ·  "+loaded+" / "+favorites.size());
''',
'''        if(more!=null){more.setVisibility(View.GONE);}
''',
'hide legacy more button')

p.write_text(s)
