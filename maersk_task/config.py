from dataclasses import dataclass


SIMULATION_TIME_IN_MINUTES = 60

@dataclass(slots=True, frozen=True)
class Config:
    vessel_average_in_minutes: int = 5 * 6

    berth_count: int = 2

    crane_count: int = 2
    crane_time_in_minutes: int = 3

    truck_count: int = 3
    truck_time_in_minutes: int = 6

    simulation_time_in_minutes: int = SIMULATION_TIME_IN_MINUTES
    



config = Config()


if __name__ == "__main__":
    print(config)