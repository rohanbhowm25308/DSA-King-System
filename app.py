from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from pathlib import Path
from dotenv import load_dotenv
import ast, json, subprocess, sys, tempfile, time, os, requests, webbrowser, threading, sqlite3, secrets, re
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
app=Flask(__name__,static_folder=str(ROOT/'static'),static_url_path='/static')
# Persistent sessions require a stable secret. Generated once on first launch.
secret_path=ROOT/'.flask_session_secret'
if not secret_path.exists():
    secret_path.write_text(secrets.token_hex(32))
app.secret_key=os.getenv('FLASK_SECRET_KEY') or secret_path.read_text().strip()
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax')
DB_PATH=ROOT/'users.sqlite3'
def db_connect():
    con=sqlite3.connect(DB_PATH)
    con.row_factory=sqlite3.Row
    return con
def init_auth_db():
    with db_connect() as con:
        con.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
init_auth_db()
with db_connect() as con:
    columns={r['name'] for r in con.execute('PRAGMA table_info(users)')}
    if 'google_sub' not in columns:
        con.execute('ALTER TABLE users ADD COLUMN google_sub TEXT')
    con.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub)')

oauth=OAuth(app)
GOOGLE_CLIENT_ID=os.getenv('GOOGLE_CLIENT_ID','').strip()
GOOGLE_CLIENT_SECRET=os.getenv('GOOGLE_CLIENT_SECRET','').strip()
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(name='google',client_id=GOOGLE_CLIENT_ID,client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope':'openid email profile'})

@app.get('/auth/google')
def google_login():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return redirect('/?'+urlencode({'auth_error':'Google login needs OAuth credentials in .env'}))
    return oauth.google.authorize_redirect(url_for('google_callback',_external=True))

@app.get('/auth/google/callback')
def google_callback():
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return redirect('/')
    try:
        token=oauth.google.authorize_access_token()
        info=token.get('userinfo') or oauth.google.userinfo(token=token)
        sub=str(info.get('sub',''))
        email=str(info.get('email','')).strip().lower()
        name=str(info.get('name') or email.split('@')[0])[:60]
        if not sub or not email or info.get('email_verified') is not True:
            raise ValueError('Google did not verify your email address.')
        with db_connect() as con:
            user=con.execute('SELECT id FROM users WHERE google_sub=?',(sub,)).fetchone()
            if not user:
                # Never silently link to a password account by email: avoids account takeover.
                existing=con.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()
                if existing:
                    raise ValueError('ACCOUNT_EXISTS: This email already has a password account. Please sign in with your email and password. For security, Google sign-in cannot automatically link an existing account.')
                cur=con.execute('INSERT INTO users(name,email,password_hash,google_sub) VALUES(?,?,?,?)',
                    (name,email,generate_password_hash(secrets.token_urlsafe(64)),sub))
                uid=cur.lastrowid
            else:uid=user['id']
        session.clear();session['uid']=uid
        return redirect('/')
    except Exception as exc:
        app.logger.exception('Google sign-in failed')
        message = str(exc)
        if message.startswith('ACCOUNT_EXISTS:'):
            detail = message.split(':',1)[1].strip()
        elif 'mismatching_state' in message or 'state' in message.lower() and 'csrf' in message.lower():
            detail = 'Google sign-in session expired or cookies were blocked. Try again using the same 127.0.0.1 address and enable cookies.'
        else:
            detail = 'Google sign-in could not finish. Check the Flask terminal logs and your OAuth client settings.'
        return redirect('/?'+urlencode({'auth_error':detail}))

@app.get('/api/auth/me')
def auth_me():
    uid=session.get('uid')
    if not uid:return jsonify(authenticated=False)
    with db_connect() as con:
        user=con.execute('SELECT id,name,email FROM users WHERE id=?',(uid,)).fetchone()
    if not user:return jsonify(authenticated=False)
    return jsonify(authenticated=True,user=dict(user))

@app.post('/api/auth/register')
def auth_register():
    d=request.get_json(silent=True) or {}
    name=str(d.get('name','')).strip()[:60]
    email=str(d.get('email','')).strip().lower()
    password=d.get('password','')
    if not name or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or not isinstance(password,str) or len(password)<8 or len(password)>128:
        return jsonify(error='Enter a name, valid email, and password of at least 8 characters.'),400
    try:
        with db_connect() as con:
            cur=con.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,generate_password_hash(password)))
            uid=cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify(error='An account with this email already exists.'),409
    session.clear();session['uid']=uid
    return jsonify(ok=True,user={'id':uid,'name':name,'email':email}),201

