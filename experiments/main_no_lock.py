"""Unsynchronized variant showing race conditions when writing shared state.

Master starts a SyncManager list and workers notify the master of
completion. Master appends results without synchronization.
"""

from mpi4py import MPI
from multiprocessing.managers import SyncManager
import time
import random
import multiprocessing as mp
import os


def setup_process_start_method():
    start_method = 'spawn' if os.name == 'nt' else 'fork'
    mp.set_start_method(start_method, force=True)


def main():
    setup_process_start_method()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    shared_orders = None
    manager_addr = None
    manager_port = None
    manager_auth = None

    if rank == 0:
        if os.name == 'nt':
            shared_orders = []
        else:
            manager_auth = os.urandom(16)
            manager = SyncManager(address=('0.0.0.0', 0), authkey=manager_auth)
            manager.start()

            try:
                import socket
                host = socket.gethostbyname(socket.gethostname())
            except Exception:
                host = '127.0.0.1'

            manager_addr, manager_port = host, manager.address[1]
            shared_orders = manager.list()

    # Share manager connection info with workers
    manager_addr = comm.bcast(manager_addr, root=0)
    manager_port = comm.bcast(manager_port, root=0)
    manager_auth = comm.bcast(manager_auth, root=0)

    if rank != 0 and manager_addr is not None:
        class MPManagerClient(SyncManager):
            pass

        MPManagerClient.register('list')
        mclient = MPManagerClient(address=(manager_addr, manager_port), authkey=manager_auth)
        mclient.connect()
        shared_orders = mclient.list()

    if rank == 0:
        print("\n[MASTER] Starting Parallel Pantry System (NO LOCK - Testing Race Conditions)...\n")

        orders = [f"Order_{i}" for i in range(1, 9)]

        num_workers = size - 1
        if num_workers <= 0:
            print("[MASTER] No workers available.")
            exit()

        for i, order in enumerate(orders):
            worker_rank = (i % num_workers) + 1
            print(f"[MASTER] Sending {order} to worker {worker_rank}")
            comm.send(order, dest=worker_rank)

        for i in range(1, size):
            comm.send("STOP", dest=i)

        print("\n[MASTER] Waiting for workers to complete processing...\n")

        for _ in orders:
            result = comm.recv(source=MPI.ANY_SOURCE)
            print(f"[MASTER] Received completion notification: {result}")
            try:
                shared_orders.append(result)
            except Exception as e:
                print(f"[MASTER] Failed to append to shared memory: {e}")

        print("\n[MASTER] Final processed orders from shared memory:")
        print(f"Total orders completed: {len(shared_orders)}\n")

        if len(shared_orders) > 0:
            for i, completed_order in enumerate(shared_orders, 1):
                print(f"  {i}. {completed_order}")
        else:
            print("  [No orders found in shared memory]")

    else:
        print(f"[WORKER {rank}] Ready to receive orders...\n")

        while True:
            order = comm.recv(source=0)

            if order == "STOP":
                print(f"[WORKER {rank}] Received STOP signal. Exiting...\n")
                break

            print(f"[WORKER {rank}] Received: {order}")

            processing_time = random.uniform(0.5, 2.0)
            print(f"[WORKER {rank}] Processing {order} for {processing_time:.2f} seconds...")
            time.sleep(processing_time)

            result = f"{order} processed by Worker {rank} in {processing_time:.2f}s"

            print(f"[WORKER {rank}] Completed: {order}\n")

            print(f"[WORKER {rank}] Sending result to master (no lock)...\n")
            comm.send(result, dest=0)


if __name__ == '__main__':
    main()
