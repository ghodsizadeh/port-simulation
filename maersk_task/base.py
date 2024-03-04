# create an abstract class for the all the simpy resources that will be used in the simulation
import simpy
from abc import ABC, abstractmethod


class SimpyResourceABC(ABC):
    @abstractmethod
    def __init__(self, env: simpy.Environment, *args, **kwargs):
        """
        Initialize the Base class.
        Args:
            env (simpy.Environment): The simulation environment.
        """
        pass

    @abstractmethod
    def run(self):
        """
        This method is responsible for running the process.
        """
        pass


class VesselABC(SimpyResourceABC):
    vessel_count: int = 0

    @abstractmethod
    def interact_with_berth(self, berth: simpy.Resource):
        """
        This method is responsible for the interaction between the vessel and the berth.
        Args:
            berth (simpy.Resource): The berth resource.
        """
        pass

    @classmethod
    @abstractmethod
    def vessel_arrival(cls, env: simpy.Environment, *args, **kwargs):
        """
        This method is responsible for the arrival of the vessel
        and starting point of the simulation.
        Args:
            env (simpy.Environment): The simulation environment.
        """
        pass

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        """
        This property is responsible for checking if the container is empty.
        """
        pass


class CraneABC(SimpyResourceABC):
    @abstractmethod
    def interact_with_vessel_and_truck(self, vessel: VesselABC, truck: "TruckABC"):
        """
        This method is responsible for the interaction between the crane and the berth/vessel.
        Args:
            vessel (VesselABC): The vessel resource.
        """
        pass


class TruckABC(SimpyResourceABC):
    pass
