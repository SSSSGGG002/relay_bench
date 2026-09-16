#!/usr/bin/env python3
"""Generate the IQ item bank (suite/iq.json) with machine-verified answers.

Every item's answer is computed by code (simulation / brute force / sqlite / node),
so the bank can be regenerated with a new seed at any time:  python3 gen_iq.py --seed 123
Tiers:
  direct : must be answered WITHOUT chain-of-thought (max_tokens ~40, thinking off)
  reason : chain-of-thought allowed, final line 'ANSWER: ...'
  hard   : same format, much harder (search / constraint problems)
"""
import argparse, itertools, json, random, sqlite3, string, subprocess, sys, os, datetime, heapq, collections

WORDS = ("apple river stone cloud bright silver window garden yellow purple dream forest "
         "castle meadow ocean quiet thunder velvet copper marble candle orbit puzzle rocket "
         "timber violet anchor breeze canyon desert ember falcon glacier harbor island jungle "
         "kettle lantern mirror nectar oyster pepper quartz ribbon saddle tunnel umbrella walnut").split()
PALS = ["level", "rotor", "kayak", "deified", "civic", "madam", "refer", "noon", "stats", "racecar", "redder", "tenet"]
NONPALS = ["table", "planet", "cactus", "silver", "button", "garden", "marble", "orbit", "pencil", "rocket", "window", "zebra"]

def norm_alnum(rng, n):
    alpha = "abcdefghjkmnpqrstuvwxyz23456789"  # no 0/O/1/l/i ambiguity
    return "".join(rng.choice(alpha) for _ in range(n))

def gen_direct(rng):
    items = []
    a, b = rng.randint(1000, 9999), rng.randint(1000, 9999)
    items.append(dict(id="D1", cat="arithmetic", q=f"Compute {a} × {b}.", ans=str(a * b)))
    words = [rng.choice(WORDS) for _ in range(22)]
    text = " ".join(words)
    items.append(dict(id="D2", cat="counting", q=f"How many times does the letter 'e' (case-insensitive) appear in the following text?\n\n\"{text}\"", ans=str(text.lower().count("e"))))
    s = norm_alnum(rng, 13)
    items.append(dict(id="D3", cat="string", q=f"Reverse this string exactly: {s}", ans=s[::-1]))
    nums = [rng.randint(100, 999) for _ in range(12)]
    items.append(dict(id="D4", cat="arithmetic", q=f"Sum these numbers: {', '.join(map(str, nums))}", ans=str(sum(nums))))
    nums2 = rng.sample(range(100, 999), 10)
    items.append(dict(id="D5", cat="sorting", q=f"Sort these numbers in descending order, comma-separated: {', '.join(map(str, nums2))}", ans=", ".join(map(str, sorted(nums2, reverse=True)))))
    d = datetime.date(rng.randint(1905, 2095), rng.randint(1, 12), rng.randint(1, 28))
    items.append(dict(id="D6", cat="calendar", q=f"What day of the week is {d.isoformat()} in the Gregorian calendar? Output only the weekday name.", ans=d.strftime("%A")))
    k = rng.randint(3, 6)
    lst = rng.sample(PALS, k) + rng.sample(NONPALS, 12 - k); rng.shuffle(lst)
    items.append(dict(id="D7", cat="counting", q=f"How many of these words are palindromes? {', '.join(lst)}", ans=str(k)))
    h = rng.randint(0x10000, 0xFFFFF)
    items.append(dict(id="D8", cat="base", q=f"Convert hexadecimal 0x{h:X} to decimal.", ans=str(h)))
    return items

# ---------------- reason tier ----------------
def run_vm(prog, limit=2000):
    r = [0, 0, 0, 0]; pc = 0; steps = 0
    while pc < len(prog) and steps < limit:
        steps += 1
        op = prog[pc]
        name = op[0]
        if name == "SET": r[op[1]] = op[2]
        elif name == "ADD": r[op[1]] += op[2]
        elif name == "ADDR": r[op[1]] += r[op[2]]
        elif name == "MUL": r[op[1]] *= op[2]
        elif name == "MOD": r[op[1]] %= op[2]
        elif name == "DEC": r[op[1]] -= 1
        elif name == "JNZ":
            if r[op[1]] != 0: pc = op[2] - 1; continue
        elif name == "HALT": break
        pc += 1
    return r, steps

def gen_vm(rng):
    while True:
        n = rng.randint(6, 11); m1 = rng.randint(2, 5); md = rng.choice([53, 61, 89, 97, 101]); add = rng.randint(2, 9)
        prog = [("SET", 0, n), ("SET", 1, 1), ("SET", 2, add),           # 1..3
                ("MUL", 1, m1), ("MOD", 1, md), ("ADDR", 2, 1), ("ADDR", 3, 2),  # 4..7
                ("DEC", 0), ("JNZ", 0, 4), ("MOD", 3, 1000), ("HALT",)]        # 8..11
        r, steps = run_vm(prog)
        if steps < 2000: break
    lines = []
    for i, op in enumerate(prog, 1):
        if op[0] in ("SET", "ADD", "MUL", "MOD"): lines.append(f"{i}: {op[0]} r{op[1]}, {op[2]}")
        elif op[0] == "ADDR": lines.append(f"{i}: ADDR r{op[1]}, r{op[2]}")
        elif op[0] == "DEC": lines.append(f"{i}: DEC r{op[1]}")
        elif op[0] == "JNZ": lines.append(f"{i}: JNZ r{op[1]}, {op[2]}")
        else: lines.append(f"{i}: HALT")
    q = ("A register machine has registers r0..r3, all initially 0. Instructions (lines are 1-indexed):\n"
         "SET r, v  -> r = v;  ADD r, v -> r = r + v;  ADDR r, s -> r = r + s (s is a register);\n"
         "MUL r, v -> r = r * v;  MOD r, v -> r = r mod v;  DEC r -> r = r - 1;\n"
         "JNZ r, L -> if r != 0 jump to line L, else continue;  HALT -> stop.\n"
         "Program:\n" + "\n".join(lines) + "\n\nRun it to completion. Give the final register values as JSON {\"r0\":..,\"r1\":..,\"r2\":..,\"r3\":..}.")
    return dict(id="R1", cat="simulation", q=q, ans=json.dumps({"r0": r[0], "r1": r[1], "r2": r[2], "r3": r[3]}), kind="json")

