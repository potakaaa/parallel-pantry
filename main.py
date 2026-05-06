from mpi4py import MPI
from multiprocessing import Manager, Lock
import time
import random
import multiprocessing as mp

# Critical: Create Manager OUTSIDE the main function and before MPI initialization
# This ensures it's available to all MPI processes on the master
if __name__ == '__main__':
    mp.set_start_method('fork', force=True)

    # Initialize MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Create shared memory only on master process
    if rank == 0:
        manager = Manager()
        shared_orders = manager.list()
        lock = Lock()
    else:
        shared_orders = None
        lock = None

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

        # Wait for all workers to finish processing
        print("\n[MASTER] Waiting for workers to complete processing...\n")
        
        # Collect results from workers via MPI
        for _ in orders:
            result = comm.recv(source=MPI.ANY_SOURCE)
            # Use lock for thread-safe access to shared_orders
            with lock:
                print(f"[MASTER] [LOCK ACQUIRED] Storing result in shared memory...")
                shared_orders.append(result)
                print(f"[MASTER] [LOCK RELEASED] Total orders in shared memory: {len(shared_orders)}\n")

        # Display results from shared memory
        print("\n[MASTER] Final processed orders from shared memory:")
        print(f"Total orders completed: {len(shared_orders)}\n")
        
        if len(shared_orders) > 0:
            for completed_order in shared_orders:
                print(f"  ✓ {completed_order}")
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
            processing_time = random.uniform(0.5, 2.0)
            print(f"[WORKER {rank}] Processing {order} for {processing_time:.2f} seconds...")
            time.sleep(processing_time)

            # Create result
            result = f"{order} processed by Worker {rank} in {processing_time:.2f}s"
            
            print(f"[WORKER {rank}] ✓ Completed: {order}\n")

            # Send result back to master via MPI
            print(f"[WORKER {rank}] Sending result to master...\n")
            comm.send(result, dest=0)