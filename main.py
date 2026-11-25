
MEMORY_CAPACITY = 100
next_block_id = 1

memory = [
    {"id": None, "size": MEMORY_CAPACITY, "status": "Free"}
]


# ----------------------------
# Memory allocation algorithms
# ----------------------------

def allocate(requested_size, min_split_size=0):
    """First Fit allocation."""
    global next_block_id

    for index, block in enumerate(memory):
        if block["status"] == "Free" and block["size"] >= requested_size:
            remaining_size = block["size"] - requested_size

            if remaining_size <= min_split_size:
                allocated_size = block["size"]
            else:
                allocated_size = requested_size

            memory[index] = {
                "id": next_block_id,
                "size": allocated_size,
                "requested_size": requested_size,
                "status": "Allocated"
            }

            if remaining_size > min_split_size:
                memory.insert(index + 1, {
                    "id": None,
                    "size": remaining_size,
                    "status": "Free"
                })

            print("First Fit: Allocated", allocated_size, "MB")
            next_block_id += 1
            return True

    print("First Fit: Allocation failed for", requested_size, "MB")
    return False


def best_fit_allocate(requested_size, min_split_size=0):
    """Best Fit allocation."""
    global next_block_id

    best_index = -1
    smallest_size = float("inf")

    for index, block in enumerate(memory):
        if block["status"] == "Free" and block["size"] >= requested_size:
            if block["size"] < smallest_size:
                smallest_size = block["size"]
                best_index = index

    if best_index == -1:
        print("Best Fit: Allocation failed for", requested_size, "MB")
        return False

    block = memory[best_index]
    remaining_size = block["size"] - requested_size

    if remaining_size <= min_split_size:
        allocated_size = block["size"]
    else:
        allocated_size = requested_size

    memory[best_index] = {
        "id": next_block_id,
        "size": allocated_size,
        "requested_size": requested_size,
        "status": "Allocated"
    }

    if remaining_size > min_split_size:
        memory.insert(best_index + 1, {
            "id": None,
            "size": remaining_size,
            "status": "Free"
        })

    print("Best Fit: Allocated", allocated_size, "MB")
    next_block_id += 1
    return True


def worst_fit_allocate(requested_size, min_split_size=0):
    """Worst Fit allocation."""
    global next_block_id

    worst_index = -1
    largest_size = -1

    for index, block in enumerate(memory):
        if block["status"] == "Free" and block["size"] >= requested_size:
            if block["size"] > largest_size:
                largest_size = block["size"]
                worst_index = index

    if worst_index == -1:
        print("Worst Fit: Allocation failed for", requested_size, "MB")
        return False

    block = memory[worst_index]
    remaining_size = block["size"] - requested_size

    if remaining_size <= min_split_size:
        allocated_size = block["size"]
    else:
        allocated_size = requested_size

    memory[worst_index] = {
        "id": next_block_id,
        "size": allocated_size,
        "requested_size": requested_size,
        "status": "Allocated"
    }

    if remaining_size > min_split_size:
        memory.insert(worst_index + 1, {
            "id": None,
            "size": remaining_size,
            "status": "Free"
        })

    print("Worst Fit: Allocated", allocated_size, "MB")
    next_block_id += 1
    return True


# ----------------------------
# Deallocation and coalescing
# ----------------------------

def deallocate(block_id):
    for block in memory:
        if block["id"] == block_id and block["status"] == "Allocated":
            block["status"] = "Free"
            block["id"] = None
            block.pop("requested_size", None)
            print("Block", block_id, "released successfully")
            return True

    print("Deallocation failed: Block", block_id, "not found")
    return False


def coalesce():
    """Merge adjacent free blocks."""
    index = 0

    while index < len(memory) - 1:
        current_block = memory[index]
        next_block = memory[index + 1]

        if current_block["status"] == "Free" and next_block["status"] == "Free":
            current_block["size"] += next_block["size"]
            memory.pop(index + 1)
            print("Two free blocks merged successfully")
        else:
            index += 1


def reset_memory():
    global memory, next_block_id

    memory = [
        {"id": None, "size": MEMORY_CAPACITY, "status": "Free"}
    ]
    next_block_id = 1


