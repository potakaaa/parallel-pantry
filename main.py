from mpi4py import MPI
import time
import random

# Initialize MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# ======================
# MASTER PROCESS (rank 0)
# ======================
if rank == 0:
    print("\n[MASTER] Starting Parallel Pantry System...\n")

    # Create 5–8 orders
    orders = [f"Order_{i}" for i in range(1, 9)]

    num_workers = size - 1
    if num_workers <= 0:
        print("[MASTER] No workers available.")
        exit()

    # Send orders to workers (round-robin)
    for i, order in enumerate(orders):
        worker_rank = (i % num_workers) + 1
        print(f"[MASTER] Sending {order} to worker {worker_rank}")
        comm.send(order, dest=worker_rank)

    # Send STOP signal to all workers
    for i in range(1, size):
        comm.send("STOP", dest=i)

    # Collect results from workers
    results_dict = {}

    for _ in orders:
        result = comm.recv(source=MPI.ANY_SOURCE)
        order_id = int(result.split("_")[1].split()[0])
        results_dict[order_id] = result

    print("\n[MASTER] Final processed orders:")
    for i in range(1, len(orders) + 1):
        print(results_dict[i])

# ======================
# WORKER PROCESSES
# ======================
else:
    while True:
        order = comm.recv(source=0)

        if order == "STOP":
            print(f"[WORKER {rank}] Stopping...")
            break

        print(f"[WORKER {rank}] Processing {order}...")

        # Simulate processing time
        time.sleep(random.uniform(0.5, 2.0))

        result = f"{order} processed by worker {rank}"

        # Send result back to master
        comm.send(result, dest=0)