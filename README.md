# Traffic_Q_Learning_Agent

## Presentation
https://docs.google.com/presentation/d/1Hmio323lrSvD4h3xU-MN5fP9dEINcDasdfxs1rXZbXY/edit?usp=sharing 

## Final Report
https://docs.google.com/document/d/1nNG7YIrSVACgBUsm745hBQVljJ6f99NiDa_7Wx2qTGg/edit?usp=sharing

## Traffic Flow Video
https://drive.google.com/file/d/17lhfV8YA6saY8PAU_KeSyh2rMZWOhl_i/view?usp=sharing


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


## File Descriptions

`osm.sumocfg`
  - Used to buikd the simulation
  - Links to XML files that map the routes, junctions, and cars

`osm.net.xml`
  - has traffic light data (plus other things) 
  - comment at top has line number for traffic light for our intersection

`7a.rou.xml` 
  - has route info 


## Running the Agnet
 
Will run 10,000 steps (almost 3 hours of traffic) using Q-Learning and the Random Traffic Light Agents
```
python run_new_q.py
```

## Running the Simulation

```
cd tools
sumo-gui -c osm.sumocfg 
```

 
## Resources

Link to download and has video tutorial: https://www.eclipse.org/sumo/

SUMO Python API: https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html

Traffic Light Documentation for API: https://sumo.dlr.de/docs/Tutorials/TraCI4Traffic_Lights.html

Vehicle flow documentation (for the routes): https://sumo.dlr.de/docs/Definition_of_Vehicles,_Vehicle_Types,_and_Routes.html#departlane
