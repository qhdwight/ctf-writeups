import angr
import claripy


INPUT_FILE = './oracle'
AVOID_ADDR = (0x0010163b)
FLAG_CONTENT_LENGTH = 42


def goal(state: angr.SimState):
    """Check stdout for success print out"""
    return b"Good job" in state.posix.dumps(1)


proj = angr.Project(INPUT_FILE, main_opts={'base_addr': 0x0})
flag = claripy.BVS('flag', FLAG_CONTENT_LENGTH * 8)
stdin = angr.SimFileStream(name='stdin', content=flag, has_end=True)
state = proj.factory.full_init_state(
    args=[INPUT_FILE],
    stdin=stdin,
    add_options={angr.sim_options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                 angr.sim_options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
)
sim_manager = proj.factory.simulation_manager(state)
sim_manager.explore(find=goal, avoid=AVOID_ADDR)

for found in sim_manager.found:
    print(found.solver.eval(flag, cast_to=bytes))
