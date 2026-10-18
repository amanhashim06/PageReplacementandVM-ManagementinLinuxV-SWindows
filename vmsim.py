import random
import sys
from collections import OrderedDict, deque

SEED = 42
N_REFS = 20000
FRAMES = [10, 20, 30, 40, 50, 60, 80]


def fifo(tr, n):
    mem = set()
    q = deque()
    faults = 0
    for p in tr:
        if p not in mem:
            faults += 1
            if len(mem) >= n:
                mem.remove(q.popleft())
            mem.add(p)
            q.append(p)
    return faults


def lru(tr, n):
    mem = OrderedDict()
    faults = 0
    for p in tr:
        if p in mem:
            mem.move_to_end(p)
        else:
            faults += 1
            if len(mem) >= n:
                mem.popitem(last=False)
            mem[p] = 1
    return faults


def clock(tr, n):
    frames = [None] * n
    ref = [0] * n
    where = {}
    hand = 0
    faults = 0
    for p in tr:
        if p in where:
            ref[where[p]] = 1
            continue
        faults += 1
        while frames[hand] is not None and ref[hand]:
            ref[hand] = 0
            hand = (hand + 1) % n
        if frames[hand] is not None:
            del where[frames[hand]]
        frames[hand] = p
        ref[hand] = 1
        where[p] = hand
        hand = (hand + 1) % n
    return faults


def optimal(tr, n):
    nxt = {}
    nxt_use = [0] * len(tr)
    for i in range(len(tr) - 1, -1, -1):
        nxt_use[i] = nxt.get(tr[i], float("inf"))
        nxt[tr[i]] = i
    mem = {}
    faults = 0
    for i, p in enumerate(tr):
        if p in mem:
            mem[p] = nxt_use[i]
            continue
        faults += 1
        if len(mem) >= n:
            victim = max(mem, key=mem.get)
            del mem[victim]
        mem[p] = nxt_use[i]
    return faults


def linux_model(tr, n):
    act = OrderedDict()
    ina = OrderedDict()
    f = 0
    amax = n // 2
    for p in tr:
        if p in act:
            act.move_to_end(p)
        elif p in ina:
            del ina[p]
            act[p] = 1
            if len(act) > amax:
                k, _ = act.popitem(last=False)
                ina[k] = 1
        else:
            f += 1
            if len(act) + len(ina) >= n:
                if ina:
                    ina.popitem(last=False)
                else:
                    act.popitem(last=False)
            ina[p] = 1
    return f


def windows_model(tr, n, ws_frac=0.7):
    w = max(1, int(n * ws_frac))
    s = n - w
    ws = OrderedDict()
    sb = OrderedDict()
    hard = soft = 0
    for p in tr:
        if p in ws:
            continue
        if p in sb:
            soft += 1
            del sb[p]
        else:
            hard += 1
        if len(ws) >= w:
            k, _ = ws.popitem(last=False)
            if s > 0:
                sb[k] = 1
                if len(sb) > s:
                    sb.popitem(last=False)
        ws[p] = 1
    return hard, soft


def sequential_loop(rng):
    return [i % 60 for i in range(N_REFS)]


def locality(rng):
    return [rng.randrange(20) if rng.random() < 0.85 else 20 + rng.randrange(180) for _ in range(N_REFS)]


def uniform(rng):
    return [rng.randrange(100) for _ in range(N_REFS)]


def hot_scan(rng):
    tr = []
    k = 0
    while len(tr) < N_REFS:
        tr += [rng.randrange(30) for _ in range(60)]
        for _ in range(40):
            tr.append(30 + k % 500)
            k += 1
    return tr[:N_REFS]


WORKLOADS = [
    ("Workload A: Sequential loop", sequential_loop),
    ("Workload B: Locality 85/15", locality),
    ("Workload C: Uniform random", uniform),
    ("Workload D: Hot set + scan", hot_scan),
]