def gen_ca(rng):
    rule = rng.choice([30, 90, 110, 150, 184, 54, 126])
    cells = [rng.randint(0, 1) for _ in range(16)]
    while sum(cells) in (0, 16): cells = [rng.randint(0, 1) for _ in range(16)]
    init = "".join(map(str, cells)); steps = 8
    cur = cells[:]
    for _ in range(steps):
        cur = [(rule >> ((cur[(i - 1) % 16] << 2) | (cur[i] << 1) | cur[(i + 1) % 16])) & 1 for i in range(16)]
    q = (f"An elementary cellular automaton with Wolfram rule {rule} runs on a ring of 16 cells (cell 0's left neighbour is cell 15). "
         f"Initial state (cell 0 to cell 15): {init}. Apply the rule synchronously for exactly {steps} steps. "
         "Give the final state as a 16-character string of 0s and 1s.")
    return dict(id="R2", cat="simulation", q=q, ans="".join(map(str, cur)))

def gen_pipeline(rng):
    s = norm_alnum(rng, 12)
    ops = []
    def rot13(x): return x.translate(str.maketrans(string.ascii_lowercase + string.ascii_uppercase, string.ascii_lowercase[13:] + string.ascii_lowercase[:13] + string.ascii_uppercase[13:] + string.ascii_uppercase[:13]))
    catalog = [
        ("reverse the string", lambda x: x[::-1]),
        ("apply ROT13 to letters (digits unchanged)", rot13),
        ("convert letters to uppercase", lambda x: x.upper()),
        ("delete every vowel (a,e,i,o,u in either case)", lambda x: "".join(c for c in x if c.lower() not in "aeiou")),
        ("keep only characters at even 0-based indices", lambda x: x[0::2]),
        ("move the first two characters to the end", lambda x: x[2:] + x[:2]),
        ("replace every digit d with (9-d)", lambda x: "".join(str(9 - int(c)) if c.isdigit() else c for c in x)),
        ("append the length of the current string as decimal digits", lambda x: x + str(len(x))),
        ("swap each adjacent pair of characters (positions 0<->1, 2<->3, ...; an unpaired last char stays)", lambda x: "".join(x[i + 1] + x[i] if i + 1 < len(x) else x[i] for i in range(0, len(x), 2))),
    ]
    chosen = rng.sample(catalog, 7)
    cur = s
    for desc, f in chosen:
        ops.append(desc); cur = f(cur)
    q = f"Start with the string: {s}\nApply these operations in order:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(ops)) + "\nWhat is the final string?"
    return dict(id="R3", cat="string", q=q, ans=cur)

def gen_josephus(rng):
    n, k = rng.randint(20, 40), rng.randint(3, 9)
    people = list(range(1, n + 1)); idx = 0; order = []
    while len(people) > 1:
        idx = (idx + k - 1) % len(people); order.append(people.pop(idx))
    q = (f"{n} people numbered 1..{n} stand in a circle. Starting the count at person 1, every {k}-th person is eliminated "
         f"(person {k} goes first), counting continues from the next person after each elimination. Which number is the last survivor?")
    return dict(id="R4", cat="simulation", q=q, ans=str(people[0]))

def gen_graph(rng):
    nodes = "ABCDEFGH"
    while True:
        edges = {}
        for i in range(8):
            for j in range(8):
                if i != j and rng.random() < 0.3:
                    edges[(i, j)] = rng.randint(1, 9)
        for i in range(7):
            if (i, i + 1) not in edges and rng.random() < 0.6: edges[(i, i + 1)] = rng.randint(1, 9)
        dist = [10**9] * 8; cnt = [0] * 8; dist[0] = 0; cnt[0] = 1
        pq = [(0, 0)]; done = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in done: continue
            done.add(u)
            for (a, b), w in edges.items():
                if a != u: continue
                nd = d + w
                if nd < dist[b]: dist[b] = nd; cnt[b] = cnt[u]; heapq.heappush(pq, (nd, b))
                elif nd == dist[b]: cnt[b] += cnt[u]
        if dist[7] < 10**9 and cnt[7] >= 2 and len(edges) <= 22: break
    elist = ", ".join(f"{nodes[a]}->{nodes[b]}({w})" for (a, b), w in sorted(edges.items()))
    q = (f"Directed weighted graph on nodes A..H. Edges as from->to(weight): {elist}. "
         "Find the shortest-path distance from A to H and the number of distinct shortest paths from A to H. Answer as 'distance,count'.")
    return dict(id="R5", cat="graph", q=q, ans=f"{dist[7]},{cnt[7]}")

def gen_count(rng):
    m = rng.choice([3, 4, 5, 7])
    c = sum(1 for comb in itertools.combinations(range(1, 10), 5) if sum(comb) % m == 0)
    q = f"How many 5-digit positive integers have strictly increasing digits (each digit larger than the one to its left, no digit 0) and a digit sum divisible by {m}?"
    return dict(id="R6", cat="counting", q=q, ans=str(c))

def gen_modpow(rng):
    b, e = rng.choice([3, 7, 11, 13, 17]), rng.randint(500, 3000)
    return dict(id="R7", cat="number", q=f"Compute {b}^{e} mod 1000 (the last three digits of {b}^{e}). Give the number without leading zeros.", ans=str(pow(b, e, 1000)))

