# 🍽️ Parallel Pantry: MPI-Based Order Processing System

## 📌 Overview

**Parallel Pantry** is a simulation of a distributed order processing system built using **MPI (Message Passing Interface)** and Python’s **multiprocessing** tools.

The system demonstrates how tasks (orders) can be distributed from a **Master process** to multiple **Worker processes**, processed concurrently, and safely stored in shared memory using synchronization mechanisms.

This project highlights key concepts in **parallel and distributed computing**, including:

- Task distribution using MPI
- Concurrent execution across processes
- Shared memory management
- Race conditions and synchronization using locks

---

## 🧠 System Architecture

- **Master Process (Rank 0)**
  Responsible for generating orders and distributing them to workers.

- **Worker Processes (Rank > 0)**
  Receive orders, process them independently, and store results in shared memory.

- **Shared Memory (`Manager().list()`)**
  Stores processed orders accessible across processes.

- **Lock (`multiprocessing.Lock`)**
  Ensures that only one worker writes to shared memory at a time.

---

## ⚙️ Technologies Used

- Python
- mpi4py
- Open MPI
- multiprocessing

---

## 📁 Project Structure

```
parallel-pantry/
│
├── main.py              # Main script (MPI + multiprocessing logic)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore
└── docs/
    └── notes.md
```

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/parallel-pantry.git
cd parallel-pantry
```

---

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate:

```bash
# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install MPI (Required)

#### Mac (Homebrew)

```bash
brew install open-mpi
```

#### Ubuntu/Debian

```bash
sudo apt install openmpi-bin openmpi-common libopenmpi-dev
```

#### Windows

Install MS-MPI from Microsoft:
https://learn.microsoft.com/en-us/message-passing-interface/microsoft-mpi

---

## ▶️ How to Run

```bash
mpirun -np 4 python main.py
```

- `-np 4` → 1 Master + 3 Workers
- Adjust depending on your system

---

## 🔄 Program Flow

1. Master generates 5–8 orders
2. Orders are distributed to workers using MPI
3. Workers process orders concurrently
4. Results are appended to shared memory
5. Lock ensures safe, synchronized writing
6. Master prints final processed orders

---

## 🔒 Synchronization Demonstration

### ❌ Without Lock

- Race conditions occur
- Data may be inconsistent or corrupted

### ✅ With Lock

- Safe access to shared memory
- Clean and consistent output

---

## 🧪 Sample Output

```
[MASTER] Starting system...
[MASTER] Sending Order_1 to worker 1
[MASTER] Sending Order_2 to worker 2
...

[MASTER] Final processed orders:
['Order_1 processed by worker 1',
 'Order_2 processed by worker 2',
 ...]
```

---

## Team Members & Roles

**Gerald Helbiro Jr.** (@potakaaa) - Lead 1
- Environment setup (MPI + mpi4py)
- Master process logic
- Task distribution
- Lock synchronization

**Hans Matthew Del Mundo** (@hdmGOAT) - Lead 2
- Worker execution logic
- Shared memory implementation (Manager.list)

**Ira Chloie Narisma** (@unripelo) - Lead 3
- Processing delays (time.sleep)
- Testing and quality assurance
- Test reports and analysis

**Vin Marcus Gerebise** (@areeesss) - Lead 4
- Documentation
- Repository organization

---

## 📊 Key Concepts Demonstrated

- Parallel processing
- Distributed task scheduling
- Inter-process communication (MPI)
- Shared memory coordination
- Race conditions and synchronization

---

## 🧾 Notes

- Ensure MPI is properly installed before running
- Always run using `mpirun`, not just `python`
- Reinstall `mpi4py` if MPI is installed after pip

---

## 📌 Submission Requirements

✔️ Complete working code
✔️ Demonstration of concurrency
✔️ Evidence of synchronization (with and without lock)
✔️ Organized repository with meaningful commits

---

## 🎓 Final Thoughts

This project demonstrates how distributed systems coordinate tasks efficiently while maintaining data consistency. It emphasizes the importance of synchronization when multiple processes interact with shared resources.

---
