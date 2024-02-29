import simpy
from maersk_task.base import VesselABC, TruckABC, CraneABC
from maersk_task.config import config
from dataclasses import dataclass
import random


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
        self.action: simpy.Process = env.process(self.run())

        print(f"{self.name} arrived at", self.env.now)

    def run(self):
        print(f"{self.name} is requesting berth", self.env.now)
        yield self.env.process(self.interact_with_berth(self.port.berth))
        print(f"{self.name} is leaving", self.env.now)

    def interact_with_berth(self, berth: simpy.Resource):
        with self.port.berth.request() as request_berth, self.port.crane.request() as request_crane:
            yield request_berth
            yield request_crane

            print(f"{self.name} is berthing", self.env.now)
            # simulate attaching the crane to the vessel
            # actually, we assign the free crane to the vessel
            crane = Crane(self.env, self.port, self)
            yield self.env.process(crane.run())

    @classmethod
    def vessel_arrival(cls, env: simpy.Environment, port: "Port"):
        while True:
            next_arrival = random.expovariate(1 / config.vessel_average_in_minutes)
            print("next arrival in ", next_arrival)
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
        print(f"{self.name} is unloading", self.env.now)
        start_time = self.env.now
        while not vessel.is_empty:
            yield self.env.timeout(self.process_time)
            vessel.containers.get(1)
        print(f"{self.name} is Done  ", self.env.now)
        print(
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