def table(name, tr):
    print("\n" + name)
    print("%-14s" % "Algorithm" + "".join("%8d" % n for n in FRAMES))
    algs = [("FIFO", fifo), ("LRU", lru), ("Clock", clock), ("Optimal", optimal),
            ("Linux-style", linux_model), ("Windows-style", lambda t, n: windows_model(t, n)[0])]
    for label, fn in algs:
        row = "".join("%8.2f" % (100.0 * fn(tr, n) / len(tr)) for n in FRAMES)
        print("%-14s" % label + row)


def soft_hard(tr):
    print("\nWindows-style soft vs hard faults (locality workload)")
    print("%-8s%10s%10s%10s" % ("Frames", "Hard", "Soft", "Soft %"))
    for n in FRAMES:
        h, s = windows_model(tr, n)
        print("%-8d%10d%10d%9.1f%%" % (n, h, s, 100.0 * s / (h + s)))


def sensitivity(tr):
    print("\nWorking-set fraction sensitivity (hot set + scan, 40 frames)")
    for frac in (0.3, 0.5, 0.7, 0.9, 1.0):
        h, s = windows_model(tr, 40, frac)
        print("ws_frac %.1f -> hard fault rate %.2f%%" % (frac, 100.0 * h / len(tr)))


def fifo_trace(tr, n):
    mem = deque()
    rows = []
    faults = 0
    for p in tr:
        hit = p in mem
        if not hit:
            faults += 1
            if len(mem) >= n:
                mem.popleft()
            mem.append(p)
        rows.append((p, list(mem), "hit" if hit else "FAULT"))
    return rows, faults


def belady():
    tr = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    print("\nBelady's anomaly, reference string:", tr)
    print("%-8s%8s%8s%10s" % ("Frames", "FIFO", "LRU", "Optimal"))
    for n in (3, 4):
        print("%-8d%8d%8d%10d" % (n, fifo(tr, n), lru(tr, n), optimal(tr, n)))
    for n in (3, 4):
        rows, f = fifo_trace(tr, n)
        print("\nFIFO trace with %d frames" % n)
        for p, mem, res in rows:
            print("ref %-3d frames %-14s %s" % (p, mem, res))
        print("total faults:", f)


def make_plots(traces):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    algs = [("FIFO", fifo), ("LRU", lru), ("Clock", clock), ("Optimal", optimal),
            ("Linux-style", linux_model), ("Windows-style", lambda t, n: windows_model(t, n)[0])]
    styles = {"FIFO": "s--", "LRU": "o-", "Clock": "^-", "Optimal": "k:", "Linux-style": "D-", "Windows-style": "v-"}

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    for ax, key in zip(axes, ["Workload B: Locality 85/15", "Workload D: Hot set + scan"]):
        tr = traces[key]
        for label, fn in algs:
            ax.plot(FRAMES, [100.0 * fn(tr, n) / len(tr) for n in FRAMES], styles[label], label=label, markersize=4)
        ax.set_title(key)
        ax.set_xlabel("Physical frames")
        ax.set_ylabel("Page fault rate (%)")
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    plt.tight_layout()
    plt.savefig("fig_fault_rates.png", dpi=200)
    plt.close()

    tr = traces["Workload B: Locality 85/15"]
    hard = []
    soft = []
    for n in FRAMES:
        h, so = windows_model(tr, n)
        hard.append(h)
        soft.append(so)
    fig, ax = plt.subplots(figsize=(6, 3.4))
    pos = range(len(FRAMES))
    ax.bar(pos, hard, label="Hard faults (disk I/O)")
    ax.bar(pos, soft, bottom=hard, label="Soft faults (standby list)")
    ax.set_xticks(list(pos))
    ax.set_xticklabels(FRAMES)
    ax.set_xlabel("Physical frames")
    ax.set_ylabel("Faults")
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig("fig_soft_hard.png", dpi=200)
    plt.close()
    print("saved fig_fault_rates.png and fig_soft_hard.png")


def main():
    rng = random.Random(SEED)
    traces = {}
    for name, gen in WORKLOADS:
        traces[name] = gen(rng)
        table(name, traces[name])
    soft_hard(traces["Workload B: Locality 85/15"])
    sensitivity(traces["Workload D: Hot set + scan"])
    belady()
    if "--plots" in sys.argv:
        make_plots(traces)


if __name__ == "__main__":
    main()
