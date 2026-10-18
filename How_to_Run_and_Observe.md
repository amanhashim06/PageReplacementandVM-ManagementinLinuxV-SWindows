# How to run the simulation and observe paging

## 1. Run the simulator (same on both systems)

Needs Python 3.8+. No libraries needed for the tables.

| | Linux | Windows (PowerShell or CMD) |
|---|---|---|
| Check Python | `python3 --version` | `python --version` (or `py --version`) |
| Run tables | `python3 vmsim.py` | `python vmsim.py` (or `py vmsim.py`) |
| Save output to a file | `python3 vmsim.py > results.txt` | `python vmsim.py > results.txt` |
| Make the graphs | `pip3 install matplotlib` then `python3 vmsim.py --plots` | `pip install matplotlib` then `python vmsim.py --plots` |

Seed is fixed at 42, so everyone in the group gets identical numbers. The output is exactly what Tables 4 to 7 in the report show. `--plots` saves `fig_fault_rates.png` and `fig_soft_hard.png` in the same folder.

## 2. Linux: commands to type (take screenshots)

```
free -h
swapon --show
cat /proc/sys/vm/swappiness
grep -E 'Active|Inactive' /proc/meminfo
vmstat 1 10
ps -o pid,min_flt,maj_flt,cmd -p <PID>
```

Create pressure in a second terminal, then run `vmstat 1 10` and `free -h` while it runs:

```
sudo apt install stress-ng
stress-ng --vm 1 --vm-bytes 80% --timeout 30s
```

Or without stress-ng: `python3 mem_pressure.py 3000 30` (allocates 3000 MB and holds it for 30 s).

What to look at: `si` / `so` in vmstat (swap in / out), swap used in `free -h`, Active vs Inactive sizes in /proc/meminfo.

## 3. Windows: what to open / type (take screenshots)

PowerShell:

```
Get-CimInstance Win32_PageFileUsage
Get-Counter '\Memory\Pages Input/sec' -SampleInterval 1 -MaxSamples 10
Get-Counter '\Memory\Page Faults/sec' -SampleInterval 1 -MaxSamples 10
```

GUI: Task Manager > Performance > Memory (In use, Compressed, Committed, Cached). Then Resource Monitor (`resmon`) > Memory tab: Hard Faults/sec graph, and the bar showing Modified, Standby, Free. Task Manager > Details > right-click a header > Select columns > Page faults, Working set.

Create pressure: `python mem_pressure.py 3000 30`, or open many browser tabs / a large file.

What to look at: size of the Standby list, Compressed memory, Hard Faults/sec rising during pressure.

## 4. Safety for mem_pressure.py

The first argument is MB to allocate, the second is seconds to hold. Start at about 50 to 70 percent of your free RAM (check with `free -m` or Task Manager), save your work first, and close other apps. Going far above RAM can freeze the laptop. Press Ctrl+C to stop.

## 5. Tips for the screenshots in Section 4.6 of the report

- Keep each screenshot to about half page width so the body stays inside 10 pages.
- Write the 2 to 3 observation sentences from what your own screen showed, not from this guide.
- If nobody has a Linux machine, WSL2 or a Linux VM works for the commands above.
