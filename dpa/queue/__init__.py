"""The code in here is specific to clemson dpa. 

Reimplement these based on how your facility submits tasks to your queue and 
monkey path. Given more time, I'd like to think of a better way to do this.

"""

# -----------------------------------------------------------------------------

import datetime
import os

from dpa.ptask.area import PTaskArea
from dpa.user import current_username

QUEUE = 'cheesyq'

# -----------------------------------------------------------------------------
def queue_submit_cmd(command, queue_name, output_file=None, id_extra=None):
    """Create and submit a shell script with the given command."""
    
    ptask_area = PTaskArea.current()
    ptask_area.provision(QUEUE)
    script_dir = ptask_area.dir(dir_name=QUEUE)

    now = datetime.datetime.now()

    if not id_extra:
        id_extra = now.strftime("%f")

    unique_id = "{u}_{t}_{s}_{e}".format(
        u=current_username(),
        t=now.strftime("%Y_%m_%d_%H_%M_%S"),
        s=ptask_area.spec.replace('=', '_'),
        e=id_extra,
    )
    script_name = unique_id + '.sh'
    log_name = unique_id + '.log'

    script_path = os.path.join(script_dir, script_name)
    log_path = os.path.join(script_dir, log_name)

    with open(script_path, "w") as script_file:
        script_file.write("#!/bin/bash\n")
        script_file.write(command + "\n") 
        script_file.write("chmod 660 " + output_file + "\n")

    os.chmod(script_path, 0770)

    # ---- submit to the queue

    from cheesyq import DPACheesyQ, DPADataLibrary, DPACheesyQTasks

    data_lib = DPADataLibrary.DjangoLibrary(None)

    render_task = DPACheesyQ.RenderTask()
    render_task.taskid = unique_id
    render_task.logFileName = log_path
    render_task.outputFileName = output_file

    data_lib.set(render_task.taskid, render_task)
    render_task.addTask(script_path)

    os.system("cqresubmittask {qn} {tid}".format(
        qn=queue_name,
        tid=render_task.taskid
    ))
        
    print "Submitted task: " + str(render_task.taskid)