def gen_sql(rng):
    depts = ["Sales", "Engineering", "Support", "Finance"]
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jun", "Kai", "Lou"]
    rows = []
    for i, nm in enumerate(names, 1):
        rows.append((i, nm, rng.randint(1, 4), rng.randint(40, 160) * 1000, f"{rng.randint(2016, 2024)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}"))
    con = sqlite3.connect(":memory:"); cur = con.cursor()
    cur.execute("CREATE TABLE departments(id INTEGER, name TEXT)")
    cur.executemany("INSERT INTO departments VALUES (?,?)", list(enumerate(depts, 1)))
    cur.execute("CREATE TABLE employees(id INTEGER, name TEXT, dept_id INTEGER, salary INTEGER, hired TEXT)")
    cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?)", rows)
    sql = ("SELECT d.name, COUNT(*) AS c, MAX(e.salary) AS mx FROM employees e JOIN departments d ON e.dept_id = d.id "
           "WHERE e.hired >= '2020-01-01' GROUP BY d.name HAVING COUNT(*) >= 2 ORDER BY mx DESC, d.name ASC")
    res = cur.execute(sql).fetchall()
    tbl = "\n".join(f"({r[0]}, '{r[1]}', {r[2]}, {r[3]}, '{r[4]}')" for r in rows)
    q = ("Tables:\ndepartments(id, name): " + ", ".join(f"({i}, '{d}')" for i, d in enumerate(depts, 1)) +
         "\nemployees(id, name, dept_id, salary, hired):\n" + tbl + f"\n\nQuery:\n{sql}\n\nGive the exact result rows as a JSON array of arrays, e.g. [[\"Sales\", 3, 120000], ...]. Use [] if empty.")
    return dict(id="R8", cat="sql", q=q, ans=json.dumps([list(r) for r in res]), kind="json")

def gen_python(rng):
    N, K, M, V = rng.randint(3, 6), rng.randint(2, 9), rng.randint(10, 99), rng.uniform(1, 9)
    V = round(V, 3)
    if int(round(V * 1000)) % 10 in (5, 0): V = round(V + 0.002, 3)  # avoid .xx5 float-rounding ambiguity in the {:.2f} format
    code = f'''def f(x, acc=[]):
    acc.append(x)
    return sum(acc)
r = [f(i) for i in range(1, {N}+1)]
fs = [lambda y, i=i: y*i for i in range(3)]
g = [lambda y: y+i for i in range(3)]
a = [{K}]*3; a[0] += 1
s = "{{:>5}}|{{:<3}}|{{:.2f}}".format({M}, "ab", {V:.3f})
print(r[-1], [h(2) for h in fs], [h(1) for h in g], a, s, 7//-2, -7%3, 2**3**2 % 1000, sep=" ; ")'''
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout.strip()
    q = "What exactly does this Python 3 program print (single line)?\n\n```python\n" + code + "\n```"
    return dict(id="R9", cat="code", q=q, ans=out)

def gen_js(rng):
    labels = list("ABCDEFGHJK"); rng.shuffle(labels)
    L = labels
    code = f'''console.log('{L[0]}');
setTimeout(() => {{ console.log('{L[1]}'); Promise.resolve().then(() => console.log('{L[2]}')); }}, 0);
const p = Promise.resolve().then(() => {{ console.log('{L[3]}'); return {{ then(res) {{ console.log('{L[4]}'); res(); }} }}; }});
p.then(() => console.log('{L[5]}'));
queueMicrotask(() => {{ console.log('{L[6]}'); queueMicrotask(() => console.log('{L[7]}')); }});
(async () => {{ await null; console.log('{L[8]}'); await p; console.log('{L[9]}'); }})();
console.log('Z');'''
    out = subprocess.run(["node", "-e", code + "\nsetTimeout(()=>{},5);"], capture_output=True, text=True).stdout.split()
    q = "In Node.js 22 (same semantics as a modern browser for this code), what is the exact order of console.log output? Answer as a JSON array of strings.\n\n```js\n" + code + "\n```"
    return dict(id="R10", cat="event-loop", q=q, ans=json.dumps(out), kind="json")

def gen_knights(rng):
    names = ["Ada", "Bo", "Cy", "Di", "Ed"]
    while True:
        truth = {n: rng.random() < 0.5 for n in names}
        stmts = []
        for n in names:
            others = [o for o in names if o != n]
            t = rng.choice(["is", "both", "atleast", "same"])
            if t == "is":
                o = rng.choice(others); kind = rng.choice([True, False])
                stmts.append((n, f"{o} is a {'knight' if kind else 'knave'}.", lambda a, o=o, kind=kind: a[o] == kind))
            elif t == "both":
                o1, o2 = rng.sample(others, 2)
                stmts.append((n, f"{o1} and {o2} are both knights.", lambda a, o1=o1, o2=o2: a[o1] and a[o2]))
            elif t == "atleast":
                o1, o2 = rng.sample(others, 2)
                stmts.append((n, f"At least one of {o1} and {o2} is a knave.", lambda a, o1=o1, o2=o2: (not a[o1]) or (not a[o2])))
            else:
                o = rng.choice(others)
                stmts.append((n, f"I am the same type as {o}.", lambda a, n=n, o=o: a[n] == a[o]))
        sols = []
        for bits in itertools.product([True, False], repeat=5):
            a = dict(zip(names, bits))
            if all(a[n] == f(a) for n, _, f in stmts): sols.append(a)
        if len(sols) == 1: break
    sol = sols[0]
    knights = sorted(n for n in names if sol[n])
    q = ("On an island every person is a knight (always tells the truth) or a knave (always lies). Five people: " + ", ".join(names) + ".\n" +
         "\n".join(f"{n} says: \"{s}\"" for n, s, _ in stmts) + "\nWho are the knights? List their names in alphabetical order, comma-separated, or NONE.")
    return dict(id="R11", cat="logic", q=q, ans=", ".join(knights) if knights else "NONE")

