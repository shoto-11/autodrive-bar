# A Second Pair of Eyes: An Attention-Guiding eHMI Approach for Autonomous Vehicles
Code for "A Second Pair of Eyes: An Attention-Guiding eHMI Approach for Autonomous Vehicles".

## Installation
Set up a new virtual environment

```
git clone https://github.com/shoto-11/autodrive-bar.git
cd autodrive-eval
```

## Usage
### Generate car-watching-graphs
```
python make-eval.py "chi_20251123164328_waka"
```
This script generates csv files that indicate 0 or 1 how long they watched cars and pushed button.
The graphs are saved in the evaluated folder.
exaple: please change chi_20251123164328_waka to what you want to evaluate folder


### Generate car-watching-graphs
```
python make-graph-car.py
```
This script generates graphs that indicate how long participants watched each vehicle.
The graphs are saved in the graphs folder, and comparisons are made within matching scenarios.

Vehicle definitions:
car1: Ego vehicle
car2: Small car
car3: Opposing large truck
car4: Small car behind the truck

### Generate button-graph
```
python make-graph-button.py
```
This script generates graphs showing how long participants pressed the button during each moment.
Graphs are saved in the graphs/PrimaryButtonFlag folder and compared across identical scenarios.

### Generate collision-graph
```
python make-graph-collision.py
```
This script generates graphs showing how many participants pressed the button when the car is moving.
Graphs are saved in the graphs/collision folder.

## Customization

## References

## Note
This GitHub project is currently under development.
