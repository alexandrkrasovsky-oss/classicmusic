from pathlib import Path

def one(text, old, new, label):
    count=text.count(old)
    if count!=1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old,new,1)

p=Path('app/src/main/java/ru/classic/music/MainActivity.java')
s=p.read_text()

# Remove the easy-to-hit logout control from the everyday player UI.
# Keep an invisible zero-height account view only because existing theme/page code references it.
s=one(s,
'''        account=text("выйти",12,activeTheme.accent);account.setTypeface(uiFontStrong());account.setGravity(Gravity.CENTER);account.setPadding(dp(6),dp(7),dp(6),dp(7));account.setOnClickListener(v->logout());root.addView(account,new LinearLayout.LayoutParams(-1,dp(32)));
''',
'''        account=text("",12,activeTheme.accent);account.setVisibility(View.GONE);root.addView(account,new LinearLayout.LayoutParams(-1,0));
''',
'remove logout control')

s=one(s,
'''        controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(loggedIn?View.VISIBLE:View.GONE);if(footerMark!=null)footerMark.setVisibility(loggedIn?View.VISIBLE:View.INVISIBLE);applyResponsivePlayer();
''',
'''        controls.setVisibility(loggedIn?View.VISIBLE:View.GONE);account.setVisibility(View.GONE);if(footerMark!=null)footerMark.setVisibility(loggedIn?View.VISIBLE:View.INVISIBLE);applyResponsivePlayer();
''',
'keep logout hidden')

p.write_text(s)
