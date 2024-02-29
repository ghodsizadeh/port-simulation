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
    def run(self) -> None:
        """
        This method is responsible for running the process.
        """
        pass


class VesselABC(SimpyResourceABC):
    vessel_count: int = 0

    @abstractmethod
    def interact_with_berth(self, berth: simpy.Resource) -> None:
        """
        This method is responsible for the interaction between the vessel and the berth.
        Args:
            berth (simpy.Resource): The berth resource.
        """
        pass
    @classmethod
    @abstractmethod
    def vessel_arrival(cls, env: simpy.Environment, *args, **kwargs) -> None:
        """ 
        This method is responsible for the arrival of the vessel
        and starting point of the simulation.
        Args:
            env (simpy.Environment): The simulation environment.
        """
        pass


class Crane(SimpyResourceABC):
    @abstractmethod
    def interact_with_berth(self, berth: simpy.Resource, vessel: VesselABC) -> None:
        """ 
        This method is responsible for the interaction between the crane and the berth/vessel.
        Args:
            berth (simpy.Resource): The berth resource.
            vessel (VesselABC): The vessel resource.
        """
        pass


class Truck(SimpyResourceABC):
    truck_pool: int = 0
    @abstractmethod
    def interact_with_crane(self, crane: Crane) -> None:
        """
        This method is responsible for the interaction between the truck and the crane.
        Args:
            crane (Crane): The crane resource.
        """
        pass