@app.post('/api/auth/login')
def auth_login():
    d=request.get_json(silent=True) or {}
    email=str(d.get('email','')).strip().lower()
    password=d.get('password','')
    with db_connect() as con:
        user=con.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
    if not user or not isinstance(password,str) or not check_password_hash(user['password_hash'],password):
        return jsonify(error='Invalid email or password.'),401
    session.clear();session['uid']=user['id']
    return jsonify(ok=True,user={'id':user['id'],'name':user['name'],'email':user['email']})

@app.post('/api/auth/logout')
def auth_logout():
    session.clear()
    return jsonify(ok=True)

@app.before_request
def require_login_for_private_api():
    if request.path in ('/judge','/ai','/mentor') and not session.get('uid'):
        return jsonify(error='Please log in first.'),401


@app.get('/')
def index(): return send_from_directory(ROOT,'index.html')
@app.get('/health')
def health(): return jsonify(status='ok',provider='groq' if os.getenv('GROQ_API_KEY') else 'offline-guidance')
TESTS={
1:[([[2,7,11,15],9],[0,1]),([[3,2,4],6],[1,2]),([[3,3],6],[0,1])],
2:[(['A man, a plan, a canal: Panama'],True),(['race a car'],False),([''],True)],
3:[([[-2,1,-3,4,-1,2,1,-5,4]],6),([[1]],1),([[5,4,-1,7,8]],23)],
4:[([[-1,0,3,5,9,12],9],4),([[-1,0,3,5,9,12],2],-1),([[5],5],0)],
100005:[([[0,1,0,2,1,0,1,3,2,1,2,1]],6),([[4,2,0,3,2,5]],9),([[1,2,3]],0),([[3,0,3]],3)],
100006:[([[2,1,5,6,2,3]],10),([[2,4]],4),([[1,1]],2),([[6,2,5,4,5,1,6]],12)]}

# Optional Judge0-compatible external service. No untrusted code is executed
# by the Flask process for non-Python languages. The service must be secured.
LANGUAGE_IDS={'javascript':63,'typescript':74,'java':62,'c':50,'cpp':54,'csharp':51,'go':60,'rust':73,'ruby':72,'php':68,'swift':83,'kotlin':78,'scala':81,'dart':90,'r':80}

def run_remote_judge(language, code, problem_id):
    """Judge0-compatible sandbox, one submission per test. Never run arbitrary code locally."""
    if language not in LANGUAGE_IDS:
        return jsonify(error='Unsupported language.'), 400
    if not isinstance(code,str) or not code.strip() or len(code)>20000:
        return jsonify(error='Provide source code (maximum 20,000 characters).'),400
    tests=get_tests(problem_id)
    if tests is None: return jsonify(error='Unknown problem'),404
    endpoint=os.getenv('JUDGE0_URL','').strip().rstrip('/')
    if not endpoint or not endpoint.startswith(('https://','http://')):
        return jsonify(error='Remote code execution requires a configured Judge0 server. Set JUDGE0_URL in .env; no unsafe local compiler fallback is used.'),503
    token=os.getenv('JUDGE0_API_KEY','').strip()
    headers={'Content-Type':'application/json'}
    if token: headers[os.getenv('JUDGE0_AUTH_HEADER','X-Auth-Token')]=token
    # Each submission reads a JSON array of function arguments from stdin,
    # then prints one JSON value to stdout. Works for all supported languages.
    passed=0; failure=None; started=time.monotonic()
    for args,expected in tests:
        payload={'source_code':code,'language_id':LANGUAGE_IDS[language],
                 'stdin':json.dumps(args,ensure_ascii=False)+'\n',
                 'expected_output':json.dumps(expected,ensure_ascii=False),
                 'cpu_time_limit':2,'wall_time_limit':5,'memory_limit':128000}
        try:
            r=requests.post(endpoint+'/submissions',params={'base64_encoded':'false','wait':'true'},headers=headers,json=payload,timeout=12)
            r.raise_for_status();result=r.json()
            if result.get('status',{}).get('id') in (1,2) and result.get('token'):
                poll=requests.get(endpoint+'/submissions/'+result['token'],params={'base64_encoded':'false'},headers=headers,timeout=8)
                poll.raise_for_status();result=poll.json()
            status=result.get('status',{}).get('id')
            output=(result.get('stdout') or '').strip()
            try:
                actual=json.loads(output)
                ok=(actual==expected and type(actual)==type(expected))
            except (ValueError,TypeError): ok=False
            if status==3 and ok: passed+=1
            else:
                failure=(result.get('compile_output') or result.get('stderr') or result.get('message') or
                         ('Wrong answer. Expected JSON '+json.dumps(expected)+', received '+output[:150]))[:500]
                break
        except (requests.RequestException,ValueError,KeyError) as exc:
            return jsonify(error='Remote judge unavailable: '+str(exc)[:220]),502
    return jsonify(accepted=passed==len(tests),passed=passed,total=len(tests),
                   message='All test cases passed.' if passed==len(tests) else (failure or 'Some tests failed.'),
                   runtime_ms=round((time.monotonic()-started)*1000,2))

