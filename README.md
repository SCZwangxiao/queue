This is a queuing script that can automatically monitor GPU information
and run your shell command when GPU condition is satisfied.

## Features
- Circularly monitor average gpu utilization rate and free memory within a fixed duration.

- Run your command when gpu satisfies certain conditions:
    - gpu utilization rate <= threshold
    - gpu free memory >= threshold
    - condition-satisfied gpu number >= threshold

- Send e-mail to inform you:
    - when running your command
    - when error occurred
    - when your command finfished

## Installation
Packages
- pynvml, numpy

E-mail
- change the send_mail( ) function in `queue_script.py`.

## Quick start

- File structure:  

        /queue 
            queue_script.py  
            user.py (user defined)  
            *.log (automatically generated)  
            README.md

- Parpare your code and conda environment.

- Create `queue/user.py`, and define your own command function and user name like following:
    ```python
    import subprocess
    import numpy
    ############################ Edit your server name ############################
    COMPUTER_NAME = 'Computer X'
    ###############################################################################

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
        ############################## Edit your command ##############################
        cmd = "python /test.py"
        cwd = "/home/share/name"
        # Generating shell command
        for gid in range(len(avg_free_memory)):
            if gid not in free_gpu_id:
                avg_free_memory[gid] = 0
        max_mem_id = np.argmax(avg_free_memory)
        CMD_prefix = 'CUDA_VISIBLE_DEVICES=%d ' % max_mem_id    # use GPU with maximum GPU memory
        CMD = CMD_prefix + cmd
        ###############################################################################

        # launch subprocess
        task = subprocess.Popen(CMD, shell=True, cwd=cwd, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                universal_newlines=True)  # if universal_newlines=False the output will be in binary format
        return_code = task.poll()
        task_out, task_err = task.communicate()
        return return_code, task_out, task_err
    ```

- Run the queue script:

    ```bash
    python queue_script.py --monitor-interval 600 --measure-duration 10 --min-memory 5000 --max-util 20 --min-gpu 1
    ```
    This command means:  
    - The script will check conditions every `600` seconds.
    - Run command defined in `user.py` when there is at least `1` GPU with more than `5000MB` free memory and less than `20` utilization rate averaged in `10` seconds. 