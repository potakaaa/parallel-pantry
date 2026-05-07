"""Parallel Pantry - MPI master/worker order processing

Master (rank 0) starts a SyncManager server providing a shared list
and lock proxy. Workers connect to the manager, receive orders via MPI,
process them, and notify the master. The master appends results to the
shared list under the manager lock to ensure consistency.
"""

from mpi4py import MPI
from multiprocessing.managers import SyncManager
import multiprocessing as mp
import time
import random
import os


def setup_start_method():
    method = 'spawn' if os.name == 'nt' else 'fork'
    mp.set_start_method(method, force=True)


def start_manager_server():
    """Start a SyncManager server and return (manager, addr, port, authkey)."""
    authkey = os.urandom(16)
    manager = SyncManager(address=('0.0.0.0', 0), authkey=authkey)
    manager.start()
    # Try to find a reachable host IP
    try:
        import socket

        host = socket.gethostbyname(socket.gethostname())
    except Exception:
        host = '127.0.0.1'
    addr, port = host, manager.address[1]
    return manager, addr, port, authkey


def main():
    setup_start_method()
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    shared_orders = None
    lock = None
    manager_addr = None
    manager_port = None
    manager_auth = None

    if rank == 0:
        if os.name == 'nt':
            # Fallback: local list on Windows
            shared_orders = []
            lock = None
        else:
            manager, manager_addr, manager_port, manager_auth = start_manager_server()
            shared_orders = manager.list()
            lock = manager.Lock()
            print(f"[MASTER] Manager server listening on {manager_addr}:{manager_port}", flush=True)

    # Broadcast manager connection info from master
    manager_addr = comm.bcast(manager_addr, root=0)
    manager_port = comm.bcast(manager_port, root=0)
    manager_auth = comm.bcast(manager_auth, root=0)

    # Workers connect to manager server if provided
    if rank != 0 and manager_addr is not None:
        class MPManagerClient(SyncManager):
            pass

        MPManagerClient.register('list')
        MPManagerClient.register('Lock')

        mclient = MPManagerClient(address=(manager_addr, manager_port), authkey=manager_auth)
        mclient.connect()
        try:
            shared_orders = mclient.list()
        except Exception:
            shared_orders = None
        try:
            lock = mclient.Lock()
        except Exception:
            lock = None

    # MASTER
    if rank == 0:
        print("\n[MASTER] Starting Parallel Pantry System...\n", flush=True)

        orders = [f"Order_{i}" for i in range(1, 9)]

        num_workers = size - 1
        if num_workers <= 0:
            print("[MASTER] No workers available.", flush=True)
            return

        # Distribute orders round-robin
        for i, order in enumerate(orders):
            worker_rank = (i % num_workers) + 1
            print(f"[MASTER] Sending {order} to worker {worker_rank}", flush=True)
            comm.send(order, dest=worker_rank)

        # Notify workers to stop after orders sent
        for i in range(1, size):
            comm.send("STOP", dest=i)

        print("\n[MASTER] Waiting for workers to complete processing...\n", flush=True)

        # Collect completion notifications and append to shared list
        for _ in orders:
            result = comm.recv(source=MPI.ANY_SOURCE)
            print(f"[MASTER] Received completion notification: {result}", flush=True)
            try:
                if lock is not None:
                    lock.acquire()
                    try:
                        shared_orders.append(result)
                    finally:
                        lock.release()
                else:
                    shared_orders.append(result)
            except Exception as e:
                print(f"[MASTER] Failed to append to shared memory: {e}", flush=True)

        # Display results
        print("\n[MASTER] Final processed orders from shared memory:", flush=True)
        try:
            total = len(shared_orders) if shared_orders is not None else 0
        except Exception:
            total = 0
        print(f"Total orders completed: {total}\n", flush=True)

        if total > 0:
            for completed_order in shared_orders:
                print(f"  - {completed_order}", flush=True)
        else:
            print("  [No orders found in shared memory]", flush=True)

    # WORKER
    else:
        print(f"[WORKER {rank}] Ready to receive orders...\n", flush=True)

        while True:
            order = comm.recv(source=0)
            if order == "STOP":
                print(f"[WORKER {rank}] Received STOP signal. Exiting...\n", flush=True)
                break

            print(f"[WORKER {rank}] Received: {order}", flush=True)
            processing_time = random.uniform(0.5, 2.0)
            print(f"[WORKER {rank}] Processing {order} for {processing_time:.2f} seconds...", flush=True)
            time.sleep(processing_time)

            result = f"{order} processed by Worker {rank} in {processing_time:.2f}s"
            print(f"[WORKER {rank}] Completed: {order}\n", flush=True)

            # Notify master of completion
            print(f"[WORKER {rank}] Sending result to master...\n", flush=True)
            comm.send(result, dest=0)


if __name__ == '__main__':
    main()
