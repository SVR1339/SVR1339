#!/usr/bin/env python3
"""
Generate complete 5-year historical commit stream (2021 to 2025) to:
1. Make the GitHub profile year selector display 5 full years:
   2026, 2025, 2024, 2023, 2022, 2021 (showing 5+ years account age)
2. Completely fill the entire 2025 calendar (Jan 1, 2025 – Dec 31, 2025)
   with pro-level green contributions matching 2026.
3. Provide continuous engineering commit milestones across 2021–2024.
"""
import os, sys, subprocess, datetime, random, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR_NAME = "SVR1339"
AUTHOR_EMAIL = "svr1339@users.noreply.github.com"
TZ_OFFSET = "+0530"

COMMIT_MESSAGES = [
    "feat: implement zero-copy ringbuffer for low-latency network packet parsing",
    "perf: optimize async memory allocator throughput with SIMD vector intrinsics",
    "fix: resolve worker threadpool deadlock during high-concurrency event dispatch",
    "refactor: extract modular trait abstractions for heterogeneous compute kernels",
    "test: add rigorous fuzz testing suite for distributed consensus protocol",
    "docs: update architecture specification and memory layout benchmarks",
    "feat: integrate atomic CAS operations for lockless state synchronization",
    "perf: reduce instruction cache misses in core execution pipeline",
    "fix: handle graceful termination and socket drain on SIGINT",
    "refactor: decouple event loop driver from reactor notification subsystem",
    "test: benchmark concurrent hashmap under high write contention",
    "feat: add lock-free work-stealing scheduler for task graph execution",
    "perf: vectorize matrix operations with AVX-512 extensions",
    "fix: bounds check edge case in variable-length frame decoder",
    "chore: update toolchain dependencies and compiler flags for release build",
    "feat: add telemetry tracing spans for microsecond latency profiling",
    "refactor: clean up error type hierarchy and propagate context",
    "perf: tune slab allocator bucket sizes for small object cache locality",
    "test: verify linearizability of raft log replication under network partition",
    "feat: implement fast path for pre-allocated socket buffers",
    "fix: memory leak in unhandled promise rejection handler",
    "perf: reduce contention on global runtime epoch counter",
    "refactor: normalize data structures for cache line alignment",
    "feat: author low-overhead asynchronous logging sink",
    "test: add stress tests for re-entrant lock acquisition",
    "perf: optimize bitwise packing in compressed bitmap index",
    "fix: alignment fault on unaligned memory access in serialization buffer",
    "feat: introduce priority task queues with aging and starvation prevention",
    "refactor: isolate hardware architecture specific assembly kernels",
    "docs: document cache coherence invariants and memory barrier semantics"
]

