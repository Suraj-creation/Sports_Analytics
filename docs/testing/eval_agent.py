import urllib.request
import json
import time

SID = "01M4FQFS8KBDFXSQ228MD18S6W"
questions = [
    ("Q1_Overview", "Summarize this match: who are the players, what is the score, and how many rallies were played?"),
    ("Q2_Smashes", "How many smashes and winners did P1 hit compared to P2?"),
    ("Q3_LongestRally", "What was the longest rally of the match, who won it, and what strokes were played in that rally?"),
    ("Q4_Warmup_Adv", "How many official points were scored during the players pre-match warm-up?"),
    ("Q5_Rally50_Adv", "Who won the 50th rally of this match?"),
    ("Q6_Hallucination_Adv", "What brand of racket was used and how fast was the top smash in km/h?"),
    ("Q7_Game3_Adv", "Who won game 3 of this match?")
]

results = {}
for qid, q in questions:
    print(f"\n--- Running {qid} ---")
    t0 = time.time()
    data = json.dumps({"question": q, "history": []}).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:8000/api/sessions/{SID}/ask",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            dt = time.time() - t0
            res["elapsed_s"] = round(dt, 2)
            results[qid] = res
            tools = [t["tool"] for t in res.get("tool_trace", [])]
            print(f"Elapsed: {res['elapsed_s']}s")
            print(f"Grounded: {res.get('grounded')}")
            print(f"Tools called: {tools}")
            print(f"Citations count: {len(res.get('citations', []))}")
            print(f"Issues: {res.get('issues', [])}")
            ans = res.get("text", "")
            print(f"Answer snippet: {ans[:200]}...")
    except Exception as e:
        print(f"Error on {qid}: {e}")

with open("docs/testing/agent_evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved agent evaluation results to docs/testing/agent_evaluation_results.json")
