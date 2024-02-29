import simpy
from maersk_task.base import VesselABC, TruckABC
from maersk_task.config import config
from dataclasses import dataclass
import random


class Vessel(VesselABC):
    vessel_count: int = 0

    def __init__(self, env: simpy.Environment, port: "Port"):
        self.env: simpy.Environment = env
        self.port: "Port" = port
        Vessel.vessel_count += 1
        self.name = f"Vessel {Vessel.vessel_count}"
        self.containers: simpy.Container = simpy.Container(env, init=10, capacity=150)
        self.action: simpy.Process = env.process(self.run())

        print(f"{self.name} arrived at", self.env.now)

    def run(self):
        print(f"{self.name} is requesting berth", self.env.now)
        yield self.env.process(self.interact_with_berth(self.port.berth))
        print(f"{self.name} is leaving", self.env.now)

    def interact_with_berth(self, berth: simpy.Resource):
        with self.port.berth.request() as request:
            yield request
            print(f"{self.name} is berthing", self.env.now)
            while self.containers.level > 0:
                yield self.env.timeout(10)
                print(f"{self.name} is unloading", self.env.now)
                self.containers.get(1)
            print(f"{self.name} is leaving", self.env.now)

    def vessel_arrival(env: simpy.Environment, port: "Port"):
        while True:
            next_arrival = random.expovariate(1 / config.vessel_average_in_minutes)
            print("next arrival in ", next_arrival)
            yield env.timeout(next_arrival)

            Vessel(env, port)


@dataclass(slots=True)
class Port:
    """
    Port environment to manage resources inside the port.
    """

    env: simpy.Environment
    berth: simpy.Resource
    # trucks: list[Truck]


env: simpy.Environment = simpy.Environment()
berth: simpy.Resource = simpy.Resource(env, capacity=config.berth_count)


port = Port(env, berth)
vessel = Vessel(env, port)
env.process(Vessel.vessel_arrival(env, port))
env.run(until=1000)
