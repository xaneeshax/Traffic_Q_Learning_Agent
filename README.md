# Traffic_Q_Learning_Agent

## Create Your Own Github Branch

```
git  checkout  -b  branchName
git  add  .
git  commit  -am  "commit message"
git  push
```

## Running SUMO on MacOS Moneterey (M1 chip)

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Hom...)"
brew update

brew install cmake
brew install --cask xquartz
brew install xerces-c fox proj gdal gl2ps

brew install python swig eigen pygobject3 gtk+3 adwaita-icon-theme
python3 -m pip install texttest

git clone --recursive https://github.com/eclipse/sumo
export SUMO_HOME="$PWD/sumo"

cd $SUMO_HOME
mkdir build/cmake-build
cd build/cmake-build
cmake ../..

cd $SUMO_HOME/build/cmake-build
cmake --build . --parallel $(sysctl -n hw.ncpu)
```

## Generating XML Data

Step 1: Run the omsWebWizard to kickstart the SUMO software
```
cd sumo/tools/
python osmWebWizard.py
```
Step 2:
Choose a Portion of the Map and configure traffic flow settings using the selecter tools

Step 3:
Generate the data. This will run a process to create folders containing the `osm.sumoconfig` file and other related XML files

## Running the Simulation

```
sumo-gui -c osm.sumocfg 
```

## File Descriptions

`osm.sumocfg`
  - Used to buikd the simulation
  - Links to XML files that map the routes, junctions, and cars

`osm.net.xml`
  -has traffic light data (plus other things) 
  - comment at top has line number for traffic light for our intersection

`7a.rou.xml` 
  - has route info 

## Resources

Link to download and has video tutorial: https://www.eclipse.org/sumo/

SUMO Python API: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html

Traffic Light Documentation for API: https://sumo.dlr.de/docs/Tutorials/TraCI4Traffic_Lights.html

Vehicle flow documentation (for the routes): https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#departlane

## Running

python run_q.py
^ will run 10,000 steps (almost 3 hours of traffic) using q learning

python run_random.py
^ will run 10,000 steps (almost 3 hours of traffic) using random legal light choices
