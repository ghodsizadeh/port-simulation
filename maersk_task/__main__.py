import simpy
from maersk_task.config import config, Config
from maersk_task.port import Port, Vessel, Crane, Truck, Report, env



def setup(env: simpy.Environment, config: Config):
    # Create the berth resource
    berth: simpy.Resource = simpy.Resource(env, capacity=config.berth_count)

    # Create the port
    port = Port(env, berth, Crane.crane_resource, Truck.truck_resource, Report())
    # Create starting vessels
    for _ in range(config.vessels_in_start):
        Vessel(env, port)    
    
    # start the vessel arrival process
    env.process(Vessel.vessel_arrival(env, port))
    # start the simulation
    env.run(until=config.simulation_time_in_minutes)


    print(f"""\033[92m{"="*30} Simulation Report {"="*30}
Duration:  { config.simulation_time_in_minutes//(60*24) } days {config.simulation_time_in_minutes//60} hours and {config.simulation_time_in_minutes%60} minutes
{port.report}
{"="*79}
\033[0m""")
    


if __name__ == "__main__":
    setup(env, config)