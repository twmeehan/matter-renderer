# Steps

## Install matter and matter-renderer

ssh into remote machine using 

```ssh -L 8080:localhost:8080 {netID}@lagrange.cs.rutgers.edu```

then download these repos

https://github.com/larsblatny/matter/

These must be in the same root directory like

Repos
┝matter
┝matter-renderer

## Install dependencies

boost-1.82
openvdb-12.0.0

You can add these manually in your repos folder and specify the path in your cmake command. I think these may not be nessesary if running without vbo objects 

## Run matter

Go to src/tools.hpp and uncomment the line

```#define THREEDIM```

Go to src/mpm.cpp and change the T k_rad to something like the following for a more managable number of particles

```T k_rad = 0.05```

You can also add extra planes if you want a bounding box. As well as changing the height and dimensions of the sand particles

```
sim.plates.push_back(std::make_unique<ObjectPlate>(-1.0, PlateType::left,   BC::NoSlip));
    sim.plates.push_back(std::make_unique<ObjectPlate>(1.0, PlateType::right,  BC::NoSlip));
    sim.plates.push_back(std::make_unique<ObjectPlate>(0.0, PlateType::bottom, BC::NoSlip));
    sim.plates.push_back(std::make_unique<ObjectPlate>(-1.0, PlateType::back,   BC::NoSlip));
    sim.plates.push_back(std::make_unique<ObjectPlate>(1.0, PlateType::front,  BC::NoSlip));
```

Run cmake and the make in the base directory to build the executable. Then run the executable

```./src/mpm```

## Run the renderer

Go to matter-renderer directory and run 

```source matter-renderer-env/bin/activate```

and 

```python3 main.py &```

Open the browser on your local machine to localhost:8080. It should show a 3d enviroment and a header saying OBJ loader.

Put in the name of the MPM output directory (`collapse` for the default project) and specify a particle size for rendering (`10` is good for 5000 particles, `5` if you have even more particles) then click load. 

The animation will take a few seconds to load in, and then will begin playing on repeat.