def gen_recur(rng):
    a1, a2, p, q_, N = rng.randint(1, 50), rng.randint(1, 50), rng.randint(2, 5), rng.randint(2, 5), 40
    a = [None, a1, a2]
    for n in range(3, N + 1): a.append((p * a[n - 1] + q_ * a[n - 2] + n) % 1000)
    q = f"Define a(1)={a1}, a(2)={a2}, and for n>=3: a(n) = ({p}*a(n-1) + {q_}*a(n-2) + n) mod 1000. What is a({N})?"
    return dict(id="R12", cat="number", q=q, ans=str(a[N]))

# ---------------- hard tier ----------------
def gen_zebra(rng):
    colors = ["red", "blue", "green", "white"]; pets = ["dog", "cat", "fish", "bird"]; drinks = ["tea", "milk", "juice", "water"]
    def solve(clues):
        sols = []
        for pc in itertools.permutations(colors):
            for pp in itertools.permutations(pets):
                for pd in itertools.permutations(drinks):
                    h = [dict(color=pc[i], pet=pp[i], drink=pd[i]) for i in range(4)]
                    if all(c(h) for _, c in clues): sols.append(h)
                    if len(sols) > 1: return sols
        return sols
    while True:
        sol = [dict(color=c, pet=p, drink=d) for c, p, d in zip(rng.sample(colors, 4), rng.sample(pets, 4), rng.sample(drinks, 4))]
        clues = []
        pool = []
        for i in range(4):
            for j in range(4):
                if j == i + 1:
                    pool.append((f"The {sol[i]['color']} house is immediately to the left of the {sol[j]['color']} house.", lambda h, a=sol[i]['color'], b=sol[j]['color']: any(h[k]['color'] == a and h[k+1]['color'] == b for k in range(3))))
                    pool.append((f"The person who drinks {sol[i]['drink']} lives immediately to the left of the person with the {sol[j]['pet']}.", lambda h, a=sol[i]['drink'], b=sol[j]['pet']: any(h[k]['drink'] == a and h[k+1]['pet'] == b for k in range(3))))
                if abs(i - j) == 1:
                    pool.append((f"The {sol[i]['pet']} owner lives next to the {sol[j]['color']} house.", lambda h, a=sol[i]['pet'], b=sol[j]['color']: any(h[k]['pet'] == a and h[k+1]['color'] == b or h[k]['color'] == b and h[k+1]['pet'] == a for k in range(3))))
            pool.append((f"The {sol[i]['color']} house's owner drinks {sol[i]['drink']}.", lambda h, a=sol[i]['color'], b=sol[i]['drink']: any(x['color'] == a and x['drink'] == b for x in h)))
            pool.append((f"The person with the {sol[i]['pet']} drinks {sol[i]['drink']}.", lambda h, a=sol[i]['pet'], b=sol[i]['drink']: any(x['pet'] == a and x['drink'] == b for x in h)))
            pool.append((f"House {i+1} is {sol[i]['color']}.", lambda h, i=i, a=sol[i]['color']: h[i]['color'] == a))
            pool.append((f"The {sol[i]['pet']} is not in house {[k for k in range(4) if k != i][rng.randrange(3)] + 1}." , None))
        pool = [c for c in pool if c[1] is not None]
        rng.shuffle(pool)
        for c in pool:
            clues.append(c)
            if len(solve(clues)) == 1: break
        if 5 <= len(clues) <= 9 and len(solve(clues)) == 1:
            break
    tgt = rng.choice(pets)
    house = next(i + 1 for i in range(4) if sol[i]['pet'] == tgt)
    q = ("Four houses in a row numbered 1 (leftmost) to 4 (rightmost). Each house has a distinct color (red, blue, green, white), "
         "pet (dog, cat, fish, bird) and drink (tea, milk, juice, water).\nClues:\n" + "\n".join(f"- {t}" for t, _ in clues) +
         f"\nIn which house number is the {tgt}?")
    return dict(id="H1", cat="logic", q=q, ans=str(house))

def gen_rooks(rng):
    forb = set()
    while len(forb) < 5: forb.add((rng.randint(1, 5), rng.randint(1, 5)))
    cells = [(r, c) for r in range(1, 6) for c in range(1, 6) if (r, c) not in forb]
    cnt = 0
    for comb in itertools.combinations(cells, 3):
        rs = {x[0] for x in comb}; cs = {x[1] for x in comb}
        if len(rs) == 3 and len(cs) == 3: cnt += 1
    q = (f"On a 5×5 chessboard (rows 1-5, columns 1-5) the cells {sorted(forb)} (row, column) are blocked and cannot hold a piece. "
         "In how many ways can you place 3 identical rooks on unblocked cells so that no two share a row or a column?")
    return dict(id="H2", cat="counting", q=q, ans=str(cnt))

def gen_queue(rng):
    arr = sorted(rng.randint(0, 60) for _ in range(10)); svc = [rng.randint(2, 12) for _ in range(10)]
    t = 0; total_wait = 0
    for a, s in zip(arr, svc):
        start = max(t, a); total_wait += start - a; t = start + s
    q = (f"A single clerk serves customers first-come-first-served. Arrival times (minutes): {arr}. Service times in the same order: {svc}. "
         "Service starts immediately if the clerk is free, otherwise the customer waits. What is the total waiting time (sum over all customers, in minutes) before service starts?")
    return dict(id="H3", cat="simulation", q=q, ans=str(total_wait))

