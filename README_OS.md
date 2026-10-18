# Code Guide: How to Run the Codes and Get the Outputs

Two programs, no other dependencies for the main run.

| File | What it does | Used for |
|---|---|---|
| `vmsim.py` | Page replacement simulator (FIFO, LRU, Clock, Optimal, Linux-style, Windows-style) | Report Tables 4 to 7 and Figures 2 and 3 |
| `mem_pressure.py` | Allocates and holds memory so you can watch the OS react | Report Section 4.6 screenshots (Ubuntu and Windows) |

Repo: https://github.com/amanhashim06/PageReplacementandVM-ManagementinLinuxV-SWindows

---

## 1. vmsim.py (same on Ubuntu and Windows)

**Requirements:** Python 3.8 or newer. Graphs also need matplotlib.

### Run

| Task | Ubuntu | Windows (PowerShell or CMD) |
|---|---|---|
| Check Python | `python3 --version` | `python --version` or `py --version` |
| Print all tables | `python3 vmsim.py` | `python vmsim.py` |
| Save tables to a file | `python3 vmsim.py > results.txt` | `python vmsim.py > results.txt` |
| Install graph library | `pip3 install matplotlib` | `pip install matplotlib` |
| Also save graphs | `python3 vmsim.py --plots` | `python vmsim.py --plots` |

Run it from the folder that contains `vmsim.py` (`cd` into it first). Runtime is a few seconds.

### What you get

The program prints these blocks, in this order:

1. Workload A, B, C, D tables: fault rate (%) for 10, 20, 30, 40, 50, 60, 80 frames
2. Windows-style soft vs hard faults on workload B
3. Working set fraction sensitivity (hot set + scan, 40 frames)
4. Belady's anomaly summary, then the FIFO trace for 3 and 4 frames

`--plots` also saves `fig_fault_rates.png` (Figure 2) and `fig_soft_hard.png` (Figure 3) next to the script.

### Check your output is correct

The seed is fixed at 42, so your numbers must match these exactly:

| Check | Expected value |
|---|---|
| Workload D, 40 frames, FIFO / LRU / Clock / Windows-style | 66.23 |
| Workload D, 40 frames, Linux-style | 48.85 |
| Workload D, 40 frames, Optimal | 39.43 |
| Workload B, 30 frames, LRU / FIFO | 17.43 / 29.12 |
| Soft share on workload B at 40 frames | 52.6% (2,936 hard, 3,264 soft) |
| Belady: FIFO with 3 / 4 frames | 9 / 10 faults |

If any value differs, you are running an edited copy. Download the file again from the repo.

### Where each output goes in the report

| Program output | Report item |
|---|---|
| Workload B and D tables | Tables 5 and 6 |
| Row at 40 frames from all four workloads | Table 4 |
| Soft vs hard table | Section 4.4 text and Figure 3 |
| Sensitivity lines | Section 4.4 text (66.23% for every fraction) |
| FIFO trace | Table 7 |
| fig_fault_rates.png | Figure 2 |
| fig_soft_hard.png | Figure 3 |

### Common problems

- `python` not found on Ubuntu: use `python3`.
- `ModuleNotFoundError: matplotlib`: run the install command above, or skip `--plots`.
- Nothing seems to happen: the tables print in the terminal, so scroll up, or use `> results.txt` and open the file.
- `BrokenPipeError` when adding `| head`: harmless, it only means output was cut short.

---

## 2. mem_pressure.py (observation screenshots)

### Usage

```
python3 mem_pressure.py <MB to allocate> <seconds to hold>
```

On Windows use `python` instead of `python3`.

| What you did | Command | Note |
|---|---|---|
| Ubuntu, 23 GiB RAM | `python3 mem_pressure.py 18000 30` | about 78% of RAM |
| Windows, 24 GB RAM | `python mem_pressure.py 14000 60` | about 58% of RAM |

It prints `allocated N MB` every 100 MB, then `holding ... watch your tools now`, then `done` when it exits. Start your monitors before running it, and take screenshots while it prints "holding".

### Safety

- Save your work and close heavy apps first.
- Start at 50 to 70% of RAM. Going close to 100% can freeze the machine.
- Ctrl+C stops the script and frees the memory.

### Ubuntu: what to type

Terminal 1:
```
free -h
swapon --show
vmstat 1 40
```
Terminal 2:
```
python3 mem_pressure.py 18000 30
```
While it runs (third terminal or tab):
```
free -h
grep -i active /proc/meminfo
```
Look at: free memory dropping, `buff/cache`, `si` and `so` columns (swap in and out), Active vs Inactive and the anon and file lines.

Alternative load: `sudo apt install stress-ng` then `stress-ng --vm 1 --vm-bytes 80% --timeout 30s`.

### Windows: what to open

1. Press Win+R, type `resmon`, open the **Memory** tab. Optionally expand **Physical Memory** at the bottom to see Standby, Modified and Free.
2. Open Task Manager > Performance > Memory.
3. Run `python mem_pressure.py 14000 60`.
4. While it runs, tick `python.exe` in Resource Monitor and sort by Working Set.
5. Screenshot both windows while "holding" is on screen.

Optional PowerShell commands:
```
Get-CimInstance Win32_PageFileUsage
Get-Counter '\Memory\Pages Input/sec' -SampleInterval 1 -MaxSamples 10
```

### What your own results showed

| | Ubuntu | Windows |
|---|---|---|
| Free or available | free 17 GiB to 5.1 GiB (vmstat down to about 217 MiB) | available 18.4 GB to 4.6 GB |
| Used | 2.2 GiB to 14 GiB | about 21% to 80% |
| Swapping | si and so stayed 0, swap about 512 KB | Hard Faults/sec only short spikes |
| Other | Active about 20 GiB (mostly anon), Inactive about 2 GiB (mostly file) | python.exe working set about 14.4 GB, committed 24.1 of 25.6 GB |

---

## 3. Update the GitHub repo

From the project folder:

```
git add .
git commit -m "Add results and README"
git push
```

Suggested extra files: `README.md` (one paragraph plus `python vmsim.py`), `results.txt` (from `python vmsim.py > results.txt`), and the two PNG figures.

---

## 4. Quick checklist

- [ ] `python vmsim.py` output matches the check table
- [ ] `--plots` PNGs created
- [ ] Ubuntu before and during screenshots taken
- [ ] Windows before and during screenshots taken
- [ ] Repo contains code, README, results.txt and figures
- [ ] Report link text shows the full repo URL (without `.git`)