def get_allocation_function(algorithm):
    if algorithm == "First Fit":
        return allocate
    if algorithm == "Best Fit":
        return best_fit_allocate
    if algorithm == "Worst Fit":
        return worst_fit_allocate

    raise ValueError("Unknown allocation algorithm: " + algorithm)


# ----------------------------
# Workload scenarios
# ----------------------------

small_requests = [2, 3, 5, 4, 2, 6]
large_requests = [20, 25, 30, 15, 25]
mixed_requests = [5, 20, 3, 25, 10, 2, 30]


def get_workload(workload_type):
    if workload_type == "small":
        return small_requests
    if workload_type == "large":
        return large_requests
    if workload_type == "mixed":
        return mixed_requests

    raise ValueError("Unknown workload: " + workload_type)


# ----------------------------
# Allocation-only experiments
# ----------------------------

def run_experiment(algorithm, workload_type, min_split_size=0):
    reset_memory()

    requests = get_workload(workload_type)
    allocation_function = get_allocation_function(algorithm)

    successful_allocations = 0
    failed_allocations = 0

    print("\n----------------------------")
    print("Algorithm:", algorithm)
    print("Workload:", workload_type)
    print("Threshold:", min_split_size, "MB")
    print("----------------------------")

    for request in requests:
        success = allocation_function(request, min_split_size)

        if success:
            successful_allocations += 1
        else:
            failed_allocations += 1

    total_free_memory = sum(
        block["size"] for block in memory
        if block["status"] == "Free"
    )

    largest_free_block = max(
        (block["size"] for block in memory
         if block["status"] == "Free"),
        default=0
    )

    if total_free_memory > 0:
        external_fragmentation = (
                                         1 - largest_free_block / total_free_memory
                                 ) * 100

        print(
            "External Fragmentation:",
            round(external_fragmentation, 2), "%"
        )
    else:
        external_fragmentation = None
        print("External Fragmentation: N/A (No free memory)")

    internal_fragmentation = sum(
        block["size"] - block["requested_size"]
        for block in memory
        if block["status"] == "Allocated"
    )

    allocated_memory = sum(
        block["size"] for block in memory
        if block["status"] == "Allocated"
    )

    memory_utilization = (
                                 allocated_memory / MEMORY_CAPACITY
                         ) * 100

    print("Internal Fragmentation:", internal_fragmentation, "MB")
    print("Allocated Memory:", allocated_memory, "MB")
    print("Memory Utilization:", round(memory_utilization, 2), "%")
    print("Successful allocations:", successful_allocations)
    print("Failed allocations:", failed_allocations)
    print("Final Memory Pool:")
    print(memory)

    return successful_allocations, failed_allocations


# ----------------------------
# Standalone deallocation test
# ----------------------------

def run_fragmentation_test():
    print("\n===== STANDALONE DEALLOCATION TEST =====")

    reset_memory()

    for size in [20, 15, 10, 25, 10]:
        allocate(size)

    print("\nBefore deallocation:")
    print(memory)

    deallocate(2)
    deallocate(4)
    coalesce()

    print("\nAfter deallocation:")
    print(memory)

    free_blocks = [
        block["size"] for block in memory
        if block["status"] == "Free"
    ]

    total_free = sum(free_blocks)
    largest_free = max(free_blocks, default=0)

    if total_free > 0:
        fragmentation = (
                                1 - largest_free / total_free
                        ) * 100

        print("External Fragmentation:", round(fragmentation, 2), "%")
    else:
        print("External Fragmentation: N/A (No free memory)")


# ----------------------------
# Dynamic experiments
# ----------------------------

SCENARIO_1_EVENTS = [
    ("allocate", 20),
    ("allocate", 15),
    ("allocate", 10),
    ("allocate", 25),
    ("allocate", 10),
    ("free", 2),
    ("free", 4),
    ("allocate", 18),
    ("allocate", 12),
    ("free", 1),
    ("free", 3),
    ("allocate", 22)
]


SCENARIO_2_EVENTS = [
    ("allocate", 12),
    ("allocate", 18),
    ("allocate", 8),
    ("allocate", 22),
    ("allocate", 14),
    ("allocate", 16),
    ("free", 2),
    ("free", 4),
    ("allocate", 17),
    ("allocate", 20),
    ("free", 1),
    ("free", 3),
    ("allocate", 25)
]


