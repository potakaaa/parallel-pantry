from mpi4py import MPI
from multiprocessing import Lock, Manager

manager = Manager()
shared_list = manager.list()
lock = Lock()

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    print("[MASTER] Starting system...")

    orders = [f"Order_{i}" for i in range(1, 9)]

    for i, order in enumerate(orders):
        worker_rank = (i % (size - 1)) + 1
        comm.send(order, dest=worker_rank)

    for i in range(1, size):
        comm.send("STOP", dest=i)

    # wait a bit (simple sync)
    import time
    time.sleep(2)

    print("\n[MASTER] Final processed orders:")
    print(list(shared_list))

# Member 2 expands here
else:
    while True:
        order = comm.recv(source=0)

        if order == "STOP":
            break

        # simulate processing (Member 3 will improve)
        result = f"{order} processed by worker {rank}"

        # 🔒 critical section
        with lock:
            shared_list.append(result)