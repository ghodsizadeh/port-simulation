from dataclasses import dataclass
import logging

SIMULATION_TIME_IN_MINUTES = 60 * 24 * 70


@dataclass(slots=True, frozen=True)
class Config:
    vessel_average_in_minutes: int = 5 * 60 
    vessel_container_capacity: int = 150

    berth_count: int = 2

    # crane count should be equal to the berth count
    crane_count: int = 2 
    crane_time_in_minutes: int = 3

    truck_count: int = 3
    truck_time_in_minutes: int = 6

    # Options: DEBUG, *INFO*, WARNING, CRITICAL
    log_level: int = logging.INFO

    simulation_time_in_minutes: int = SIMULATION_TIME_IN_MINUTES




config = Config()


if __name__ == "__main__":
    print(config)
