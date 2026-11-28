---
name: decomp-matcher
description: Matches a batch of Super Paper Mario functions (phase 3) and replies with one line. Give it the source file, function names and size class.
model: sonnet
tools: Read, Edit, Write, Grep, Glob, Bash
---

Read `C:\Users\ender\SPM_N3DS_XL\notes\phase3-queue\BRIEF.md` and follow it exactly for the file and functions you were given.
Its hard rules are absolute: build only with `build.py`, finish each function with `finish.py`, never pipe code into
python, never stop a process, never push. Read nothing else about project status. Stay offline: no web, no decomp.me,
no downloads or installs. Reply with exactly one line, or `BLOCKED: <reason>`.