def gen_poset(rng):
    els = "ABCDEFGH"
    while True:
        rel = set()
        for i in range(8):
            for j in range(i + 1, 8):
                if rng.random() < 0.28: rel.add((i, j))
        perm_pool = list(range(8)); rng.shuffle(perm_pool)
        rel = {(perm_pool[a], perm_pool[b]) for a, b in rel}
        banned = tuple(rng.sample(range(8), 2))
        cnt = 0
        for p in itertools.permutations(range(8)):
            pos = [0] * 8
            for i, x in enumerate(p): pos[x] = i
            if abs(pos[banned[0]] - pos[banned[1]]) == 1: continue
            if all(pos[a] < pos[b] for a, b in rel): cnt += 1
        if 6 <= len(rel) <= 10 and 30 <= cnt <= 3000: break
    q = ("Tasks A..H must each run once, one at a time. Constraints (X before Y): " + "; ".join(f"{els[a]} before {els[b]}" for a, b in sorted(rel)) +
         f". Additionally {els[banned[0]]} and {els[banned[1]]} must not be adjacent in the schedule. How many valid orderings exist?")
    return dict(id="H4", cat="counting", q=q, ans=str(cnt))

def gen_crypt(rng):
    letters = list("ABCDEFGHJKLMNPQRSTUVWXYZ")
    while True:
        x, y = rng.randint(1000, 9999), rng.randint(1000, 9999); z = x + y
        if z < 10000: continue
        digs = sorted(set(str(x) + str(y) + str(z)))
        if len(digs) > 8: continue
        rng.shuffle(letters); mp = {d: letters[i] for i, d in enumerate(digs)}
        W = ["".join(mp[c] for c in str(v)) for v in (x, y, z)]
        # uniqueness check
        ls = digs; L = [mp[d] for d in ls]
        sols = 0
        for perm in itertools.permutations(range(10), len(L)):
            a = dict(zip(L, perm))
            if a[W[0][0]] == 0 or a[W[1][0]] == 0 or a[W[2][0]] == 0: continue
            v = [int("".join(str(a[c]) for c in w)) for w in W]
            if v[0] + v[1] == v[2]:
                sols += 1
                if sols > 1: break
        if sols == 1: break
    q = (f"Cryptarithm: {W[0]} + {W[1]} = {W[2]}. Each letter stands for a distinct digit 0-9, no number has a leading zero, and the solution is unique. "
         f"What number does {W[2]} represent?")
    return dict(id="H5", cat="search", q=q, ans=str(z))

def gen_hamilton(rng):
    while True:
        edges = {frozenset(e) for e in itertools.combinations(range(7), 2) if rng.random() < 0.5}
        cnt = 0
        for p in itertools.permutations(range(1, 7)):
            path = (0,) + p
            if all(frozenset((path[i], path[i + 1])) in edges for i in range(6)): cnt += 1
        if 8 <= cnt <= 120: break
    names = "ABCDEFG"
    el = ", ".join("".join(sorted(names[i] for i in e)) for e in sorted(edges, key=lambda e: sorted(e)))
    q = (f"Undirected graph on vertices A..G with edges: {el}. How many Hamiltonian paths (visiting every vertex exactly once) start at vertex A? "
         "Count each sequence of vertices once.")
    return dict(id="H6", cat="counting", q=q, ans=str(cnt))


# ---------------- xhard tier (added 2026-09-10 to widen the top-end gap) ----------------
from fractions import Fraction
def gen_vm2(rng):
    """nested-loop register machine, 150-400 steps"""
    while True:
        n1, n2 = rng.randint(4, 7), rng.randint(3, 6); m1 = rng.randint(2, 4); md = rng.choice([97, 101, 103, 107]); add = rng.randint(3, 11)
        prog = [("SET", 0, n1), ("SET", 3, 0),                       # 1,2
                ("SET", 1, n2), ("SET", 2, add),                     # 3,4  inner init
                ("MUL", 2, m1), ("MOD", 2, md), ("ADDR", 3, 2),      # 5,6,7 inner body
                ("DEC", 1), ("JNZ", 1, 5),                           # 8,9 inner loop
                ("ADDR", 3, 0), ("DEC", 0), ("JNZ", 0, 3),           # 10,11,12 outer loop
                ("MOD", 3, 10000), ("HALT",)]                        # 13,14
        r, steps = run_vm(prog, limit=5000)
        if 150 <= steps <= 800: break
    lines = []
    for i, op in enumerate(prog, 1):
        if op[0] in ("SET", "ADD", "MUL", "MOD"): lines.append(f"{i}: {op[0]} r{op[1]}, {op[2]}")
        elif op[0] == "ADDR": lines.append(f"{i}: ADDR r{op[1]}, r{op[2]}")
        elif op[0] == "DEC": lines.append(f"{i}: DEC r{op[1]}")
        elif op[0] == "JNZ": lines.append(f"{i}: JNZ r{op[1]}, {op[2]}")
        else: lines.append(f"{i}: HALT")
    q = ("Same register machine as before: registers r0..r3 start at 0; SET r,v; ADD r,v; ADDR r,s (r += register s); MUL r,v; MOD r,v; DEC r; "
         "JNZ r,L (jump to line L if r != 0); HALT. Lines are 1-indexed.\nProgram:\n" + "\n".join(lines) +
         "\n\nRun it to completion (it contains a nested loop). Give the final registers as JSON {\"r0\":..,\"r1\":..,\"r2\":..,\"r3\":..}.")
    return dict(id="X1", cat="simulation", q=q, ans=json.dumps({"r0": r[0], "r1": r[1], "r2": r[2], "r3": r[3]}), kind="json")

def gen_dfa(rng):
    states = "ABCD"; alpha = "xyz"
    while True:
        tbl = {(s, c): rng.choice(states) for s in states for c in alpha}
        w = "".join(rng.choice(alpha) for _ in range(36))
        cur = "A"; visits = {s: 0 for s in states}; trace = []
        for c in w:
            cur = tbl[(cur, c)]; visits[cur] += 1; trace.append(cur)
        if min(visits.values()) >= 2 and len(set(trace[-6:])) >= 2: break
    rows = "\n".join(f"{s}: " + ", ".join(f"{c}->{tbl[(s,c)]}" for c in alpha) for s in states)
    q = (f"A deterministic automaton has states A,B,C,D (start state A) and input symbols x,y,z. Transition table (state: symbol->next):\n{rows}\n"
         f"Process the input string {w} one symbol at a time. Report the final state and how many times the automaton entered state C during processing (count each transition into C, including staying in C). Answer as 'STATE,count'.")
    return dict(id="X2", cat="simulation", q=q, ans=f"{cur},{visits['C']}")

