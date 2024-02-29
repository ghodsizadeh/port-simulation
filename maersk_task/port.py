import simpy
from maersk_task.base import VesselABC, TruckABC, CraneABC
from maersk_task.config import config
from dataclasses import dataclass
import random
import logging

logging.basicConfig(level=config.log_level,
                    format="%(levelname)s - %(message)s")    


# add loging name for the critcal logs and warning logs with red and yellow color
logging.addLevelName(logging.CRITICAL, f"\033[1;31mWaiting\033[1;0m")
logging.addLevelName(logging.WARNING, f"\033[1;33mArrival\033[1;0m")

env: simpy.Environment = simpy.Environment()


class Vessel(VesselABC):
    vessel_count: int = 0

    def __init__(self, env: simpy.Environment, port: "Port"):
        self.env: simpy.Environment = env
        self.port: "Port" = port
        Vessel.vessel_count += 1
        self.name = f"Vessel {Vessel.vessel_count}"
        self.containers: simpy.Container = simpy.Container(
            env,
            init=config.vessel_container_capacity,
            capacity=config.vessel_container_capacity,
        )

        
        logging.warning(f"{self.name} arrived at {self.env.now:.2f}")
        self.arrival_time = self.env.now

        self.action: simpy.Process = env.process(self.run())

    def run(self):
        logging.info(f"{self.name} is requesting berth {self.env.now:.2f}")
        yield self.env.process(self.interact_with_berth(self.port.berth))
        logging.info(f"{self.name} is leaving {self.env.now:.2f}")

    def interact_with_berth(self, berth: simpy.Resource):
        


        with self.port.berth.request() as request_berth, self.port.crane.request() as request_crane:
            yield request_berth
            yield request_crane
            waiting_time = self.env.now - self.arrival_time
            logging.critical(f"{self.name} waited for {waiting_time:.2f} minutes")

            logging.info(f"{self.name} is berthing {self.env.now:.2f}")
            # simulate attaching the crane to the vessel
            # actually, we assign the free crane to the vessel
            crane = Crane(self.env, self.port, self)
            yield self.env.process(crane.run())

    @classmethod
    def vessel_arrival(cls, env: simpy.Environment, port: "Port"):
        while True:
            next_arrival = random.expovariate(1 / config.vessel_average_in_minutes)
            logging.warning(f"next arrival in {next_arrival:.2f} minutes")
            yield env.timeout(next_arrival)
            
            Vessel(env, port)

    @property
    def is_empty(self) -> bool:
        return self.containers.level == 0


class Crane(CraneABC):
    crane_resource: simpy.Resource = simpy.Resource(env, capacity=config.crane_count)
    crane_count: int = 0

    def __init__(self, env: simpy.Environment, port: "Port", vessel: Vessel):
        self.env: simpy.Environment = env
        self.port: "Port" = port
        self.process_time = config.crane_time_in_minutes
        Crane.crane_count += 1
        self.name = f"Crane {(Crane.crane_count % config.crane_count) + 1} "
        self.vessel: Vessel = vessel

        # self.action: simpy.Process = env.process(self.run())

    def run(self):
        yield self.env.process(self.interact_with_vessel_and_truck(self.vessel))

    def interact_with_vessel_and_truck(self, vessel: Vessel):
        """
        This method is responsible for the interaction between the crane and the vessel and truck.
        """
        logging.info(f"{self.name} is unloading {self.env.now:.2f}")
        start_time = self.env.now
        while not vessel.is_empty:
            yield self.env.timeout(self.process_time)
            vessel.containers.get(1)
        logging.info(f"{self.name} is Done   {self.env.now:.2f}")
        logging.info(
            f"{self.name} took {self.env.now - start_time} minutes to unload the vessel"
        )


@dataclass(slots=True)
class Port:
    """
    Port environment to manage resources inside the port.
    """

    env: simpy.Environment
    berth: simpy.Resource
    crane: simpy.Resource
    # trucks: list[Truck]


berth: simpy.Resource = simpy.Resource(env, capacity=config.berth_count)


port = Port(env, berth, Crane.crane_resource)
vessel = Vessel(env, port)
env.process(Vessel.vessel_arrival(env, port))
env.run(until=config.simulation_time_in_minutes)
