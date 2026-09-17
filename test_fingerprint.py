"""Checks for the ModelTrace fingerprint group (bench.py) and its REPORT.md rendering (report.py).

  ../.venvs/relay-bench/bin/python test_fingerprint.py

No network and no API spend: a fake runner covers every verdict; the end-to-end case uses the
real runner + ModelTrace maths against a local fake relay (skipped if ModelTrace is not installed).
"""
import http.server, importlib, json, os, random, re, subprocess, sys, tempfile, threading, types, unittest, warnings

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
bench = importlib.import_module("bench")
report = importlib.import_module("report")
KEY = "sk-fixture-fingerprint-0123456789abcdef"

FAKE_RUNNER = r'''
import json, os, sys
a = sys.argv[1:]; flag = lambda n: a[a.index(n) + 1]
out = flag("--out"); os.makedirs(out, exist_ok=True)
json.dump({"argv": a, "key": os.environ.get("MT_API_KEY")}, open(os.path.join(out, "seen.json"), "w"))
s = json.loads(os.environ["FAKE_SUMMARY"]); s.setdefault("claimed", flag("--model"))
json.dump(s, open(os.path.join(out, "modeltrace-summary.json"), "w"))
json.dump({**s, "attempts": [{"accepted": True, "parsed": 300}]}, open(os.path.join(out, "modeltrace.json"), "w"))
sys.exit(0 if s.get("ok") else 2)
'''

def summary(code, top, p, family="claude", family_p=1.0, weak=False, ok=True, received=3):
    labels = {"match": "指纹一致", "version_mismatch": "同家族·版本不符", "family_mismatch": "家族不符", "out_of_bank": "库外型号", "inconclusive": "样本不足"}
    return {"ok": ok, "verdict": {"code": code, "label": labels[code], "weak": weak}, "top_model": top, "top_probability": p,
            "family": family, "family_name": family.title(), "family_probability": family_p,
            "ranking": [{"model": top, "p": p}] if top else [], "received": received, "target": 3, "attempted": 3, "seconds": 1.0, "errors": []}