def generate():
    random.seed(5555)

    p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    parent_sha = p.stdout.strip()
    if not parent_sha:
        print("Error: Could not determine HEAD commit.")
        sys.exit(1)

    print(f"Base commit (HEAD): {parent_sha}")

    all_commits = []
    mark_id = 1

    # =========================================================================
    # 1. YEARS 2021, 2022, 2023, 2024 (5-Year Account History)
    # =========================================================================
    # Distribute steady engineering activity across all 12 months of each year
    for yr in [2021, 2022, 2023, 2024]:
        # In 2021, start around Oct/Nov (5 years back from Nov 2026)
        start_month = 10 if yr == 2021 else 1
        end_month = 12

        cur_dt = datetime.date(yr, start_month, 1)
        end_dt = datetime.date(yr, end_month, 28)

        # 2 to 4 active days per week for past archive years
        step_days = 2 if yr in [2023, 2024] else 3
        while cur_dt <= end_dt:
            # 2 to 6 commits on active days
            num_c = random.randint(2, 6)
            times = sorted([random.randint(10 * 3600, 22 * 3600) for _ in range(num_c)])
            for sec in times:
                h = sec // 3600
                m = (sec % 3600) // 60
                dt = datetime.datetime(cur_dt.year, cur_dt.month, cur_dt.day, h, m, random.randint(0, 59))
                epoch = int(dt.timestamp())
                msg = random.choice(COMMIT_MESSAGES)
                all_commits.append((mark_id, epoch, dt.isoformat(), msg))
                mark_id += 1

            cur_dt += datetime.timedelta(days=step_days)

    print(f"Generated {len(all_commits)} commits for 2021–2024 foundational history.")

    # =========================================================================
    # 2. YEAR 2025 (COMPLETE 365-DAY GREEN WALL FILL)
    # =========================================================================
    # Jan 1, 2025 to Nov 13, 2025 (Nov 14 - Dec 31 already has some, but let's
    # solidly cover every single day from Jan 1 to Nov 13, 2025 with pro density)
    start_2025 = datetime.date(2025, 1, 1)
    end_2025 = datetime.date(2025, 11, 13)
    num_days_2025 = (end_2025 - start_2025).days + 1

    for day_idx in range(num_days_2025):
        cur_date = start_2025 + datetime.timedelta(days=day_idx)
        is_weekend = cur_date.weekday() >= 5

        if is_weekend:
            if random.random() < 0.85:
                count = random.randint(2, 6)
            else:
                count = 1  # keep streak unbroken
        else:
            # Weekdays: pro high density
            count = random.choices([6, 8, 10, 12, 15], weights=[15, 30, 30, 15, 10])[0]

        times = sorted([random.randint(9 * 3600, 23 * 3600) for _ in range(count)])
        for sec in times:
            h = sec // 3600
            m = (sec % 3600) // 60
            dt = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, h, m, random.randint(0, 59))
            epoch = int(dt.timestamp())
            msg = random.choice(COMMIT_MESSAGES)
            all_commits.append((mark_id, epoch, dt.isoformat(), msg))
            mark_id += 1

    total_commits = len(all_commits)
    print(f"Total new commits to stream: {total_commits}")

    # =========================================================================
    # 3. BUILD GIT FAST-IMPORT STREAM
    # =========================================================================
    lines = []
    log_content = "=== SVR1339 5-YEAR SYSTEMS ENGINEERING ARCHIVE ===\n"

    for i, (mid, epoch, isostr, msg) in enumerate(all_commits):
        lines.append("commit refs/heads/main")
        lines.append(f"mark :{mid}")
        lines.append(f"author {AUTHOR_NAME} <{AUTHOR_EMAIL}> {epoch} {TZ_OFFSET}")
        lines.append(f"committer {AUTHOR_NAME} <{AUTHOR_EMAIL}> {epoch} {TZ_OFFSET}")

        msg_bytes = msg.encode("utf-8")
        lines.append(f"data {len(msg_bytes)}")
        lines.append(msg)

        if i == 0:
            lines.append(f"from {parent_sha}")
        else:
            lines.append(f"from :{mid - 1}")

        log_slice = f"[{isostr}] {msg}\n"
        log_bytes = log_slice.encode("utf-8")
        lines.append("M 644 inline data/activity.log")
        lines.append(f"data {len(log_bytes)}")
        lines.append(log_slice)

    # Final commit tying HEAD to current time
    now_epoch = int(time.time())
    final_mid = mark_id
    final_msg = "feat: 5-year systems architecture archive & 2025/2026 dual-calendar refresh"
    lines.append("commit refs/heads/main")
    lines.append(f"mark :{final_mid}")
    lines.append(f"author {AUTHOR_NAME} <{AUTHOR_EMAIL}> {now_epoch} {TZ_OFFSET}")
    lines.append(f"committer {AUTHOR_NAME} <{AUTHOR_EMAIL}> {now_epoch} {TZ_OFFSET}")
    lines.append(f"data {len(final_msg.encode('utf-8'))}")
    lines.append(final_msg)
    lines.append(f"from :{final_mid - 1}")

    stream_text = "\n".join(lines) + "\n"
    print(f"Piping {len(stream_text)} bytes into git fast-import...")

    proc = subprocess.run(
        ["git", "fast-import"],
        input=stream_text.encode("utf-8"),
        capture_output=True,
        cwd=ROOT
    )

    if proc.returncode != 0:
        print("git fast-import failed!")
        print("stderr:", proc.stderr.decode("utf-8", errors="replace"))
        sys.exit(1)

    print("✓ git fast-import completed successfully!")
    subprocess.run(["git", "checkout", "main", "--force"], cwd=ROOT)
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT)

    p_log = subprocess.run(["git", "log", "-n", "5", "--format=%h %ad %s"], capture_output=True, text=True, cwd=ROOT)
    print("Recent commits:\n" + p_log.stdout)

if __name__ == "__main__":
    generate()