# A reproducible expandable bank of parameterized exercises. Variants are
# not claimed to be independently curated or AI-verified new algorithms.
import random
from dsa_problem_bank import PROBLEMS as CURATED_PROBLEMS, TESTS as CURATED_TESTS
TESTS.update(CURATED_TESTS)
BASE_TITLES=['Two Sum','Valid Palindrome','Maximum Subarray','Binary Search']
def get_tests(problem_id):
    try: pid=int(problem_id)
    except (ValueError,TypeError):return None
    if pid in TESTS:return TESTS[pid]
    if pid<5 or pid>100004:return None
    base=(pid-5)%4+1
    rng=random.Random(pid)
    tests=[]
    if base==1:
        for _ in range(6):
            nums=rng.sample(range(-10000,10000),rng.randint(6,20));i,j=rng.sample(range(len(nums)),2)
            target=nums[i]+nums[j]
            # Multiple pairs can exist. Choose cases with exactly one valid pair.
            pairs=[(a,b) for a in range(len(nums)) for b in range(a+1,len(nums)) if nums[a]+nums[b]==target]
            if len(pairs)!=1:continue
            tests.append(([nums,target],list(pairs[0])))
    elif base==2:
        for _ in range(6):
            word=''.join(rng.choices('abcdefgh',k=rng.randint(3,14)))
            text=word+word[::-1] if rng.choice([True,False]) else word+'z'+word[::-1]+'q'
            clean=''.join(c.lower() for c in text if c.isalnum())
            tests.append(([text],clean==clean[::-1]))
    elif base==3:
        for _ in range(6):
            nums=[rng.randint(-50,50) for _ in range(rng.randint(2,28))]
            best=cur=nums[0]
            for v in nums[1:]:cur=max(v,cur+v);best=max(best,cur)
            tests.append(([nums],best))
    else:
        for _ in range(6):
            nums=sorted(rng.sample(range(-10000,10000),rng.randint(3,30)))
            target=rng.choice(nums) if rng.choice([True,False]) else 20001
            tests.append(([nums,target],nums.index(target) if target in nums else -1))
    return tests or TESTS[base]

@app.get('/api/problems')
def generated_problems():
    # The first four remain stable; request more variants in pages.
    try: page=max(0,min(1000,int(request.args.get('page',0))))
    except ValueError:return jsonify(error='Invalid page'),400
    if page==0:return jsonify(problems=[{'id':i,'title':t,'difficulty':'Easy' if i!=3 else 'Medium','base':i} for i,t in enumerate(BASE_TITLES,1)]+[{'id':100005,'title':'Trapping Rain Water','difficulty':'Hard','base':5},{'id':100006,'title':'Largest Rectangle in Histogram','difficulty':'Hard','base':6}]+CURATED_PROBLEMS,has_more=True)
    first=5+(page-1)*40
    problems=[{'id':pid,'title':BASE_TITLES[(pid-5)%4]+' · Challenge #'+str(pid-4),
               'difficulty':'Medium' if (pid-5)%4==2 else 'Easy','base':(pid-5)%4+1}
              for pid in range(first,min(first+40,100005))]
    return jsonify(problems=problems,has_more=first+40<=100004)