def run_dynamic_experiment(algorithm, min_split_size, scenario_name, events):
    reset_memory()

    allocation_function = get_allocation_function(algorithm)

    successful_allocations = 0
    failed_allocations = 0

    print("\n================================")
    print(scenario_name, "-", algorithm)
    print("Threshold:", min_split_size, "MB")
    print("================================")

    for action, value in events:

        if action == "allocate":
            if allocation_function(value, min_split_size):
                successful_allocations += 1
            else:
                failed_allocations += 1

        elif action == "free":
            deallocate(value)
            coalesce()

    total_free = sum(
        block["size"] for block in memory
        if block["status"] == "Free"
    )

    largest_free = max(
        (block["size"] for block in memory
         if block["status"] == "Free"),
        default=0
    )

    internal = sum(
        block["size"] - block["requested_size"]
        for block in memory
        if block["status"] == "Allocated"
    )

    allocated_memory = sum(
        block["size"] for block in memory
        if block["status"] == "Allocated"
    )

    memory_utilization = (
                                 allocated_memory / MEMORY_CAPACITY
                         ) * 100

    if total_free > 0:
        external = (
                           1 - largest_free / total_free
                   ) * 100
        external_result = round(external, 2)
    else:
        external = None
        external_result = None

    print("\nFinal Memory:", memory)
    print("Total Free Memory:", total_free, "MB")
    print("Largest Free Block:", largest_free, "MB")

    if external is not None:
        print("External Fragmentation:", round(external, 2), "%")
    else:
        print("External Fragmentation: N/A (No free memory)")

    print("Internal Fragmentation:", internal, "MB")
    print("Allocated Memory:", allocated_memory, "MB")
    print("Memory Utilization:", round(memory_utilization, 2), "%")
    print("Successful allocations:", successful_allocations)
    print("Failed allocations:", failed_allocations)

    return {
        "scenario": scenario_name,
        "algorithm": algorithm,
        "threshold": min_split_size,
        "external_fragmentation": external_result,
        "internal_fragmentation": internal,
        "allocated_memory": allocated_memory,
        "memory_utilization": round(memory_utilization, 2),
        "successful_allocations": successful_allocations,
        "failed_allocations": failed_allocations
    }


# ----------------------------
# Run all experiments
# ----------------------------

if __name__ == "__main__":

    algorithms = ["First Fit", "Best Fit", "Worst Fit"]
    workloads = ["small", "large", "mixed"]
    thresholds = [0, 2, 5, 10]

    print("Small Workload:", get_workload("small"))
    print("Large Workload:", get_workload("large"))
    print("Mixed Workload:", get_workload("mixed"))

    print("\n========== ALLOCATION-ONLY EXPERIMENTS ==========")

    for threshold in thresholds:
        print("\n===== THRESHOLD:", threshold, "MB =====")

        for algorithm in algorithms:
            for workload in workloads:
                print("\n", algorithm, "-", workload)
                run_experiment(algorithm, workload, threshold)

    run_fragmentation_test()

    print("\n========== DYNAMIC EXPERIMENTS: SCENARIO 1 ==========")

    scenario_1_results = []

    for threshold in thresholds:
        for algorithm in algorithms:
            result = run_dynamic_experiment(
                algorithm,
                threshold,
                "Scenario 1",
                SCENARIO_1_EVENTS
            )

            scenario_1_results.append(result)

    print("\n========== DYNAMIC EXPERIMENTS: SCENARIO 2 ==========")

    scenario_2_results = []

    for threshold in thresholds:
        for algorithm in algorithms:
            result = run_dynamic_experiment(
                algorithm,
                threshold,
                "Scenario 2",
                SCENARIO_2_EVENTS
            )

            scenario_2_results.append(result)

    print("\n========== EXPERIMENT SUMMARY ==========")

    print(
        "Allocation-only experiments:",
        len(thresholds) * len(algorithms) * len(workloads)
    )

    print("Dynamic Scenario 1 experiments:", len(scenario_1_results))
    print("Dynamic Scenario 2 experiments:", len(scenario_2_results))

    print(
        "Total dynamic experiments:",
        len(scenario_1_results) + len(scenario_2_results)
    )

    print("\nAll experiments completed.")