def gen_expect(rng):
    N = rng.randint(7, 10); sides = rng.choice([4, 6])
    # E[k] = expected rolls to reach total >= N starting from sum k
    E = {}
    for k in range(N + sides, -1, -1):
        if k >= N: E[k] = Fraction(0); continue
        E[k] = 1 + sum(E[k + d] for d in range(1, sides + 1)) / sides
    ans = E[0]
    q = (f"You repeatedly roll a fair {sides}-sided die (faces 1..{sides}) and keep a running total, stopping as soon as the total is at least {N}. "
         "What is the expected number of rolls? Give the exact value as a reduced fraction p/q (or an integer).")
    return dict(id="X3", cat="probability", q=q, ans=f"{ans.numerator}/{ans.denominator}" if ans.denominator != 1 else str(ans.numerator))

def gen_runs(rng):
    L, k = 20, rng.randint(8, 12)
    cnt = 0
    for x in range(1 << L):
        if bin(x).count("1") != k: continue
        s = format(x, f"0{L}b")
        if "000" in s or "111" in s: continue
        cnt += 1
    q = f"How many binary strings of length {L} contain exactly {k} ones and have no run of three or more identical consecutive bits (no '000' and no '111')?"
    return dict(id="X4", cat="counting", q=q, ans=str(cnt))

def gen_knap(rng):
    while True:
        items = [(rng.randint(3, 15), rng.randint(10, 60)) for _ in range(9)]  # (weight, value)
        cap = rng.randint(25, 40)
        best = -1; ways = 0
        for mask in range(1 << 9):
            w = sum(items[i][0] for i in range(9) if mask >> i & 1); v = sum(items[i][1] for i in range(9) if mask >> i & 1)
            if w <= cap:
                if v > best: best, ways = v, 1
                elif v == best: ways += 1
        if ways in (2, 3): break
    lst = "; ".join(f"item{i+1}: weight {w}, value {v}" for i, (w, v) in enumerate(items))
    q = (f"0/1 knapsack. Items: {lst}. Capacity {cap} (total weight must be <= {cap}). What is the maximum total value, and how many distinct subsets of items achieve that maximum? Answer as 'value,count'.")
    return dict(id="X5", cat="optimization", q=q, ans=f"{best},{ways}")

def gen_bits(rng):
    x0 = rng.randint(0x1000, 0xFFFF); ops = []; x = x0
    catalog = [
        ("rotate left by 3 within 16 bits", lambda v: ((v << 3) | (v >> 13)) & 0xFFFF),
        ("XOR with 0x5A5A", lambda v: v ^ 0x5A5A),
        ("swap the high and low bytes", lambda v: ((v & 0xFF) << 8) | (v >> 8)),
        ("reverse the order of all 16 bits", lambda v: int(format(v, "016b")[::-1], 2)),
        ("add 0x1357 modulo 2^16", lambda v: (v + 0x1357) & 0xFFFF),
        ("clear every bit whose position (0 = least significant) is a multiple of 3", lambda v: v & ~sum(1 << i for i in range(0, 16, 3)) & 0xFFFF),
        ("rotate right by 5 within 16 bits", lambda v: ((v >> 5) | (v << 11)) & 0xFFFF),
        ("invert all 16 bits", lambda v: (~v) & 0xFFFF),
    ]
    for desc, f in rng.sample(catalog, 6): ops.append(desc); x = f(x)
    q = f"Start with the 16-bit value 0x{x0:04X}. Apply in order:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(ops)) + "\nGive the final 16-bit value in hexadecimal (4 uppercase hex digits, e.g. 0x1A2B)."
    return dict(id="X6", cat="bits", q=q, ans=f"0x{x:04X}")

def gen_schedule(rng):
    while True:
        jobs = [(rng.randint(1, 9), rng.randint(5, 30)) for _ in range(7)]  # (duration, deadline)
        best = 99; ways = 0
        for perm in itertools.permutations(range(7)):
            t = 0; late = 0
            for j in perm:
                t += jobs[j][0]
                if t > jobs[j][1]: late += 1
            if late < best: best, ways = late, 1
            elif late == best: ways += 1
        if 1 <= best <= 3 and ways < 400: break
    lst = "; ".join(f"J{i+1}: duration {d}, deadline {dl}" for i, (d, dl) in enumerate(jobs))
    q = (f"Seven jobs run one after another on a single machine starting at time 0, no idle time: {lst}. A job is late if it finishes after its deadline. "
         "What is the minimum possible number of late jobs, and how many of the 7! orderings achieve that minimum? Answer as 'late,orderings'.")
    return dict(id="X7", cat="optimization", q=q, ans=f"{best},{ways}")

