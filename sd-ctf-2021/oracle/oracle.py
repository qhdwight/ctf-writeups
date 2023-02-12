#!/usr/bin/env python3

import angr
import claripy

INPUT_FILE = './oracle'

if __name__ == '__main__':
    proj = angr.Project(INPUT_FILE, main_opts={'base_addr': 0})
    flag = claripy.BVS('flag', 0x2A * 8)  # Character count found from reversing, each character is 8 bits
    stdin = angr.SimFileStream(name='stdin', content=flag, has_end=True)
    state = proj.factory.full_init_state(
        args=[INPUT_FILE],
        stdin=stdin,
        add_options={angr.sim_options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
                     angr.sim_options.SYMBOL_FILL_UNCONSTRAINED_REGISTERS}
    )
    sim_manager = proj.factory.simulation_manager(state)
    sim_manager.explore(find=lambda s: b"Good job" in s.posix.dumps(1), avoid=0x0010163b)

    for found in sim_manager.found:
        print(found.solver.eval(flag, cast_to=bytes))
