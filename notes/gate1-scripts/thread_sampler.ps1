<#
Per-thread CPU and instruction-pointer sampler for a running game (read-only: it never changes the game's files or memory).
Run it in a SECOND PowerShell window, before or after starting the game:

    powershell -NoProfile -ExecutionPolicy Bypass -File thread_sampler.ps1 [-StartAfter 90] [-Length 20] [-Hz 200]

What it records, into -OutDir (default Play\sampler-out\run-<timestamp>):
  threads_timeline.csv  every second, for every thread of the process: total CPU time (kernel + user), plus the thread's
                        name if it has one (GetThreadDescription). Gives CPU milliseconds per thread over the whole run.
  rip_samples.csv       during the window only: the instruction pointer of every thread, -Hz times a second
                        (each thread is paused for a few microseconds per sample), with the module and offset it falls in.
  gpu_util.csv          every second, GPU engine utilisation of the game process and of the whole system
                        (Windows "GPU Engine" performance counters).
  meta.txt              process id, the time of the first presented frame, the window, sample counts.
The window is -StartAfter seconds after the game's first presented frame (the line "(frame 1)" in its console.log), the same
clock NSMBW_PROFILE uses, so both cover the same seconds.
#>
[CmdletBinding()]
param(
    [string]$ProcessName = 'SuperPaperMario',
    [int]$ProcessId = 0,
    [double]$StartAfter = 90,
    [double]$Length = 20,
    [int]$Hz = 200,
    [string]$LogRoot = 'C:\Users\ender\SPM_N3DS_XL\NewSuperPaperBros\Play\UserData\Logs',
    [string]$OutDir = '',
    [switch]$NoLog          # test mode: take the window from the process start instead of the game's log
)
$ErrorActionPreference = 'Stop'
# Keep the compiler's temporary files inside the project, not in the user's temp folder.
$projectTemp = 'C:\Users\ender\SPM_N3DS_XL\NewSuperPaperBros\toolchain\tmp'
[IO.Directory]::CreateDirectory($projectTemp) | Out-Null
$env:TEMP = $projectTemp; $env:TMP = $projectTemp

Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

public static class ThreadSampler
{
    [DllImport("kernel32.dll", SetLastError = true)] static extern IntPtr OpenThread(uint access, bool inherit, uint tid);
    [DllImport("kernel32.dll")] static extern uint SuspendThread(IntPtr h);
    [DllImport("kernel32.dll")] static extern int ResumeThread(IntPtr h);
    [DllImport("kernel32.dll")] static extern bool GetThreadContext(IntPtr h, IntPtr ctx);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
    [DllImport("kernel32.dll")] static extern int GetThreadDescription(IntPtr h, out IntPtr desc);
    [DllImport("kernel32.dll")] static extern IntPtr LocalFree(IntPtr p);
    [DllImport("kernel32.dll")] static extern bool GetThreadTimes(IntPtr h, out long create, out long exit, out long kernel, out long user);

    const uint ACCESS = 0x0002 | 0x0008 | 0x0800;   // suspend/resume, get context, query limited information

    class Th { public IntPtr H; public string Name; }

    static string ThreadName(IntPtr h)
    {
        try
        {
            IntPtr p;
            if (GetThreadDescription(h, out p) >= 0 && p != IntPtr.Zero)
            {
                string s = Marshal.PtrToStringUni(p);
                LocalFree(p);
                return s == null ? "" : s;
            }
        }
        catch (Exception) { }
        return "";
    }

    static void Timeline(Process proc, Dictionary<uint, Th> threads, StreamWriter tl, DateTime started)
    {
        proc.Refresh();
        DateTime now = DateTime.UtcNow;
        HashSet<uint> alive = new HashSet<uint>();
        foreach (ProcessThread pt in proc.Threads)
        {
            uint tid = (uint)pt.Id;
            alive.Add(tid);
            Th t;
            if (!threads.TryGetValue(tid, out t))
            {
                IntPtr h = OpenThread(ACCESS, false, tid);
                if (h == IntPtr.Zero) continue;
                t = new Th(); t.H = h; t.Name = ThreadName(h);
                threads[tid] = t;
            }
            long c, e, k, u;
            if (!GetThreadTimes(t.H, out c, out e, out k, out u)) continue;
            tl.WriteLine(now.ToString("o") + "," + (now - started).TotalSeconds.ToString("F3") + "," + tid + "," +
                         ((k + u) / 10000.0).ToString("F2") + "," + (u / 10000.0).ToString("F2") + "," + (k / 10000.0).ToString("F2") + "," + t.Name.Replace(',', ' '));
        }
        List<uint> gone = new List<uint>();
        foreach (uint tid in threads.Keys) if (!alive.Contains(tid)) gone.Add(tid);
        foreach (uint tid in gone) { CloseHandle(threads[tid].H); threads.Remove(tid); }
        tl.Flush();
    }

    static DateTime FindFirstFrame(string logRoot, int pid)
    {
        try
        {
            string[] dirs = Directory.GetDirectories(logRoot, "*_pid" + pid);
            if (dirs.Length == 0) return DateTime.MinValue;
            string path = Path.Combine(dirs[0], "console.log");
            if (!File.Exists(path)) return DateTime.MinValue;
            using (FileStream fs = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
            using (StreamReader sr = new StreamReader(fs, Encoding.UTF8))
            {
                string line;
                while ((line = sr.ReadLine()) != null)
                    if (line.IndexOf("seq ->", StringComparison.Ordinal) >= 0 && line.IndexOf("(frame 1)", StringComparison.Ordinal) >= 0)
                        return DateTime.UtcNow;
            }
        }
        catch (Exception) { }
        return DateTime.MinValue;
    }

    // The log folder is named base_<unix seconds>_pid<pid>: the moment the game created it, about 2.3-3.3 s before the first frame.
    static DateTime FolderEpoch(string logRoot, int pid)
    {
        try
        {
            string[] dirs = Directory.GetDirectories(logRoot, "*_pid" + pid);
            if (dirs.Length == 0) return DateTime.MinValue;
            string[] parts = Path.GetFileName(dirs[0]).Split('_');
            long secs;
            if (parts.Length >= 3 && long.TryParse(parts[1], out secs))
                return new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc).AddSeconds(secs);
        }
        catch (Exception) { }
        return DateTime.MinValue;
    }

    static string Describe(List<ProcessModule> mods, ulong rip, out string rva)
    {
        foreach (ProcessModule m in mods)
        {
            ulong b = (ulong)m.BaseAddress.ToInt64();
            if (rip >= b && rip < b + (ulong)m.ModuleMemorySize) { rva = (rip - b).ToString("X"); return m.ModuleName; }
        }
        rva = ""; return "(unknown)";
    }

    public static string Run(int pid, string logRoot, string outDir, double startAfter, double length, int hz, bool useLog)
    {
        Directory.CreateDirectory(outDir);
        Process proc = Process.GetProcessById(pid);
        DateTime started = DateTime.UtcNow;
        Dictionary<uint, Th> threads = new Dictionary<uint, Th>();
        StreamWriter tl = new StreamWriter(Path.Combine(outDir, "threads_timeline.csv"));
        tl.WriteLine("utc,t_s,tid,cpu_ms,user_ms,kernel_ms,name");
        List<long> sMs = new List<long>(); List<uint> sTid = new List<uint>(); List<ulong> sRip = new List<ulong>();
        IntPtr raw = Marshal.AllocHGlobal(1232 + 16);
        IntPtr ctx = new IntPtr((raw.ToInt64() + 15) & ~15L);
        DateTime t0 = useLog ? DateTime.MinValue : started;
        DateTime winStart = DateTime.MinValue, winEnd = DateTime.MinValue;
        List<ProcessModule> mods = null;
        DateTime nextTimeline = started, nextLogPoll = started, nextCycle = started;
        double periodMs = 1000.0 / hz;
        long cycles = 0, failed = 0;
        bool firstPollDone = false, estimated = false;
        Stopwatch sw = new Stopwatch();
        if (!useLog) { winStart = t0.AddSeconds(startAfter); winEnd = winStart.AddSeconds(length); }
        while (true)
        {
            DateTime now = DateTime.UtcNow;
            try { if (proc.HasExited) break; } catch (Exception) { break; }
            if (t0 == DateTime.MinValue && now >= nextLogPoll)
            {
                nextLogPoll = now.AddMilliseconds(250);
                DateTime f = FindFirstFrame(logRoot, pid);
                if (f != DateTime.MinValue)
                {
                    // Started late (the first frame was already in the log at the first look): the time we saw it is not the
                    // time it happened, so estimate it from the log folder's name instead (accurate to about +-0.5 s).
                    if (!firstPollDone)
                    {
                        DateTime ep = FolderEpoch(logRoot, pid);
                        if (ep != DateTime.MinValue && (f - ep).TotalSeconds > 6.0) { f = ep.AddSeconds(2.5); estimated = true; }
                    }
                    t0 = f; winStart = t0.AddSeconds(startAfter); winEnd = winStart.AddSeconds(length);
                }
                firstPollDone = true;
            }
            if (t0 != DateTime.MinValue && now > winEnd.AddSeconds(1)) break;
            if (now >= nextTimeline) { Timeline(proc, threads, tl, started); nextTimeline = now.AddSeconds(1); }
            bool inWin = t0 != DateTime.MinValue && now >= winStart && now < winEnd;
            if (!inWin) { Thread.Sleep(20); continue; }
            if (mods == null)
            {
                mods = new List<ProcessModule>();
                foreach (ProcessModule m in proc.Modules) mods.Add(m);
                sw.Start();
            }
            if (now < nextCycle) { Thread.Yield(); continue; }
            nextCycle = now.AddMilliseconds(periodMs);
            long ms = (long)(now - winStart).TotalMilliseconds;
            List<uint> ids = new List<uint>(threads.Keys);
            foreach (uint tid in ids)
            {
                Th t = threads[tid];
                if (SuspendThread(t.H) == 0xFFFFFFFF) { failed++; continue; }
                Marshal.WriteInt32(ctx, 0x30, 0x100001);          // CONTEXT_CONTROL
                bool ok = GetThreadContext(t.H, ctx);
                ulong rip = ok ? (ulong)Marshal.ReadInt64(ctx, 0xF8) : 0UL;
                ResumeThread(t.H);
                if (ok) { sMs.Add(ms); sTid.Add(tid); sRip.Add(rip); } else failed++;
            }
            cycles++;
        }
        Timeline(proc.HasExited ? Process.GetCurrentProcess() : proc, new Dictionary<uint, Th>(), new StreamWriter(Stream.Null), started);
        tl.Close();
        StreamWriter rs = new StreamWriter(Path.Combine(outDir, "rip_samples.csv"));
        rs.WriteLine("t_ms,tid,module,rva_hex,rip_hex");
        if (mods == null) mods = new List<ProcessModule>();
        for (int i = 0; i < sMs.Count; i++)
        {
            string rva; string mod = Describe(mods, sRip[i], out rva);
            rs.WriteLine(sMs[i] + "," + sTid[i] + "," + mod + "," + rva + "," + sRip[i].ToString("X"));
        }
        rs.Close();
        string meta = "pid=" + pid + "\nfirst_frame_estimated_because_started_late=" + estimated +
                      "\nfirst_frame_utc=" + (t0 == DateTime.MinValue ? "not found" : t0.ToString("o")) +
                      "\nwindow_start_utc=" + winStart.ToString("o") + "\nwindow_end_utc=" + winEnd.ToString("o") +
                      "\nhz=" + hz + "\ncycles=" + cycles + "\nsamples=" + sMs.Count + "\nfailed_samples=" + failed +
                      "\nthreads_seen=" + threads.Count + "\nmodules=" + mods.Count + "\n";
        File.WriteAllText(Path.Combine(outDir, "meta.txt"), meta);
        Marshal.FreeHGlobal(raw);
        return meta;
    }
}
'@

# ---- find the process ----
if ($ProcessId -eq 0) {
    Write-Host "Waiting for $ProcessName to start (start the game now)..."
    while (-not ($proc = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1)) { Start-Sleep -Milliseconds 300 }
    $ProcessId = $proc.Id
}
if (-not $OutDir) { $OutDir = Join-Path 'C:\Users\ender\SPM_N3DS_XL\NewSuperPaperBros\Play\sampler-out' ("run-" + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
[IO.Directory]::CreateDirectory($OutDir) | Out-Null
Write-Host "Sampling pid $ProcessId; output in $OutDir"
Write-Host ("Window: {0} s to {1} s after the first presented frame, {2} Hz. Keep playing in the scene you want measured until this finishes." -f $StartAfter, ($StartAfter + $Length), $Hz)

# ---- GPU utilisation, once a second, in the background ----
$job = Start-Job -ArgumentList $ProcessId, $OutDir -ScriptBlock {
    param($gamePid, $out)
    $f = Join-Path $out 'gpu_util.csv'
    'utc,scope,engtype,util_percent' | Set-Content -Path $f
    while ($true) {
        try { $s = Get-Counter -Counter '\GPU Engine(*)\Utilization Percentage' -ErrorAction Stop } catch { Start-Sleep -Seconds 1; continue }
        $utc = (Get-Date).ToUniversalTime().ToString('o')
        $sum = @{}
        foreach ($c in $s.CounterSamples) {
            if ($c.InstanceName -match '^pid_(\d+)_.*_engtype_(.+)$') {
                $eng = $Matches[2]
                $k = "all|$eng"; if ($sum.ContainsKey($k)) { $sum[$k] += $c.CookedValue } else { $sum[$k] = $c.CookedValue }
                if ($Matches[1] -eq "$gamePid") { $k = "process|$eng"; if ($sum.ContainsKey($k)) { $sum[$k] += $c.CookedValue } else { $sum[$k] = $c.CookedValue } }
            }
        }
        foreach ($k in $sum.Keys) { $p = $k.Split('|'); "$utc,$($p[0]),$($p[1]),$([math]::Round($sum[$k],2))" | Add-Content -Path $f }
    }
}
try {
    $meta = [ThreadSampler]::Run($ProcessId, $LogRoot, $OutDir, $StartAfter, $Length, $Hz, (-not $NoLog))
    Write-Host $meta
} finally {
    Stop-Job $job -ErrorAction SilentlyContinue; Remove-Job $job -Force -ErrorAction SilentlyContinue
}
Write-Host "Done. Files: $OutDir"
