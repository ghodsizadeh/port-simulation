import simpy
from maersk_task.base import VesselABC, TruckABC, CraneABC
from maersk_task.config import config
from dataclasses import dataclass
import random
import logging

logging.basicConfig(level=config.log_level, format="%(levelname)s - %(message)s")


# add loging name for the critcal logs and warning logs with red and yellow color
logging.addLevelName(logging.CRITICAL, "\033[1;31mWaiting\033[1;0m")
logging.addLevelName(logging.WARNING, "\033[1;33mArrival\033[1;0m")

env: simpy.Environment = simpy.Environment()


class Vessel(VesselABC):
    vessel_count: int = 0

    def __init__(self, env: simpy.Environment, port: "Port"):
        self.env: simpy.Environment = env
        self.port: "Port" = port
        Vessel.vessel_count += 1
        self.port.report.vessel_count = Vessel.vessel_count
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
            self.port.report.total_waiting_time += waiting_time
            logging.critical(f"{self.name} waited for {waiting_time:.2f} minutes")

            logging.info(f"{self.name} is berthing {self.env.now:.2f}")
            # simulate attaching the crane to the vessel
            # actually, we assign the free crane to the vessel
            crane = Crane(self.env, self.port, self)
            yield self.env.process(crane.run())
        self.port.report.vessel_done += 1

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
            with self.port.truck.request() as request_truck:
                yield request_truck
                truck = Truck(self.env, self.port)
                yield self.env.process(truck.run())
                vessel.containers.get(1)
                # yield self.env.process(truck.run())

        logging.info(f"{self.name} is Done   {self.env.now:.2f}")
        logging.info(
            f"{self.name} took {self.env.now - start_time} minutes to unload the vessel"
        )


class Truck(TruckABC):
    truck_resource: simpy.Resource = simpy.Resource(env, capacity=config.truck_count)
    truck_count: int = 0

    def __init__(self, env: simpy.Environment, port: "Port"):
        self.env: simpy.Environment = env

        self.port: "Port" = port
        Truck.truck_count += 1
        self.name = f"Truck {Truck.truck_count%config.truck_count + 1}"
        # self.action: simpy.Process = env.process(self.run())

    def run(self):
        """
        Pickup the container from the port and comeback in truck_time_in_minutes
        """
        logging.debug(f"{self.name} is requesting container {self.env.now:.2f}")
        yield self.env.timeout(config.truck_time_in_minutes)
        # self.port.truck.release(self)


@dataclass(slots=True)
class Report:
    """
    Report class to keep track of the simulation.
    """

    vessel_count: int = 0
    vessel_done: int = 0

    # this is the total waiting time of all the vessels that went through the port
    # because we don't know the waiting time of the vessels that are still in the queue
    total_waiting_time: float = 0

    @property
    def average_waiting_time(self) -> float:
        return self.total_waiting_time / self.vessel_done if self.vessel_done else 0

    @property
    def remaining_vessels(self) -> int:
        return self.vessel_count - self.vessel_done

    def __str__(self):
        return f"""Vessels: {self.vessel_count}
Vessels Done: {self.vessel_done}
Vessels in Queue: {self.remaining_vessels}
Average waiting time: {self.average_waiting_time:.0f} minutes |  {self.average_waiting_time//(60*24):.0f} days {self.average_waiting_time//60:.0f} hours and {self.average_waiting_time%60:.0f} minutes"""


@dataclass(slots=True)
class Port:
    """
    Port environment to manage resources inside the port.
    """

    env: simpy.Environment
    berth: simpy.Resource
    crane: simpy.Resource
    truck: simpy.Resource

    report: Report


# berth: simpy.Resource = simpy.Resource(env, capacity=config.berth_count)


# port = Port(env, berth, Crane.crane_resource, Truck.truck_resource, Report())
# vessel = Vessel(env, port)
# env.process(Vessel.vessel_arrival(env, port))
# env.run(until=config.simulation_time_in_minutes)

# print(port.report,"average_waiting_time ~=",port.report.average_waiting_time//60)
