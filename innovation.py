"""Six experimental educational modules. Never use local execution for untrusted public submissions."""
import ast, itertools, json, subprocess, sys, tempfile, time, heapq, random
from pathlib import Path

TOPICS=[('Arrays',[]),('Strings',[]),('Hash Maps',['Arrays']),('Two Pointers',['Arrays']),('Binary Search',['Arrays']),('Recursion',[]),('Sorting',['Arrays']),('Trees',['Recursion']),('Graphs',['Trees']),('Dynamic Programming',['Recursion','Arrays'])]

def inspect(code):
    if not isinstance(code,str) or len(code)>10000: raise ValueError('Provide Python code of at most 10,000 characters.')
    try: tree=ast.parse(code)
    except SyntaxError as e: raise ValueError(f'Syntax error at line {e.lineno}: {e.msg}')
    return tree

def thought(d):
    code=d.get('code',''); tree=inspect(code)
    reasoning=str(d.get('reasoning',''))[:1500].strip()
    constructs={type(n).__name__ for n in ast.walk(tree)}
    insights=[]
    if not reasoning: insights.append('Describe your approach in your own words to receive reasoning-specific feedback.')
    if 'For' in constructs or 'While' in constructs: insights.append('You use iteration. Explain the invariant that remains true after each iteration.')
    if 'Dict' in constructs or 'Set' in constructs: insights.append('You use hashing. Explain expected lookup cost and possible memory trade-offs.')
    if 'If' not in constructs: insights.append('Consider whether empty input and boundary conditions need explicit handling.')
    if 'Return' not in constructs: insights.append('No return statement detected; verify the expected function output.')
    if reasoning and not any(w in reasoning.lower() for w in ['because','since','therefore','invariant','complexity','edge','time','space']): insights.append('Strengthen your explanation: why does the algorithm work, and what are its time and space costs?')
    return {'mode':'static-coaching','insights':insights or ['Explain correctness, edge cases, and complexity to strengthen your reasoning.'],'questions':['What invariant or property proves correctness?','Which input could break your assumption?','What is your worst-case time and space complexity?'],'note':'Heuristic coaching, not a measurement of hidden thought or proof of correctness.'}

def trace(d):
    code=d.get('code','');inspect(code)
    args=d.get('args',[])
    if not isinstance(args,list) or len(json.dumps(args))>3000:raise ValueError('Arguments must be a small JSON array.')
    runner='''import json,sys\nsource=json.loads(sys.stdin.readline());args=json.loads(sys.stdin.readline());events=[];count=[0]\ndef tracer(frame,event,arg):\n if frame.f_code.co_filename=='<student>' and event=='line':\n  count[0]+=1\n  if count[0]>120:raise RuntimeError('Trace limit (120 steps) reached')\n  local={}\n  for k,v in frame.f_locals.items():\n   if not k.startswith('__'):\n    try: local[k]=repr(v)[:140]\n    except Exception:local[k]='<unavailable>'\n  events.append({'line':frame.f_lineno,'locals':local})\n return tracer\ntry:\n namespace={'__builtins__':__builtins__}\n exec(compile(source,'<student>','exec'),namespace)\n if not callable(namespace.get('solve')):raise ValueError('Define solve(...)')\n sys.settrace(tracer)\n result=namespace['solve'](*args)\n sys.settrace(None)\n try:json.dumps(result);output=result\n except:output=repr(result)\n print(json.dumps({'steps':events,'result':output}))\nexcept Exception as e:\n sys.settrace(None);print(json.dumps({'steps':events,'error':str(e)[:300]}))\n'''
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'trace.py';path.write_text(runner)
        try:r=subprocess.run([sys.executable,'-I',str(path)],input=json.dumps(code)+'\n'+json.dumps(args)+'\n',text=True,capture_output=True,timeout=2,cwd=tmp)
        except subprocess.TimeoutExpired:return {'steps':[],'error':'Trace timed out after 2 seconds.'}
    try:return json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError,IndexError):return {'steps':[],'error':'Execution failed or produced unexpected output.','stderr':r.stderr[-200:]}

def debate(d):
    code=str(d.get('code',''));tree=inspect(code)
    loops=sum(isinstance(n,(ast.For,ast.While)) for n in ast.walk(tree))
    recursive=any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==f.name for f in ast.walk(tree) if isinstance(f,ast.FunctionDef) for n in ast.walk(f))
    return {'agents':[{'name':'Correctness Advocate','argument':'First establish an invariant and verify boundary inputs. Passing examples alone cannot prove correctness.'},{'name':'Performance Advocate','argument':f'The code contains {loops} loop(s)'+(' and apparent recursion' if recursive else '')+'. Loop count alone cannot establish Big-O; analyze nesting, bounds and data structures.'}],'verdict':'A verified solution needs both correctness evidence and measured performance. Complexity is not inferred automatically from syntax.','observations':{'loop_nodes':loops,'apparent_recursion':recursive}}

