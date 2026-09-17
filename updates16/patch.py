from pathlib import Path


def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

s=one(s,
'''    private void updateBrandText(){
        if(brand==null)return;
        if(favoritesPage){
            brand.setText("вернуться на главную");
            brand.setTextColor(mixColor(activeTheme.ink,activeTheme.muted,.35f));
            brand.setContentDescription("Вернуться на главную");
            return;
        }
        SpannableString x=new SpannableString("музыка без лишнего");
''',
'''    private void updateBrandText(){
        if(brand==null)return;
        SpannableString x=new SpannableString("музыка без лишнего");
''',
'always show brand')

s=one(s,
'''                if(favoritesPage&&Math.abs(dx)<dp(10)){
                    v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    switchPage(false);
                }
''',
'''                if(Math.abs(dx)<dp(10))v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
''',
'brand tap no navigation')

s=one(s,
'''        tabs=row();waveTab=button("моя волна",()->switchPage(false));favoritesTab=button("любимые",()->switchPage(true));addWeighted(tabs,waveTab);addWeighted(tabs,favoritesTab);mainContent.addView(tabs);tabsGap=new Space(this);mainContent.addView(tabsGap,new LinearLayout.LayoutParams(1,dp(6)));
''',
'''        tabs=row();waveTab=button("моя волна",()->selectPage(false));favoritesTab=button("любимые",()->selectPage(true));addWeighted(tabs,waveTab);addWeighted(tabs,favoritesTab);mainContent.addView(tabs);tabsGap=new Space(this);mainContent.addView(tabsGap,new LinearLayout.LayoutParams(1,dp(6)));
''',
'tab callbacks')

s=one(s,
'''    private void switchPage(boolean target){
''',
'''    private void selectPage(boolean target){
        if(target==favoritesPage){
            Toast.makeText(this,"ты и так здесь",Toast.LENGTH_SHORT).show();
            return;
        }
        switchPage(target);
    }
    private void switchPage(boolean target){
''',
'active tab hint')

s=one(s,
'''        tabs.setVisibility(favoritesPage?View.GONE:View.VISIBLE);
        tabsGap.setVisibility(favoritesPage?View.GONE:View.VISIBLE);
''',
'''        tabs.setVisibility(View.VISIBLE);
        tabsGap.setVisibility(View.VISIBLE);
''',
'identical tabs on both pages')

p.write_text(s)
