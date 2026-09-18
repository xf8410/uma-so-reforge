#!/usr/bin/env python3
"""686 全量偏移 dump 流水线（uma-so-reforge v3.29.0+）

前置：游戏内已注入 libhachimi_ura.so v3.29.0+，进入育成主界面（IL2CPP 已初始化）。
用法（在能访问手机 18765 端口的环境跑）：
  adb forward tcp:18765 tcp:18765 && python3 dump_pipeline.py --out ./dump686
  或手机 Termux 直接: python3 dump_pipeline.py
产物：dump_offsets_meta.json + offsets_<A-Z>.json（每个类：字段偏移 + 方法运行时地址 + token）
"""
import argparse, json, sys, time, urllib.request
from pathlib import Path

def get(base, path, retries=3, timeout=120):
    url = base.rstrip("/") + path
    last = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"GET {url} failed: {last}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:18765")
    ap.add_argument("--out", default="./dump686")
    ap.add_argument("--letters", default="", help="只dump指定字母，如 GRS；空=全部")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    health = get(args.base, "/health")
    print("health:", json.dumps(health, ensure_ascii=False)[:200])
    meta = get(args.base, "/il2cpp/dump_offsets_meta")
    if not meta.get("ok"):
        sys.exit(f"meta failed: {meta}")
    (out / "dump_offsets_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    letters = meta["letters"]
    print(f"image={meta['image']} class_count={meta['class_count']}")

    todo = [l for l in args.letters.upper()] if args.letters else [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if letters.get(l)]
    summary = {}
    for idx, letter in enumerate(todo, 1):
        t0 = time.time()
        data = get(args.base, f"/il2cpp/dump_offsets?letter={letter}", timeout=600)
        ok = bool(data.get("ok"))
        n = data.get("class_count", 0)
        summary[letter] = {"ok": ok, "classes": n}
        if ok:
            (out / f"offsets_{letter}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        print(f"[{idx}/{len(todo)}] letter={letter} classes={n} ok={ok} {time.time()-t0:.1f}s")
    (out / "pipeline_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [l for l, v in summary.items() if not v["ok"]]
    print("DONE" if not bad else f"FAILED_LETTERS={bad}")

if __name__ == "__main__":
    main()