# ---------------- elite additions (2026-09-10): more top-end resolution ----------------
def gen_poset9(rng):
    els = "ABCDEFGHI"
    while True:
        rel = set()
        for i in range(9):
            for j in range(i + 1, 9):
                if rng.random() < 0.22: rel.add((i, j))
        perm_pool = list(range(9)); rng.shuffle(perm_pool)
        rel = {(perm_pool[a], perm_pool[b]) for a, b in rel}
        bans = [tuple(rng.sample(range(9), 2)), tuple(rng.sample(range(9), 2))]
        if set(bans[0]) == set(bans[1]) or not (7 <= len(rel) <= 11): continue
        cnt = 0
        for pm in itertools.permutations(range(9)):
            pos = [0] * 9
            for i, x in enumerate(pm): pos[x] = i
            if abs(pos[bans[0][0]] - pos[bans[0][1]]) == 1 or abs(pos[bans[1][0]] - pos[bans[1][1]]) == 1: continue
            ok = True
            for a, b in rel:
                if pos[a] > pos[b]: ok = False; break
            if ok: cnt += 1
        if 50 <= cnt <= 5000: break
    q = ("Tasks A..I must each run once, one at a time. Constraints (X before Y): " + "; ".join(f"{els[a]} before {els[b]}" for a, b in sorted(rel)) +
         f". Additionally {els[bans[0][0]]} and {els[bans[0][1]]} must not be adjacent, and {els[bans[1][0]]} and {els[bans[1][1]]} must not be adjacent. How many valid orderings exist?")
    return dict(id="X8", cat="counting", q=q, ans=str(cnt))

def gen_hitting(rng):
    from fractions import Fraction
    while True:
        n = 6; edges = {frozenset(e) for e in itertools.combinations(range(n), 2) if rng.random() < 0.45}
        adj = {v: sorted({x for e in edges for x in e if v in e and x != v}) for v in range(n)}
        if any(not adj[v] for v in range(n)): continue
        seen = {0}; st = [0]
        while st:
            v = st.pop()
            for u in adj[v]:
                if u not in seen: seen.add(u); st.append(u)
        if len(seen) < n: continue
        s_, t = rng.sample(range(n), 2)
        idx = [v for v in range(n) if v != t]; m = len(idx); pos = {v: i for i, v in enumerate(idx)}
        A = [[Fraction(0)] * m for _ in range(m)]; b = [Fraction(1)] * m
        for v in idx:
            i = pos[v]; A[i][i] += 1
            for u in adj[v]:
                if u != t: A[i][pos[u]] -= Fraction(1, len(adj[v]))
        for c in range(m):
            piv = next(r for r in range(c, m) if A[r][c] != 0)
            A[c], A[piv] = A[piv], A[c]; b[c], b[piv] = b[piv], b[c]
            for r in range(m):
                if r != c and A[r][c] != 0:
                    f = A[r][c] / A[c][c]
                    A[r] = [x - f * y for x, y in zip(A[r], A[c])]; b[r] -= f * b[c]
        E = b[pos[s_]] / A[pos[s_]][pos[s_]]
        if 3 <= len(edges) <= 9 and E.denominator <= 5000 and E > 2: break
    names = "ABCDEF"
    el = ", ".join("".join(sorted(names[i] for i in e)) for e in sorted(edges, key=lambda e: sorted(e)))
    q = (f"A token performs a simple random walk on the undirected graph with vertices A..F and edges {el}: at each step it moves to a uniformly random neighbour. "
         f"Starting at {names[s_]}, what is the expected number of steps until it first reaches {names[t]}? Give the exact value as a reduced fraction p/q (or an integer).")
    return dict(id="X9", cat="probability", q=q, ans=f"{E.numerator}/{E.denominator}" if E.denominator != 1 else str(E.numerator))

def gen_gridpaths(rng):
    N = 6
    while True:
        blocked = set()
        while len(blocked) < 4:
            c = (rng.randint(1, N), rng.randint(1, N))
            if c not in ((1, 1), (N, N)): blocked.add(c)
        via = (rng.randint(2, N - 1), rng.randint(2, N - 1))
        if via in blocked: continue
        def paths(a, bb):
            (r0, c0), (r1, c1) = a, bb
            if r1 < r0 or c1 < c0: return 0
            dp = {}
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if (r, c) in blocked: dp[(r, c)] = 0; continue
                    if (r, c) == (r0, c0): dp[(r, c)] = 1; continue
                    dp[(r, c)] = dp.get((r - 1, c), 0) + dp.get((r, c - 1), 0)
            return dp[(r1, c1)]
        total = paths((1, 1), via) * paths(via, (N, N))
        if 10 <= total <= 400: break
    q = (f"On a {N}x{N} grid of cells (row, column) numbered 1..{N} from the top-left, you move only right or down one cell at a time from (1,1) to ({N},{N}). "
         f"Cells {sorted(blocked)} are blocked and cannot be entered. How many such paths pass through cell {via}?")
    return dict(id="X10", cat="counting", q=q, ans=str(total))

def gen_sqlwindow(rng):
    depts = ["Sales", "Eng", "Ops"]
    names = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jun", "Kai", "Lou", "Mia", "Ned"]
    while True:
        rows = [(i, nm, rng.choice(depts), rng.choice([50, 60, 70, 80, 90, 100]) * 1000) for i, nm in enumerate(names, 1)]
        con = sqlite3.connect(":memory:"); cur = con.cursor()
        cur.execute("CREATE TABLE employees(id INTEGER, name TEXT, dept TEXT, salary INTEGER)")
        cur.executemany("INSERT INTO employees VALUES (?,?,?,?)", rows)
        sql = ("SELECT name FROM (SELECT name, dept, DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rk FROM employees) "
               "WHERE rk = 2 ORDER BY name")
        res = [r[0] for r in cur.execute(sql).fetchall()]
        if 2 <= len(res) <= 6: break
    tbl = ", ".join(f"({r[0]}, '{r[1]}', '{r[2]}', {r[3]})" for r in rows)
    q = (f"Table employees(id, name, dept, salary) contains: {tbl}.\nQuery:\n{sql}\n\nDENSE_RANK gives equal salaries the same rank with no gaps. "
         "Give the exact result as a JSON array of names, e.g. [\"Ana\", \"Ben\"].")
    return dict(id="X11", cat="sql", q=q, ans=json.dumps(res), kind="json")

