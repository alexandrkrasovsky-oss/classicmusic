from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

# --- MainActivity: softer typography, footer mark on both pages, track-based wave ---
p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

s=one(s,
'''private void styleToggle(Button b,boolean on){if(b==null)return;b.setSelected(on);b.setBackground(shape(on?activeTheme.dark:activeTheme.paper,on?0:activeTheme.line,14));b.setTextColor(on?Color.WHITE:activeTheme.ink);}''',
'''private void styleToggle(Button b,boolean on){if(b==null)return;b.setSelected(on);b.setBackground(shape(on?activeTheme.dark:activeTheme.paper,on?0:activeTheme.line,14));b.setTextColor(on?Color.WHITE:mixColor(activeTheme.ink,activeTheme.muted,.42f));}''',
'soften inactive toggles')

s=one(s,
'''Button b=new Button(this);b.setText(label);b.setTextSize(14);b.setTextColor(activeTheme.ink);b.setTypeface(uiFont());b.setLetterSpacing(-0.01f);b.setAllCaps(false);b.setMinHeight(dp(48));b.setMinimumHeight(dp(48));''',
'''Button b=new Button(this);b.setText(label);b.setTextSize(14);b.setTextColor(mixColor(activeTheme.ink,activeTheme.muted,.42f));b.setTypeface(uiFont());b.setLetterSpacing(-0.01f);b.setAllCaps(false);b.setMinHeight(dp(48));b.setMinimumHeight(dp(48));''',
'soften button text')

s=one(s,
'''for(Button b:outlineButtons){b.setBackground(shape(t.paper,t.line,14));b.setTextColor(t.ink);}''',
'''for(Button b:outlineButtons){b.setBackground(shape(t.paper,t.line,14));b.setTextColor(mixColor(t.ink,t.muted,.42f));}''',
'soften themed button text')

s=one(s,
'''brand.setTextColor(activeTheme.ink);''',
'''brand.setTextColor(mixColor(activeTheme.ink,activeTheme.muted,.35f));''',
'soften return-home label')

s=one(s,
'''shuffle=button("вразброс",()->{if(service!=null){if(service.current==null)stopRadio(true);service.toggleShuffle();}});addWeighted(options,shuffle);''',
'''shuffle=button("волна по треку",()->{if(service!=null&&service.current!=null){stopRadio(true);service.startTrackWave();}});shuffle.setTextSize(12);addWeighted(options,shuffle);''',
'track wave button')

s=one(s,
'''if(footerMark!=null)footerMark.setVisibility(loggedIn&&!favoritesPage?View.VISIBLE:View.INVISIBLE);''',
'''if(footerMark!=null)footerMark.setVisibility(loggedIn?View.VISIBLE:View.INVISIBLE);''',
'footer logo on both pages')

s=one(s,
'''shuffle.setSelected(service!=null&&service.isShuffle());shuffle.setEnabled(service!=null&&loggedIn);shuffle.setText("вразброс");repeat.setSelected(service!=null&&service.isRepeat());repeat.setText("повтор");''',
'''shuffle.setSelected(service!=null&&service.isTrackWave());shuffle.setEnabled(has);shuffle.setText("волна по треку");repeat.setSelected(service!=null&&service.isRepeat());repeat.setText("повтор");''',
'track wave state')

p.write_text(s)

# --- Api: allow rotor station to be selected dynamically ---
p=Path('app/src/main/java/ru/classic/music/Api.java')
s=p.read_text()

s=one(s,
'''    List<Track> wave(String last) throws Exception {
        JSONObject r=(JSONObject)call("/rotor/station/"+STATION+"/tracks"+(last.isEmpty()?"":"?queue="+enc(last)),null);
        JSONArray a=r.getJSONArray("sequence");List<Track> list=new ArrayList<>();
        for(int i=0;i<a.length();i++){Track t=new Track(a.getJSONObject(i).getJSONObject("track"));t.batch=r.optString("batchId");list.add(t);}return list;
    }
    void feedback(String type,Track t,float seconds) throws Exception {
        Map<String,String> data=form("type",type,"timestamp",Double.toString(System.currentTimeMillis()/1000.0));
        if(t!=null){data.put("trackId",t.id);data.put("totalPlayedSeconds",Float.toString(seconds));}
        if(type.equals("radioStarted"))data.put("from","mobile-radio-user-onyourwave");
        call("/rotor/station/"+STATION+"/feedback"+(t==null||t.batch.isEmpty()?"":"?batch-id="+enc(t.batch)),data);
    }
''',
'''    List<Track> wave(String last) throws Exception { return wave(STATION,last); }
    List<Track> wave(String station,String last) throws Exception {
        JSONObject r=(JSONObject)call("/rotor/station/"+station+"/tracks"+(last.isEmpty()?"":"?queue="+enc(last)),null);
        JSONArray a=r.getJSONArray("sequence");List<Track> list=new ArrayList<>();
        for(int i=0;i<a.length();i++){Track t=new Track(a.getJSONObject(i).getJSONObject("track"));t.batch=r.optString("batchId");list.add(t);}return list;
    }
    void feedback(String type,Track t,float seconds) throws Exception { feedback(STATION,type,t,seconds); }
    void feedback(String station,String type,Track t,float seconds) throws Exception {
        Map<String,String> data=form("type",type,"timestamp",Double.toString(System.currentTimeMillis()/1000.0));
        if(t!=null){data.put("trackId",t.id);data.put("totalPlayedSeconds",Float.toString(seconds));}
        if(type.equals("radioStarted")&&STATION.equals(station))data.put("from","mobile-radio-user-onyourwave");
        call("/rotor/station/"+station+"/feedback"+(t==null||t.batch.isEmpty()?"":"?batch-id="+enc(t.batch)),data);
    }
''',
'generic rotor station')

