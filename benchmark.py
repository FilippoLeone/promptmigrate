"""
Benchmark script for PromptMigrate performance testing.

This script performs various performance measurements:
1. Initialization time
2. Migration application speed
3. Prompt access performance (both static and dynamic)
4. Memory usage

Usage:
    python benchmark.py
"""

import gc
import time
import os
from pathlib import Path
import statistics
import tracemalloc
from contextlib import contextmanager

from promptmigrate.manager import PromptManager, prompt_revision

# Temporary directory for benchmark files
BENCHMARK_DIR = Path("benchmark_tmp")


@contextmanager
def measure_time(operation_name):
    """Measure and print the execution time of a code block."""
    start_time = time.time()
    yield
    end_time = time.time()
    print(f"{operation_name}: {(end_time - start_time) * 1000:.2f} ms")


@contextmanager
def measure_memory(operation_name):
    """Measure and print the memory usage of a code block."""
    tracemalloc.start()
    yield
    current, peak = tracemalloc.get_traced_memory()
    print(f"{operation_name} Memory: current={current / 1024:.1f} KB, peak={peak / 1024:.1f} KB")
    tracemalloc.stop()


def setup_benchmark_env():
    """Set up a clean environment for benchmarking."""
    # Create benchmark directory
    BENCHMARK_DIR.mkdir(exist_ok=True)
    
    # Create a clean prompt_revisions directory
    revisions_dir = BENCHMARK_DIR / "prompt_revisions"
    revisions_dir.mkdir(exist_ok=True)
    (revisions_dir / "__init__.py").touch()
    
    # Return paths for prompt and state files
    return BENCHMARK_DIR / "prompts.yaml", BENCHMARK_DIR / ".state.json"


def create_test_migrations(num_migrations=5, prompts_per_migration=10):
    """Create test migration functions."""
    migrations = []
    
    for i in range(1, num_migrations + 1):
        rev_id = f"{i:03d}_migration"
        
        @prompt_revision(rev_id, f"Test migration {i}")
        def migrate(prompts, idx=i):
            for j in range(1, prompts_per_migration + 1):
                prompts[f"PROMPT_{idx}_{j}"] = f"This is test prompt {j} from migration {idx}"
                if j % 3 == 0:
                    # Add some dynamic values to test performance
                    prompts[f"DYNAMIC_{idx}_{j}"] = f"Today is {{{{date:format=%Y-%m-%d}}}} and your number is {{{{number:min=1,max=100}}}}"
            return prompts
        
        migrations.append(migrate)
    
    return migrations


def benchmark_initialization(prompt_file, state_file, iterations=10):
    """Benchmark PromptManager initialization."""
    init_times = []
    
    for _ in range(iterations):
        gc.collect()
        start = time.time()
        manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
        end = time.time()
        init_times.append((end - start) * 1000)  # Convert to ms
    
    print(f"Initialization Time (avg of {iterations}): {statistics.mean(init_times):.2f} ms")
    print(f"  Min: {min(init_times):.2f} ms, Max: {max(init_times):.2f} ms")
    

def benchmark_migrations(prompt_file, state_file, migrations):
    """Benchmark migration application."""
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
    
    with measure_time("Apply All Migrations"):
        manager.upgrade()
    
    print(f"Applied {len(migrations)} migrations")
    
    # Reset state for individual tests
    if prompt_file.exists():
        prompt_file.unlink()
    if state_file.exists():
        state_file.unlink()
    
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
    
    # Measure individual migration times
    for i, _ in enumerate(migrations):
        with measure_time(f"Migration {i+1}"):
            manager.upgrade(target=f"{i+1:03d}_migration")


def benchmark_prompt_access(prompt_file, state_file, iterations=1000):
    """Benchmark prompt access performance."""
    manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
    
    # Make sure migrations are applied
    if manager.current_rev() is None:
        manager.upgrade()
    
    # Get all available prompts
    all_prompts = manager.load_prompts()
    static_keys = [k for k in all_prompts.keys() if not k.startswith("DYNAMIC")]
    dynamic_keys = [k for k in all_prompts.keys() if k.startswith("DYNAMIC")]
    
    if static_keys:
        # Test static prompt access
        static_key = static_keys[0]
        start = time.time()
        for _ in range(iterations):
            _ = manager[static_key]
        end = time.time()
        print(f"Static Prompt Access ({iterations} iterations): {(end - start) * 1000:.2f} ms")
        print(f"  Per access: {(end - start) * 1000 / iterations:.4f} ms")
    
    if dynamic_keys:
        # Test dynamic prompt access
        dynamic_key = dynamic_keys[0]
        start = time.time()
        for _ in range(iterations):
            _ = manager[dynamic_key]
        end = time.time()
        print(f"Dynamic Prompt Access ({iterations} iterations): {(end - start) * 1000:.2f} ms")
        print(f"  Per access: {(end - start) * 1000 / iterations:.4f} ms")


def cleanup():
    """Clean up benchmark files."""
    import shutil
    if BENCHMARK_DIR.exists():
        shutil.rmtree(BENCHMARK_DIR)


def main():
    print("=" * 50)
    print("PromptMigrate Performance Benchmark")
    print("=" * 50)
    
    try:
        prompt_file, state_file = setup_benchmark_env()
        
        print("\n1. Initialization Performance")
        print("-" * 30)
        benchmark_initialization(prompt_file, state_file)
        
        print("\n2. Migration Performance")
        print("-" * 30)
        migrations = create_test_migrations(num_migrations=5, prompts_per_migration=20)
        with measure_memory("Migrations"):
            benchmark_migrations(prompt_file, state_file, migrations)
        
        print("\n3. Prompt Access Performance")
        print("-" * 30)
        benchmark_prompt_access(prompt_file, state_file)
        
        print("\n4. Memory Usage")
        print("-" * 30)
        with measure_memory("Overall"):
            manager = PromptManager(prompt_file=prompt_file, state_file=state_file)
            if manager.current_rev() is None:
                manager.upgrade()
            
            # Access all prompts once
            all_prompts = manager.load_prompts()
            for key in all_prompts:
                _ = manager[key]
        
    finally:
        cleanup()
    
    print("\nBenchmark completed.")


if __name__ == "__main__":
    main()