def gen_pipeline16(rng):
    s16 = norm_alnum(rng, 16)
    def rot13(x): return x.translate(str.maketrans(string.ascii_lowercase + string.ascii_uppercase, string.ascii_lowercase[13:] + string.ascii_lowercase[:13] + string.ascii_uppercase[13:] + string.ascii_uppercase[:13]))
    catalog = [
        ("reverse the string", lambda x: x[::-1]),
        ("apply ROT13 to letters (digits unchanged)", rot13),
        ("convert letters to uppercase", lambda x: x.upper()),
        ("delete every vowel (a,e,i,o,u in either case)", lambda x: "".join(c for c in x if c.lower() not in "aeiou")),
        ("keep only characters at even 0-based indices", lambda x: x[0::2]),
        ("move the first three characters to the end", lambda x: x[3:] + x[:3]),
        ("replace every digit d with (9-d)", lambda x: "".join(str(9 - int(c)) if c.isdigit() else c for c in x)),
        ("append the count of digits in the current string as a decimal number", lambda x: x + str(sum(c.isdigit() for c in x))),
        ("swap each adjacent pair of characters (0<->1, 2<->3, ...; an unpaired last char stays)", lambda x: "".join(x[i + 1] + x[i] if i + 1 < len(x) else x[i] for i in range(0, len(x), 2))),
        ("sort the characters in ascending ASCII order", lambda x: "".join(sorted(x))),
        ("delete the middle character if the length is odd, otherwise delete the last character", lambda x: (x[:len(x)//2] + x[len(x)//2 + 1:]) if len(x) % 2 else x[:-1]),
        ("duplicate every character that is a digit", lambda x: "".join(c * 2 if c.isdigit() else c for c in x)),
    ]
    chosen = rng.sample(catalog, 10); cur = s16; ops = []
    for d, f in chosen: ops.append(d); cur = f(cur)
    q = f"Start with the string: {s16}\nApply these operations in order:\n" + "\n".join(f"{i+1}. {d}" for i, d in enumerate(ops)) + "\nWhat is the final string?"
    return dict(id="X12", cat="string", q=q, ans=cur)

def gen_js2(rng):
    L = list("ABCDEFGHJKLMN"); rng.shuffle(L)
    lines = [
        "console.log('%s');" % L[0],
        "setTimeout(() => { console.log('%s'); Promise.resolve().then(() => console.log('%s')); }, 0);" % (L[1], L[2]),
        "const th = { then(res) { console.log('%s'); res('%s'); } };" % (L[3], L[4]),
        "const p = Promise.resolve(th);",
        "p.then(v => { console.log(v); return new Promise(r => { console.log('%s'); r(); }); }).then(() => console.log('%s'));" % (L[5], L[6]),
        "(async () => { console.log('%s'); await p; console.log('%s'); await null; console.log('%s'); })();" % (L[7], L[8], L[9]),
        "Promise.resolve().then(() => console.log('%s')).finally(() => console.log('%s'));" % (L[10], L[11]),
        "queueMicrotask(() => console.log('%s'));" % L[12],
        "console.log('Z');",
    ]
    code = "\n".join(lines)
    out = subprocess.run(["node", "-e", code + "\nsetTimeout(()=>{},5);"], capture_output=True, text=True).stdout.split()
    q = "In Node.js 22, what is the exact order of console.log output? Answer as a JSON array of strings.\n\n```js\n" + code + "\n```"
    return dict(id="X13", cat="event-loop", q=q, ans=json.dumps(out), kind="json")

def gen_fletcher(rng):
    data = [rng.randint(1, 254) for _ in range(8)]
    s1 = s2 = 0
    for b in data:
        s1 = (s1 + b) % 255; s2 = (s2 + s1) % 255
    val = (s2 << 8) | s1
    q = (f"Compute the Fletcher-16 checksum of the byte sequence {data} (decimal bytes, processed left to right): start with sum1 = 0 and sum2 = 0; "
         "for each byte b do sum1 = (sum1 + b) mod 255, then sum2 = (sum2 + sum1) mod 255. The checksum is (sum2 << 8) | sum1. "
         "Give it as a 4-digit uppercase hexadecimal number, e.g. 0x1A2B.")
    return dict(id="X14", cat="bits", q=q, ans=f"0x{val:04X}")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=20260909); ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "suite", "iq.json"))
    a = ap.parse_args(); rng = random.Random(a.seed)
    items = []
    for it in gen_direct(rng): it["tier"] = "direct"; items.append(it)
    for g in (gen_vm, gen_ca, gen_pipeline, gen_josephus, gen_graph, gen_count, gen_modpow, gen_sql, gen_python, gen_js, gen_knights, gen_recur):
        it = g(rng); it["tier"] = "reason"; items.append(it)
    for g in (gen_zebra, gen_rooks, gen_queue, gen_poset, gen_crypt, gen_hamilton):
        it = g(rng); it["tier"] = "hard"; items.append(it)
    for g in (gen_vm2, gen_dfa, gen_expect, gen_runs, gen_knap, gen_bits, gen_schedule, gen_poset9, gen_hitting, gen_gridpaths, gen_sqlwindow, gen_pipeline16, gen_js2, gen_fletcher):
        it = g(rng); it["tier"] = "xhard"; items.append(it)
    # curated bank: keep only items proven to discriminate (suite/iq_keep.json); the full bank is saved alongside
    json.dump(dict(seed=a.seed, items=items), open(a.out.replace(".json", "_full.json"), "w"), indent=1, ensure_ascii=False)
    keep_path = os.path.join(os.path.dirname(a.out), "iq_keep.json")
    if os.path.exists(keep_path):
        keep = set(json.load(open(keep_path)))
        items = [it for it in items if it["id"] in keep]
    json.dump(dict(seed=a.seed, items=items), open(a.out, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {len(items)} items to {a.out}")
    for it in items: print(it["tier"], it["id"], it["cat"], "->", it["ans"][:60])

if __name__ == "__main__":
    main()