# Persistent, account-scoped progress. Only distinct curated problems count toward
# ranked progress; parameterized practice variants remain available but unranked.
CURATED_CATALOG = ([{'id':i,'title':title,'difficulty':'Medium' if i==3 else 'Easy'}
                    for i,title in enumerate(BASE_TITLES,1)] +
                   [{'id':100005,'title':'Trapping Rain Water','difficulty':'Hard'},
                    {'id':100006,'title':'Largest Rectangle in Histogram','difficulty':'Hard'}] +
                   CURATED_PROBLEMS)
# Deduplicate by stable problem ID so the progress denominator counts unique questions.
CATALOG_BY_ID = {int(p['id']): p for p in CURATED_CATALOG}
CURATED_CATALOG = list(CATALOG_BY_ID.values())
with db_connect() as con:
    con.execute('CREATE TABLE IF NOT EXISTS dsa_submissions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, problem_id INTEGER NOT NULL, language TEXT NOT NULL, accepted INTEGER NOT NULL, passed INTEGER NOT NULL, total INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
    con.execute('CREATE INDEX IF NOT EXISTS idx_dsa_submissions_user ON dsa_submissions(user_id, problem_id, accepted)')
    con.execute('CREATE TABLE IF NOT EXISTS dsa_bookmarks (user_id INTEGER NOT NULL, problem_id INTEGER NOT NULL, PRIMARY KEY(user_id,problem_id))')

def _profile_progress(uid):
    with db_connect() as con:
        solved = {int(r['problem_id']) for r in con.execute('SELECT DISTINCT problem_id FROM dsa_submissions WHERE user_id=? AND accepted=1',(uid,)) if int(r['problem_id']) in CATALOG_BY_ID}
        attempts = con.execute('SELECT COUNT(*) FROM dsa_submissions WHERE user_id=?',(uid,)).fetchone()[0]
        activity = [dict(r) for r in con.execute('SELECT DATE(created_at) day, COUNT(*) submissions, SUM(accepted) accepted FROM dsa_submissions WHERE user_id=? AND created_at>=DATETIME("now","-119 days") GROUP BY DATE(created_at) ORDER BY day',(uid,))]
        bookmarks = [r['problem_id'] for r in con.execute('SELECT problem_id FROM dsa_bookmarks WHERE user_id=?',(uid,))]
    totals={k:sum(p['difficulty']==k for p in CURATED_CATALOG) for k in ('Easy','Medium','Hard')}
    by_difficulty={k:sum(CATALOG_BY_ID[pid]['difficulty']==k for pid in solved) for k in totals}
    active_days={a['day'] for a in activity if a['submissions']}
    from datetime import date,timedelta
    today=date.today();start=today if today.isoformat() in active_days else today-timedelta(days=1)
    streak=0
    while (start-timedelta(days=streak)).isoformat() in active_days:streak+=1
    xp=sum({'Easy':50,'Medium':100,'Hard':200}[CATALOG_BY_ID[pid]['difficulty']] for pid in solved)
    return {'solved':len(solved),'solved_ids':sorted(solved),'total':len(CURATED_CATALOG),'by_difficulty':by_difficulty,'totals':totals,'submissions':attempts,'activity':activity,'streak':streak,'xp':xp,'bookmarks':bookmarks,'ranked_only':True}

@app.get('/api/progress')
def dsa_progress():
    uid=session.get('uid')
    if not uid:return jsonify(error='Log in to view saved progress'),401
    return jsonify(_profile_progress(uid))

@app.get('/api/leaderboard')
def dsa_leaderboard():
    uid=session.get('uid')
    if not uid:return jsonify(error='Log in to view leaderboard'),401
    with db_connect() as con:
        users=con.execute('SELECT id,name FROM users').fetchall()
    ranks=[]
    for user in users:
        p=_profile_progress(user['id'])
        if p['submissions']:
            ranks.append({'name':user['name'],'user_id':user['id'],'solved':p['solved'],'easy':p['by_difficulty']['Easy'],'medium':p['by_difficulty']['Medium'],'hard':p['by_difficulty']['Hard'],'xp':p['xp'],'streak':p['streak']})
    ranks.sort(key=lambda x:(-x['xp'],-x['solved'],x['user_id']))
    return jsonify(leaderboard=[dict(row,rank=i+1,is_you=row['user_id']==uid) for i,row in enumerate(ranks[:100])],your_rank=next((i+1 for i,r in enumerate(ranks) if r['user_id']==uid),None),ranked_total=len(ranks))

@app.post('/api/bookmarks/<int:pid>')
def dsa_bookmark(pid):
    uid=session.get('uid')
    if not uid:return jsonify(error='Log in first'),401
    if pid not in CATALOG_BY_ID:return jsonify(error='Unknown curated problem'),404
    with db_connect() as con:
        exists=con.execute('SELECT 1 FROM dsa_bookmarks WHERE user_id=? AND problem_id=?',(uid,pid)).fetchone()
        if exists:con.execute('DELETE FROM dsa_bookmarks WHERE user_id=? AND problem_id=?',(uid,pid))
        else:con.execute('INSERT INTO dsa_bookmarks(user_id,problem_id) VALUES(?,?)',(uid,pid))
    return jsonify(bookmarked=not bool(exists))

@app.after_request
def record_dsa_submission(response):
    if request.path!='/judge' or request.method!='POST' or response.status_code!=200 or not session.get('uid'):
        return response
    try:
        payload=request.get_json(silent=True) or {}
        pid=int(payload.get('problem_id'))
        result=response.get_json(silent=True) or {}
        if not isinstance(result.get('accepted'),bool):return response
        with db_connect() as con:
            con.execute('INSERT INTO dsa_submissions(user_id,problem_id,language,accepted,passed,total) VALUES(?,?,?,?,?,?)',
                        (session['uid'],pid,str(payload.get('language','python'))[:32],int(result['accepted']),int(result.get('passed',0)),int(result.get('total',0))))
    except (ValueError,TypeError,sqlite3.Error):
        app.logger.exception('Could not record submission')
    return response

@app.post('/judge')
def judge():
    data=request.get_json(silent=True) or {}
    problem_id=data.get('problem_id')
    code=data.get('code','')
    language=str(data.get('language','python')).lower()
    if language != 'python':
        return run_remote_judge(language, code, problem_id)
    if os.getenv('RENDER') and os.getenv('ALLOW_UNSAFE_LOCAL_EXECUTION') != '1':
        return jsonify(error='Python code execution is disabled on public Render servers for safety. Configure a securely isolated remote judge before enabling public submissions.'),503
    tests=get_tests(problem_id)
    if tests is None: return jsonify(error='Unknown problem'),404
    if not isinstance(code,str) or len(code)>12000:return jsonify(error='Invalid code'),400
    try:
        tree=ast.parse(code)
        if not any(isinstance(n,ast.FunctionDef) and n.name=='solve' for n in tree.body):
            return {'accepted':False,'passed':0,'total':len(tests),'message':'Define a solve(...) function.','runtime_ms':0}
    except SyntaxError as e:return {'accepted':False,'passed':0,'total':len(tests),'message':f'Syntax error: {e.msg} (line {e.lineno})','runtime_ms':0}
    # Development-only process isolation. Never expose this judge publicly: OS-level
    # container isolation, syscall filtering, network blocking and quotas are required.
    harness="""import json,sys\nexec(compile(sys.stdin.readline(),'<submission>','exec'))\nfor args in json.loads(sys.stdin.readline()):\n try:\n  output=solve(*args)\n  print(json.dumps({'ok':True,'value':output}))\n except Exception as e:print(json.dumps({'ok':False,'error':str(e)}))\n"""
    # The test inputs are serialized after the code to avoid embedding them in user source.
    # Run a separate local Python interpreter with an isolated temp working directory.
    t=time.monotonic()
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/'runner.py';path.write_text(harness)
        payload=json.dumps(code)+'\n'+json.dumps([x[0] for x in tests])+'\n'
        # The runner reads a JSON-encoded source string and compiles it.
        path.write_text(harness.replace("exec(compile(sys.stdin.readline(),'<submission>','exec'))","exec(compile(json.loads(sys.stdin.readline()),'<submission>','exec'))"))
        try:
            p=subprocess.run([sys.executable,'-I',str(path)],input=payload,text=True,capture_output=True,timeout=2,cwd=d)
        except subprocess.TimeoutExpired:
            return {'accepted':False,'passed':0,'total':len(tests),'message':'Time limit exceeded (2 seconds).','runtime_ms':2000}
    passed=0;error=None
    for line,(_,expected) in zip(p.stdout.splitlines(),tests):
        try:
            r=json.loads(line)
            if r.get('ok') and r.get('value')==expected:passed+=1
            elif not r.get('ok'):error=r.get('error')
        except (ValueError,TypeError):pass
    accepted=passed==len(tests) and p.returncode==0
    msg='All test cases passed.' if accepted else (error or (p.stderr[-350:] if p.stderr else 'Some test cases failed. Check edge cases and output format.'))
    return {'accepted':accepted,'passed':passed,'total':len(tests),'message':msg,'runtime_ms':round((time.monotonic()-t)*1000,2)}

# Lightweight language mismatch guard for AI analysis. This does not execute code.
LANGUAGE_LABELS={'python':'Python','c':'C','cpp':'C++','java':'Java','javascript':'JavaScript','typescript':'TypeScript','rust':'Rust','ruby':'Ruby','go':'Go','csharp':'C#','kotlin':'Kotlin','swift':'Swift','php':'PHP'}
def detect_source_language(source):
    code=source.strip()
    signals={
        'python':[r'(?m)^\s*(?:def|async def|from \w+ import|import \w+|class \w+\s*[:(])',r'(?m)^\s*(?:elif |except |with |for \w+ in |if .+:|while .+:)',r'(?m)^\s*print\s*\('],
        'cpp':[r'#include\s*<',r'\bstd::|\bcout\s*<<|\bcin\s*>>|\bvector\s*<|\busing namespace std'],
        'c':[r'#include\s*<(?:stdio|stdlib|string)\.h>',r'\bprintf\s*\(|\bscanf\s*\('],
        'java':[r'\bpublic\s+static\s+void\s+main\b',r'\bSystem\.out\.',r'\bpublic\s+class\s+\w+'],
        'javascript':[r'\bconsole\.log\s*\(',r'\b(?:const|let|var)\s+\w+\s*=',r'\bfunction\s+\w+\s*\('],
        'typescript':[r'\binterface\s+\w+',r'\btype\s+\w+\s*=',r'\b(?:const|let)\s+\w+\s*:\s*(?:string|number|boolean)'],
        'rust':[r'\bfn\s+main\s*\(',r'\blet\s+mut\b',r'\bprintln!\s*\(',r'\b(?:impl|pub fn)\b'],
        'ruby':[r'(?m)^\s*def\s+\w+[^:]*$',r'\bputs\s+|\brequire\s+[\"\']',r'(?m)^\s*end\s*$'],
        'go':[r'\bpackage\s+main\b',r'\bfunc\s+\w+\s*\(',r'\bfmt\.Print'],
        'csharp':[r'\bConsole\.WriteLine\s*\(',r'\busing\s+System\s*;',r'\bnamespace\s+\w+'],
        'kotlin':[r'\bfun\s+main\s*\(',r'\b(?:val|var)\s+\w+\s*=',r'\bprintln\s*\('],
        'swift':[r'\bimport\s+Foundation\b',r'\bfunc\s+\w+\s*\(',r'\blet\s+\w+\s*=',r'\bprint\s*\('],
        'php':[r'<\?php',r'\becho\s+',r'\$[A-Za-z_]\w*\s*=']}
    scores={lang:sum(2 if i==0 else 1 for i,pat in enumerate(patterns) if re.search(pat,code)) for lang,patterns in signals.items()}
    # Python syntax is reliably recognizable without executing it.
    if scores['python']>=2:
        try:ast.parse(code)
        except SyntaxError:pass
        else:scores['python']+=3
    top=max(scores,key=scores.get)
    return top if scores[top]>=2 else None

def language_mismatch(source,selected):
    detected=detect_source_language(source)
    if selected!='python' and (re.search(r'(?m)^\s*(?:def|async def)\s+\w+\s*\([^\n]*\)\s*(?:->[^:]*)?:',source) or re.search(r'(?m)^\s*(?:elif\b|except\b|from\s+\w+\s+import\b)',source)):
        return 'python'
    if detected and detected!=selected:
        # Overlapping syntax among C-family languages is often ambiguous.
        family={'c','cpp','java','javascript','typescript','csharp','kotlin','swift'}
        if detected in family and selected in family:
            unmistakable={'cpp':r'#include\s*<|\bstd::|\bcout\s*<<', 'java':r'\bSystem\.out\.|\bpublic\s+class', 'javascript':r'\bconsole\.log\(', 'typescript':r'\binterface\s+\w+', 'c':r'#include\s*<stdio\.h>', 'csharp':r'\bConsole\.WriteLine', 'kotlin':r'\bfun\s+main', 'swift':r'\bimport\s+Foundation'}
            if not re.search(unmistakable.get(detected,r'(?!)'),source):return None
        return detected
    return None

HINTS={1:'Use a dictionary of previously seen values. For each element, search for target minus the element.',2:'Normalize the string to lowercase alphanumeric characters before checking the reverse.',3:'Kadane’s algorithm tracks the maximum sum ending at each position.',4:'Use two bounds and check the midpoint; pay attention to the loop condition.',100005:'Try a two-pointer technique with left and right maximum heights.',100006:'A monotonic increasing stack can find the largest rectangle in linear time.'}

@app.post('/mentor')
def mentor():
    data=request.get_json(silent=True) or {}
    mode=str(data.get('mode','hint'))[:40]
    problem_id=data.get('problem_id',1)
    code=str(data.get('code',''))[:9000]
    question=str(data.get('question',''))[:1000]
    language=str(data.get('language','python'))[:30]
    result=data.get('judge_result') or {}
    if mode in ('review','counterexample','explain'):
        if not code.strip():return jsonify(mode='validation-error',message='Paste code first. The question field is optional.'),400
        if language not in LANGUAGE_LABELS:return jsonify(mode='validation-error',message='Unsupported language selection.'),400
        mismatch=language_mismatch(code,language)
        if mismatch:return jsonify(mode='validation-error',message=f'Selected {LANGUAGE_LABELS[language]}, but the pasted code appears to be {LANGUAGE_LABELS[mismatch]}. Select the correct language or paste {LANGUAGE_LABELS[language]} code.'),422
    key=os.getenv('GROQ_API_KEY','').strip()
    if key:
        task_instructions={
            'review': 'Act as a bug detective. Examine the actual code, identify concrete likely defects, explain why each is a defect, propose a corrected snippet, and give 2 tests. If the code appears correct, explicitly say no clear bug found and suggest edge cases. Do not invent execution results.',
            'counterexample': 'Generate at least 5 concrete candidate counterexample tests for this exact code. For each give input, expected output when the problem specification makes it determinable, what assumption it tests, and why it could fail. Do not claim tests were executed. Ask for the problem specification if expected output cannot be known.',
            'explain': 'Act as an AI coding mentor. Explain the algorithm and key lines, assess complexity and edge cases, suggest 2 improvements, and provide a brief example. Do not claim you executed the code.'
        }
        task=task_instructions.get(mode, 'Give actionable coding guidance for the submitted code.')
        prompt=f"Task: {task}\nLanguage: {language}\nProblem ID: {problem_id}\nLatest judge result: {json.dumps(result)[:1000]}\nOptional context: {question or 'Not provided; infer from code and state assumptions.'}\nStudent code:\n{code}"
        endpoint='https://api.groq.com/openai/v1/chat/completions'
        model=os.getenv('GROQ_TEXT_MODEL','llama-3.3-70b-versatile').strip() or 'llama-3.3-70b-versatile'
        payload={'model':model,'messages':[{'role':'system','content':'You are the DSA King System AI, a patient DSA coding mentor. Give actionable, accurate, concise feedback. Never claim code passed unless judge result says so. For hints avoid giving full solutions. For counterexamples, suggest candidate tests, and do not claim they were verified.'},{'role':'user','content':prompt}],'temperature':0.2,'max_completion_tokens':3000}
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'}
        try:
            r=requests.post(endpoint,headers=headers,json=payload,timeout=40)
            if r.status_code==404:
                fallback='openai/gpt-oss-20b'
                if model!=fallback:
                    payload['model']=fallback
                    r=requests.post(endpoint,headers=headers,json=payload,timeout=30)
            if r.status_code in (401,403):
                return jsonify(mode='groq-error',message='Groq authentication denied. Verify GROQ_API_KEY in .env, restart Flask, and check API key permissions.'),502
            if r.status_code==404:
                # Surface the provider's safe error code/message, never credentials.
                try:
                    err=r.json().get('error',{})
                    detail=str(err.get('message','Not Found'))[:350] if isinstance(err,dict) else 'Not Found'
                    code=str(err.get('code','unknown'))[:60] if isinstance(err,dict) else 'unknown'
                except (ValueError,AttributeError,TypeError):
                    detail='Groq endpoint returned Not Found (non-JSON response).'
                    code='unknown'
                app.logger.warning('Groq 404: code=%s message=%s',code,detail)
                return jsonify(mode='groq-error',message=f'Groq 404 ({code}): {detail} | Check the exact model ID and endpoint.'),502
            if r.status_code==429:
                return jsonify(mode='groq-error',message='Groq rate limit reached. Wait and retry or check account limits.'),502
            r.raise_for_status()
            response_data=r.json()
            def extract_answer(data):
                choices=data.get('choices') or []
                if not choices:return ''
                message=choices[0].get('message') or {}
                content=message.get('content') or ''
                if isinstance(content,list):
                    content='\n'.join(str(x.get('text','')) for x in content if isinstance(x,dict))
                return content.strip() if isinstance(content,str) else ''
            answer=extract_answer(response_data)
            if not answer:
                # Retry with a standard instruction model, rather than another reasoning model.
                for alternative in ('llama-3.3-70b-versatile','openai/gpt-oss-20b'):
                    if alternative==payload['model']:continue
                    retry_payload=dict(payload,model=alternative,max_completion_tokens=3000)
                    try:
                        retry=requests.post(endpoint,headers=headers,json=retry_payload,timeout=40)
                        if retry.ok:
                            answer=extract_answer(retry.json())
                            if answer:break
                        else:
                            app.logger.warning('Groq fallback %s returned HTTP %s: %s',alternative,retry.status_code,retry.text[:250])
                    except (requests.RequestException,ValueError) as error:
                        app.logger.warning('Groq fallback %s failed: %s',alternative,type(error).__name__)
            if not answer:
                finish_reason=((response_data.get('choices') or [{}])[0].get('finish_reason') or 'unknown')
                app.logger.warning('Groq empty response: model=%s finish_reason=%s',model,finish_reason)
                return jsonify(mode='groq-error',message='Groq returned no answer. Check server logs for finish_reason and verify a text-generation model is enabled in your Groq account.'),502
            return jsonify(mode='groq-ai',message=answer)
        except (requests.RequestException,ValueError,KeyError,IndexError,TypeError) as exc:
            app.logger.warning('Groq mentor request failed: %s',type(exc).__name__)
            return jsonify(mode='groq-error',message='Groq is unavailable. Check the configured model, network and Groq service status. Details: '+type(exc).__name__),502
    if mode in ('review','counterexample','explain') and code.strip():
        return jsonify(mode='ai-not-configured',message='Code-specific AI analysis is unavailable because GROQ_API_KEY is not configured. Add a valid key to your .env or Render environment and restart the server. The optional question box is not required.'),503
    if mode=='hint': msg=HINTS.get(problem_id,'Try breaking the problem into smaller steps.')
    elif mode=='counterexample':msg={1:'Try nums=[3,3], target=6.',2:'Try an empty string or punctuation-only input.',3:'Try all-negative inputs such as [-5,-2,-8].',4:'Try a one-element array or an absent target.'}.get(problem_id,'Try empty and boundary inputs.')
    elif mode=='review':msg=('The last submission failed some tests. Check edge cases. ' if not result.get('accepted') else 'Review your solution complexity. ')+HINTS.get(problem_id,'')
    else:msg=HINTS.get(problem_id,'')+' Your question: '+question
    return jsonify(mode='offline-guidance',message=msg)


# Six interactive learning modules. Local code execution is for trusted demos only.
from interview_engine import interview_api
app.register_blueprint(interview_api)

from innovation import HANDLERS
@app.post('/api/innovation/<module>')
def innovation_endpoint(module):
    if not session.get('uid'):return jsonify(error='Please log in first.'),401
    if module not in HANDLERS:return jsonify(error='Unknown module'),404
    if module in ('timeline','verifier') and os.getenv('ALLOW_UNSAFE_LOCAL_EXECUTION') != '1':
        return jsonify(error='This feature executes Python code and is disabled on public servers. Use a securely sandboxed execution service. For trusted local-only development set ALLOW_UNSAFE_LOCAL_EXECUTION=1.'),503
    data=request.get_json(silent=True) or {}
    try:return jsonify(HANDLERS[module](data))
    except (ValueError,TypeError,OverflowError) as exc:return jsonify(error=str(exc)[:250]),400
    except Exception:
        app.logger.exception('Innovation module error')
        return jsonify(error='Module could not process this request.'),500

if __name__=='__main__':
    threading.Timer(1.4,lambda:webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(host='127.0.0.1',port=5000,debug=False)
