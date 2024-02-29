from dataclasses import dataclass
import logging

SIMULATION_TIME_IN_MINUTES = 60 * 12


@dataclass(slots=True, frozen=True)
class Config:
    vessel_average_in_minutes: int = 5 * 60
    vessel_container_capacity: int = 150

    berth_count: int = 2

    crane_count: int = 2
    crane_time_in_minutes: int = 3

    truck_count: int = 3
    truck_time_in_minutes: int = 6

    log_level: int = logging.INFO

    simulation_time_in_minutes: int = SIMULATION_TIME_IN_MINUTES




config = Config()


if __name__ == "__main__":
    print(config)