class Group(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", ResourceWarning)  # bench.py reads JSON with bare open(), like the rest of the file
        self.tmp = tempfile.mkdtemp(prefix="rb-fp-")
        self.engine = os.path.join(self.tmp, "modeltrace"); os.makedirs(os.path.join(self.engine, "data"))
        open(os.path.join(self.engine, "data", "unified_bank.json"), "w").write("{}")
        self.runner = os.path.join(self.tmp, "run.py"); open(self.runner, "w").write(FAKE_RUNNER)
        self.env = {"MODELTRACE_DIR": self.engine, "MODELTRACE_PYTHON": sys.executable, "MODELTRACE_RUNNER": self.runner}
        self.saved = {k: os.environ.get(k) for k in list(self.env) + ["FAKE_SUMMARY", "RELAY_BENCH_NO_FINGERPRINT"]}
        os.environ.update(self.env); os.environ.pop("RELAY_BENCH_NO_FINGERPRINT", None)

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v

    def run_group(self, s, model="claude-opus-5", dialect="anthropic"):
        os.environ["FAKE_SUMMARY"] = json.dumps(s)
        b = bench.Bench(bench.Channel("https://relay.invalid", KEY, dialect, model), "fp-test", "screen",
                        types.SimpleNamespace(out=self.tmp, concurrency=1))
        b.g_fingerprint()
        return b

    def status(self, b):
        return [f["status"] for f in b.findings if f["group"] == "fingerprint"]

    def as_report_row(self, b):
        return {"meta": {"label": "fp-test", "model": b.ch.model, "dialect": b.ch.dialect, "expect_key": b.exp_key},
                "metrics": b.metrics, "findings": b.findings, "extra": b.extra}

    def test_match_passes_and_raises_no_flag(self):
        b = self.run_group(summary("match", "claude-opus-5", 0.996))
        self.assertEqual(self.status(b), ["PASS"])
        self.assertEqual(b.metrics["fingerprint_top"], "claude-opus-5")
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertFalse([f for f in flags if "指纹" in f])
        self.assertEqual(report.fp_cell(b.metrics), "claude-opus-5 100%")

    def test_confident_version_mismatch_is_an_ordinary_flag_not_fake(self):
        b = self.run_group(summary("version_mismatch", "claude-haiku-4-5-20251001", 0.953))
        self.assertEqual(self.status(b), ["WARN"])
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertTrue(any("版本不符" in f and "疑似降级" in f for f in flags))
        self.assertNotEqual(sev, "FAKE/ALTERED", "a version mismatch alone must not declare a fake")
        self.assertEqual(report.fp_cell(b.metrics), "claude-haiku-4-5-20251001 95%·版本不符")

    def test_low_confidence_version_mismatch_is_not_a_flag(self):
        b = self.run_group(summary("version_mismatch", "claude-opus-4-8", 0.55))
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertFalse([f for f in flags if "指纹" in f])

    def test_confident_family_mismatch_fails_and_marks_fake_mapping(self):
        b = self.run_group(summary("family_mismatch", "gpt-5.4", 0.95, family="gpt", family_p=0.99))
        self.assertEqual(self.status(b), ["FAIL"])
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertEqual(sev, "FAKE/ALTERED")
        self.assertTrue(any("家族不符" in f and "假映射" in f for f in flags))

    def test_weak_family_mismatch_is_only_a_warning(self):
        b = self.run_group(summary("family_mismatch", "gpt-5.4", 0.6, family="gpt", family_p=0.7, weak=True))
        self.assertEqual(self.status(b), ["WARN"])
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertFalse(any("假映射" in f for f in flags))

    def test_inconclusive_never_attributes(self):
        s = summary("inconclusive", "gpt-5.6-sol", 0.63, ok=False, received=1); s["errors"] = ["有效数字不足：0/167"]
        b = self.run_group(s)
        self.assertEqual(self.status(b), ["WARN"])
        self.assertIn("样本不足", b.findings[-1]["detail"])
        self.assertEqual(report.fp_cell(b.metrics), "样本不足")
        sev, flags = report.verdict(self.as_report_row(b))
        self.assertFalse([f for f in flags if "指纹" in f])

    def test_key_travels_by_env_only(self):
        b = self.run_group(summary("match", "claude-opus-5", 0.99))
        seen = json.load(open(os.path.join(self.tmp, "fp-test", "claude-opus-5.modeltrace", "seen.json")))
        self.assertEqual(seen["key"], KEY)
        self.assertNotIn(KEY, " ".join(seen["argv"]))
        self.assertEqual(seen["argv"][seen["argv"].index("--format") + 1], "anthropic")

    def test_opt_out_and_missing_engine_skip_cleanly(self):
        os.environ["RELAY_BENCH_NO_FINGERPRINT"] = "1"
        b = self.run_group(summary("match", "claude-opus-5", 0.99))
        self.assertEqual(self.status(b), ["INFO"]); self.assertNotIn("fingerprint_verdict", b.metrics)
        os.environ.pop("RELAY_BENCH_NO_FINGERPRINT")
        os.environ["MODELTRACE_DIR"] = os.path.join(self.tmp, "nope")
        b = self.run_group(summary("match", "claude-opus-5", 0.99))
        self.assertEqual(self.status(b), ["INFO"]); self.assertIn("not installed", b.findings[-1]["detail"])

    def test_models_outside_the_bank_families_are_skipped_without_calls(self):
        for model, dialect in (("glm-5.3-flash", "openai"), ("DeepSeek-V4.1-Flash", "openai"), ("kimi-k3", "openai")):
            b = self.run_group(summary("out_of_bank", "gpt-5.4", 0.6), model=model, dialect=dialect)
            self.assertEqual(self.status(b), ["INFO"], model)
            self.assertIn("only has GPT and Claude", b.findings[-1]["detail"])
            self.assertNotIn("fingerprint_verdict", b.metrics)
            self.assertFalse(os.path.exists(os.path.join(self.tmp, "fp-test", re.sub(r"[^A-Za-z0-9._-]", "_", model) + ".modeltrace", "seen.json")),
                             f"{model}: the runner must not be started")
        for model in ("gpt-6-astra", "claude-opus-5", "anthropic/claude-sonnet-5", "o3"):
            b = self.run_group(summary("match", model, 0.99), model=model)
            self.assertIn("fingerprint_verdict", b.metrics, model)

    def test_conflict_with_knowledge_is_called_out_in_the_report(self):
        b = self.run_group(summary("match", "claude-opus-5", 0.99))
        row = self.as_report_row(b); row["metrics"]["knowledge_verdict"] = "older"
        path = os.path.join(self.tmp, "rep"); os.makedirs(os.path.join(path, "fp-test"))
        json.dump(row, open(os.path.join(path, "fp-test", "claude-opus-5.json"), "w"), ensure_ascii=False)
        out = os.path.join(self.tmp, "REPORT.md")
        subprocess.run([sys.executable, os.path.join(HERE, "report.py"), path], env={**os.environ, "REPORT_OUT": out},
                       check=True, capture_output=True, text=True)
        txt = open(out).read()
        self.assertIn("指纹归属", txt)
        self.assertIn("证据冲突", txt)


class Relay(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        self.rfile.read(int(self.headers["Content-Length"]))
        text = " ".join(str(random.randint(1, 355)) for _ in range(320))
        body = ({"id": "msg_x", "type": "message", "stop_reason": "end_turn", "content": [{"type": "text", "text": text}]}
                if self.path.endswith("/messages") else {"id": "c", "choices": [{"finish_reason": "stop", "message": {"content": text}}]})
        raw = json.dumps(body).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(raw)))
        self.end_headers(); self.wfile.write(raw)


ENGINE = os.path.abspath(os.path.join(HERE, "..", "relay-collab", "engines", "modeltrace"))

@unittest.skipUnless(os.path.exists(os.path.join(ENGINE, ".venv", "bin", "python")), "ModelTrace not installed next to relay-bench")
class EndToEnd(unittest.TestCase):
    def test_bench_cli_runs_the_real_runner_and_report_shows_it(self):
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Relay)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        out = tempfile.mkdtemp(prefix="rb-fp-e2e-")
        env = {k: v for k, v in os.environ.items() if not k.startswith(("MODELTRACE_", "FAKE_SUMMARY", "RELAY_BENCH_NO"))}
        try:
            r = subprocess.run([sys.executable, os.path.join(HERE, "bench.py"), "--label", "e2e", "--base", f"http://127.0.0.1:{srv.server_address[1]}",
                                "--key", "sk-e2e", "--models", "claude-opus-5", "--only", "fingerprint", "--out", out],
                               env=env, capture_output=True, text=True, timeout=180)
        finally:
            srv.shutdown()
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        res = json.load(open(os.path.join(out, "e2e", "claude-opus-5.fingerprint.json")))
        self.assertIn(res["metrics"]["fingerprint_verdict"], ("match", "version_mismatch", "family_mismatch"))
        self.assertEqual(res["metrics"]["fingerprint_received"], 3)
        self.assertEqual(len(res["extra"]["fingerprint"]["attempts"]), 3)
        rep = os.path.join(out, "REPORT.md")
        subprocess.run([sys.executable, os.path.join(HERE, "report.py"), out], env={**env, "REPORT_OUT": rep}, check=True, capture_output=True)
        self.assertIn("数字指纹(ModelTrace", open(rep).read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
