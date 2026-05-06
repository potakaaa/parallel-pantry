from mpi4py import MPI
from multiprocessing import Manager
import time
import random
import multiprocessing as mp

# VERSION WITHOUT LOCK SYNCHRONIZATION - Used to demonstrate race conditions
# This file shows what happens when multiple processes write to shared memory
# simultaneously without proper synchronization

if __name__ == '__main__':
    mp.set_start_method('fork', force=True)

    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Create shared memory only on master process (NO LOCK)
    if rank == 0:
        manager = Manager()
        shared_orders = manager.list()
    else:
        shared_orders = None

    # ======================
    # MASTER PROCESS (rank 0)
    # ======================
    if rank == 0:
        print("\n[MASTER] Starting Parallel Pantry System (NO LOCK - Testing Race Conditions)...\n")

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

        # Wait for all workers to finish processing
        print("\n[MASTER] Waiting for workers to complete processing...\n")
        
        # Collect results from workers via MPI
        for _ in orders:
            result = comm.recv(source=MPI.ANY_SOURCE)
            # NO LOCK - Writing directly without synchronization
            print(f"[MASTER] [NO LOCK] Writing result to shared memory...")
            shared_orders.append(result)
            print(f"[MASTER] Total orders in shared memory: {len(shared_orders)}\n")

        # Display results from shared memory
        print("\n[MASTER] Final processed orders from shared memory:")
        print(f"Total orders completed: {len(shared_orders)}\n")
        
        if len(shared_orders) > 0:
            for i, completed_order in enumerate(shared_orders, 1):
                print(f"  {i}. {completed_order}")
        else:
            print("  [No orders found in shared memory]")

    # ======================
    # WORKER PROCESSES
    # ======================
    else:
        print(f"[WORKER {rank}] Ready to receive orders...\n")
        
        while True:
            order = comm.recv(source=0)

            if order == "STOP":
                print(f"[WORKER {rank}] Received STOP signal. Exiting...\n")
                break

            print(f"[WORKER {rank}] Received: {order}")

            # Simulate processing time (real-world delay)
            # Different delays to show varied completion times
            processing_time = random.uniform(0.5, 2.0)
            print(f"[WORKER {rank}] Processing {order} for {processing_time:.2f} seconds...")
            time.sleep(processing_time)

            # Create result
            result = f"{order} processed by Worker {rank} in {processing_time:.2f}s"
            
            print(f"[WORKER {rank}] ✓ Completed: {order}\n")

            # Send result back to master via MPI (NO synchronization)
            print(f"[WORKER {rank}] Sending result to master (no lock)...\n")
            comm.send(result, dest=0)