def simulator(d):
    scenario=d.get('scenario','delivery'); n=int(d.get('nodes',7));n=max(3,min(16,n));seed=int(d.get('seed',42));rng=random.Random(seed)
    # Connected, nonnegative graph, with deterministic shortcuts.
    edges=[(i,i+1,rng.randint(2,12)) for i in range(n-1)]
    for i in range(n):
        for j in range(i+2,n):
            if rng.random()<.26:edges.append((i,j,rng.randint(2,18)))
    graph=[[] for _ in range(n)]
    for a,b,w in edges:graph[a].append((b,w));graph[b].append((a,w))
    dist=[float('inf')]*n;prev=[None]*n;dist[0]=0;pq=[(0,0)]
    while pq:
        cost,u=heapq.heappop(pq)
        if cost!=dist[u]:continue
        for v,w in graph[u]:
            if cost+w<dist[v]:dist[v]=cost+w;prev[v]=u;heapq.heappush(pq,(dist[v],v))
    route=[];v=n-1
    while v is not None:route.append(v);v=prev[v]
    return {'scenario':scenario,'nodes':list(range(n)),'edges':[{'from':a,'to':b,'weight':w} for a,b,w in edges],'route':route[::-1],'total_cost':dist[-1],'algorithm':'Dijkstra (nonnegative weights)','unit':'simulated cost units','note':'Generated teaching simulation; not live traffic or real delivery data.'}

def galaxy(d):
    solved=d.get('solved',[])
    if not isinstance(solved,list):solved=[]
    from dsa_problem_bank import PROBLEMS
    completed={'Arrays':1,'Strings':2,'Dynamic Programming':3,'Binary Search':4}
    # Reflect the actual curated bank as well as the four original core problems.
    mastered=set()
    for p in PROBLEMS:
        if p['id'] in solved:
            topic=str(p.get('topic','')).lower()
            for name,_ in TOPICS:
                if name.lower() in topic:mastered.add(name)
    for name,pid in completed.items():
        if pid in solved:mastered.add(name)
    nodes=[{'name':name,'prerequisites':prereqs,'status':'mastered' if name in mastered else 'available' if all(x in mastered for x in prereqs) else 'locked'} for name,prereqs in TOPICS]
    return {'nodes':nodes,'note':'Mastery reflects completed curated problems with matching topic labels; it is an indicative learning map.'}

# Fixed reference algorithms and independently generated tests. User code runs in subprocess.
def cases(problem):
    rng=random.Random(124)
    if problem==1:
        for _ in range(24):
            nums=[rng.randint(-9,9) for _ in range(rng.randint(2,8))];target=rng.randint(-15,15)
            pairs=[(i,j) for i in range(len(nums)) for j in range(i+1,len(nums)) if nums[i]+nums[j]==target]
            if pairs:yield [nums,target],pairs
    elif problem==2:
        for s in ['','a','A man, a plan, a canal: Panama','race a car','!@#','abca','0P']+[ ''.join(rng.choice('abc!A ') for _ in range(rng.randint(0,16))) for _ in range(25)]:
            x=''.join(c.lower() for c in s if c.isalnum());yield [s],x==x[::-1]
    elif problem==3:
        for _ in range(30):
            a=[rng.randint(-12,12) for _ in range(rng.randint(1,12))]
            yield [a],max(sum(a[i:j]) for i in range(len(a)) for j in range(i+1,len(a)+1))
    elif problem==4:
        for _ in range(30):
            a=sorted(rng.sample(range(-30,31),rng.randint(0,15)));t=rng.randint(-30,30)
            yield [a,t],a.index(t) if t in a else -1

def verify(d):
    code=d.get('code','');inspect(code)
    problem=int(d.get('problem_id',1))
    if problem not in (1,2,3,4):raise ValueError('Verification supports demo problems 1–4.')
    samples=list(cases(problem));payload=[args for args,_ in samples]
    runner='''import json,sys\nsrc=json.loads(sys.stdin.readline());tests=json.loads(sys.stdin.readline());ns={}\ntry:exec(compile(src,'<submission>','exec'),ns)\nexcept Exception as e:print(json.dumps({'error':str(e)}));sys.exit()\nif not callable(ns.get('solve')):print(json.dumps({'error':'Define solve(...)'}));sys.exit()\nfor args in tests:\n try:print(json.dumps({'value':ns['solve'](*args)}))\n except Exception as e:print(json.dumps({'error':str(e)[:150]}))\n'''
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'verify.py';path.write_text(runner)
        try:r=subprocess.run([sys.executable,'-I',str(path)],input=json.dumps(code)+'\n'+json.dumps(payload)+'\n',text=True,capture_output=True,timeout=3,cwd=tmp)
        except subprocess.TimeoutExpired:return {'status':'timeout','tested':0,'message':'Verification timed out after 3 seconds.'}
    lines=r.stdout.splitlines();checked=0;failure=None
    for i,(args,expected) in enumerate(samples):
        if i>=len(lines):failure={'input':args,'expected':expected,'actual':'No output'};break
        try:obj=json.loads(lines[i]);actual=obj.get('value')
        except ValueError:actual='Invalid JSON';obj={}
        valid=actual==expected
        if problem==1:
            valid=(isinstance(actual,list) and len(actual)==2 and all(type(x)==int and 0<=x<len(args[0]) for x in actual) and actual[0]!=actual[1] and args[0][actual[0]]+args[0][actual[1]]==args[1])
        checked+=1
        if not valid or 'error' in obj:failure={'input':args,'expected':expected if problem!=1 else 'any two distinct valid indices','actual':obj.get('error',actual)};break
    return {'status':'counterexample_found' if failure else 'passed_generated_tests','tested':checked,'total':len(samples),'counterexample':failure,'message':'Generated tests passed; this is not a formal proof.' if not failure else 'Found a failing input.','note':'Local subprocess testing is for trusted demos only; use a hardened sandbox before public deployment.'}

HANDLERS={'thought':thought,'timeline':trace,'debate':debate,'simulator':simulator,'galaxy':galaxy,'verifier':verify}
