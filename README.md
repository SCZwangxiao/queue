This is a queuing script that can automatically monitor GPU info
and run your program when condition satisfied.

## Features
automatically monitor gpu utilization rate and free memory withn a fixed duration

run your command when gpu satisfy your condition:
- gpu utilization rate <= threshold
- gpu free memory >= threshold
- condition-satisfied gpu number >= threshold

send e-mail to inform you:
- when running your command
- when error occurred
- when your command finfished

## Installation
packages
- pynvml, numpy

e-mail
- change the send_mail() function

## Quick start

define your own command function and user name in `./user.py`:
```python
<<<<<<< HEAD
import subprocess
import numpy

=======
import np
>>>>>>> c3fd59f482967299b142fdd0147bb62ce392e304
COMPUTER_NAME = 'Computer X'

def run_command(free_gpu_id, avg_free_memory, avg_gpu_util):
    """
    Input:
        free_gpu_id: numpy.array(int), id of gpu which satisfy the condition
        avg_free_memory: numpy.array(int), len=gpu_num
        avg_gpu_util: numpy.array(int), len=gpu_num
    Output:
        return_code: int, 0 for success, else failure
        task_out: str, stdout of the command
        task_err: str, stderr of the command
    """
    ####### command #######
    cmd = "python /test.py"
    cwd = "/home/share/name"
    # Generating shell command
    for gid in range(len(avg_free_memory)):
        if gid not in free_gpu_id:
            avg_free_memory[gid] = 0
    max_mem_id = np.argmax(avg_free_memory)
    CMD_prefix = 'CUDA_VISIBLE_DEVICES=%d ' % max_mem_id    # use GPU with maximum GPU memory
    CMD = CMD_prefix + cmd

    # launch subprocess
    task = subprocess.Popen(CMD, shell=True, cwd=cwd, 
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                            universal_newlines=True)  # if universal_newlines=False the output will be in binary format
    return_code = task.poll()
    task_out, task_err = task.communicate()
    return return_code, task_out, task_err
```

run the queue script:
```bash
python queue_script.py --monitor-interval 10 --min-memory 5000 --max-util 20 --min-gpu 1
```