p.write_text(s)

# --- PlaybackService: real "wave by track" instead of shuffle ---
p=Path('app/src/main/java/ru/classic/music/PlaybackService.java')
s=p.read_text()

s=one(s,
'''    private boolean ready=false,wave=false,shuffle=false,repeat=false,resumeAfterFocus=false,foreground=false;
''',
'''    private boolean ready=false,wave=false,shuffle=false,repeat=false,resumeAfterFocus=false,foreground=false;
    private String station=Api.STATION;
''',
'station state')

s=one(s,
'''    boolean isWave(){return wave;}
    boolean isShuffle(){return shuffle;}
''',
'''    boolean isWave(){return wave;}
    boolean isTrackWave(){return wave&&!Api.STATION.equals(station);}
    boolean isShuffle(){return shuffle;}
''',
'track wave state getter')

s=one(s,
'''    void startFavorites(List<Api.Track> tracks,int selected){
        if(tracks.isEmpty())return;finishFeedback("skip");wave=false;queue.clear();queue.addAll(tracks);index=selected;load();
    }
''',
'''    void startFavorites(List<Api.Track> tracks,int selected){
        if(tracks.isEmpty())return;finishFeedback("skip");wave=false;station=Api.STATION;queue.clear();queue.addAll(tracks);index=selected;load();
    }
''',
'favorites resets station')

s=one(s,
'''    void startWave(){
        finishFeedback("skip");wave=true;queue.clear();index=-1;resetPlayer();current=null;
        int ticket=++generation;foreground();notifyUser("Загрузка моей волны…");
        worker.execute(()->{try{
            List<Api.Track> list=api.wave("");
            main.post(()->{if(ticket!=generation)return;if(list.isEmpty()){failed("Волна не вернула треки. Попробуй ещё раз.");return;}queue.addAll(list);index=0;feedback("radioStarted",list.get(0),0);load();});
        }catch(Exception e){main.post(()->{if(ticket==generation)failed(Api.message(e));});}});
    }
''',
'''    void startWave(){
        finishFeedback("skip");wave=true;station=Api.STATION;queue.clear();index=-1;resetPlayer();current=null;
        int ticket=++generation;foreground();notifyUser("Загрузка моей волны…");
        worker.execute(()->{try{
            List<Api.Track> list=api.wave(station,"");
            main.post(()->{if(ticket!=generation)return;if(list.isEmpty()){failed("Волна не вернула треки. Попробуй ещё раз.");return;}queue.addAll(list);index=0;feedback("radioStarted",list.get(0),0);load();});
        }catch(Exception e){main.post(()->{if(ticket==generation)failed(Api.message(e));});}});
    }
    void startTrackWave(){
        if(current==null)return;
        Api.Track seed=current;finishFeedback("skip");wave=true;station="track:"+seed.id;queue.clear();index=-1;resetPlayer();current=null;
        int ticket=++generation;foreground();notifyUser("Загрузка волны по треку…");
        worker.execute(()->{try{
            List<Api.Track> list=api.wave(station,"");list.removeIf(t->t.id.equals(seed.id));
            main.post(()->{if(ticket!=generation)return;if(list.isEmpty()){failed("Не удалось подобрать похожие треки.");return;}queue.addAll(list);index=0;feedback("radioStarted",list.get(0),0);load();});
        }catch(Exception e){main.post(()->{if(ticket==generation)failed(Api.message(e));});}});
    }
''',
'start track wave')

s=one(s,
'''        if(!playing()){player.start();playStartedAt=SystemClock.elapsedRealtime();}status=wave?"Моя волна":"Любимые песни";changed();
''',
'''        if(!playing()){player.start();playStartedAt=SystemClock.elapsedRealtime();}status=wave?(Api.STATION.equals(station)?"Моя волна":"Волна по треку"):"Любимые песни";changed();
''',
'track wave status')

s=one(s,
'''            List<Api.Track> list=api.wave(last);list.removeIf(t->t.id.equals(last));
''',
'''            List<Api.Track> list=api.wave(station,last);list.removeIf(t->t.id.equals(last));
''',
'continue selected wave')

s=one(s,
'''        worker.execute(()->{try{api.feedback(type,t,seconds);}catch(Exception ignored){}});
''',
'''        String activeStation=station;worker.execute(()->{try{api.feedback(activeStation,type,t,seconds);}catch(Exception ignored){}});
''',
'feedback selected station')

s=one(s,
'''        ++generation;resetPlayer();current=null;artwork=null;queue.clear();index=-1;wave=false;resumeAfterFocus=false;status="Выбери музыку";
''',
'''        ++generation;resetPlayer();current=null;artwork=null;queue.clear();index=-1;wave=false;station=Api.STATION;resumeAfterFocus=false;status="Выбери музыку";
''',
'reset station on stop')

p.write_text(s)
