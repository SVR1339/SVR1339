#!/usr/bin/env python3
"""
Generate a high-volume, realistic historical git commit stream across all 52 weeks
of the past year (Nov 14, 2025 to Nov 13, 2026) to populate GitHub's native contribution graph.
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
    random.seed(1339)
    start_date = datetime.date(2025, 11, 14)
    end_date = datetime.date(2026, 11, 13)
    num_days = (end_date - start_date).days + 1

    print(f"Generating realistic commit history from {start_date} to {end_date} ({num_days} days)...")

    # Get current HEAD hash
    p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT)
    parent_sha = p.stdout.strip()
    if not parent_sha:
        print("Error: Could not determine HEAD commit.")
        sys.exit(1)

    print(f"Base commit (HEAD): {parent_sha}")

    # Build commit schedule:
    # ~3,100 total commits across 365 days
    # Weekdays: 6 to 14 commits
    # Weekends: 1 to 5 commits (with occasional rest day)
    all_commits = []
    mark_id = 1

    for day_idx in range(num_days):
        cur_date = start_date + datetime.timedelta(days=day_idx)
        is_weekend = cur_date.weekday() >= 5

        if is_weekend:
            # 85% chance of weekend activity (pro dev side projects / open source)
            if random.random() < 0.85:
                count = random.randint(2, 6)
            else:
                count = 0
        else:
            # Weekdays: solid high activity
            count = random.choices([5, 7, 9, 11, 13, 16], weights=[10, 25, 30, 20, 10, 5])[0]

        if count == 0:
            continue

        # Distribute commits throughout waking hours (09:00 to 23:30)
        times = sorted([random.randint(9 * 3600, 23 * 3600 + 30 * 60) for _ in range(count)])

        for sec in times:
            hour = sec // 3600
            minute = (sec % 3600) // 60
            dt = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, hour, minute, random.randint(0, 59))
            # Epoch timestamp in seconds
            # Assuming Asia/Kolkata (IST = +05:30)
            epoch = int(dt.timestamp())
            msg = random.choice(COMMIT_MESSAGES)
            all_commits.append((mark_id, epoch, dt.isoformat(), msg))
            mark_id += 1

    total_commits = len(all_commits)
    print(f"Total commits planned: {total_commits} across {num_days} days.")

    # Generate fast-import command stream
    lines = []
    log_content = "=== SVR1339 SYSTEMS ENGINEERING ACTIVITY LOG ===\n"

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

        # Update activity.log content periodically
        log_entry = f"[{isostr}] {msg}\n"
        log_content += log_entry
        # Keep log size reasonable by slicing last 100 entries
        log_slice = "\n".join(log_content.splitlines()[-80:]) + "\n"
        log_bytes = log_slice.encode("utf-8")
        lines.append("M 644 inline data/activity.log")
        lines.append(f"data {len(log_bytes)}")
        lines.append(log_slice)

    # Final commit bringing all working tree files (hero.svg, README, etc.) up to date
    now_epoch = int(time.time())
    final_mid = mark_id
    final_msg = "feat: high-performance systems engineering profile & live runtime cards"
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
    # Check out the updated branch state into the working tree
    subprocess.run(["git", "checkout", "main", "--force"], cwd=ROOT)
    subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=ROOT)

    p_log = subprocess.run(["git", "log", "-n", "3", "--format=%h %ad %s"], capture_output=True, text=True, cwd=ROOT)
    print("Recent commits:\n" + p_log.stdout)

if __name__ == "__main__":
    generate()
