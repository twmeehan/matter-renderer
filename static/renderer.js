import { Vec3, Vec4, Mat4 , WEAVE} from './weave.esm.js'; 

var folderName

// Call init to initialize the engine
WEAVE.init();

////////////////////////////////////////////////////
// Scene
////////////////////////////////////////////////////

// The scene is the root of the object hierarchy
let scene = new WEAVE.Scene();
WEAVE.setActiveScene(scene);

////////////////////////////////////////////////////
// Camera
////////////////////////////////////////////////////

let camera = new WEAVE.Camera(WEAVE.Camera.PERSPECTIVE);
let controls = new WEAVE.CameraController(camera,canvas)
WEAVE.setActiveCamera(camera);
 
////////////////////////////////////////////////////
// Lights
////////////////////////////////////////////////////

let sunLight = new WEAVE.DirectionalLight(new Vec3(-1,-1.3,-0.8),new Vec3(1,1,1),0.8);
let ambientLight = new WEAVE.AmbientLight(new Vec3(1,1,1),0.3);
// To add a light to the scene, push it to the WEAVE.lights array (Max 8)
WEAVE.lights.push(sunLight);
WEAVE.lights.push(ambientLight);

let box = new WEAVE.Box();
box.scale = new Vec3(5,0.01,5);
box.mesh.material = new WEAVE.Material(new Vec3(0.5,0.5,0.5),new Vec3(0,1,0),new Vec3(0,0,1),10);

// Call start to begin the program loop
WEAVE.start();

let animationFrames = [];
document.addEventListener("keydown", e => {
    if (e.key === "d") {
      WEAVE.toggleDebugWindow(WEAVE.scene);
    }
  });

async function loadModel(name) {
    const sizeValue = Number(document.getElementById("size").value) ? Number(document.getElementById("size").value) : 0;
    return await WEAVE.Loader.loadParticleSystem(`/model?name=${encodeURIComponent(folderName)}/${encodeURIComponent(name)}`,'/static/texture.png',sizeValue > 0 ? 0.01*sizeValue : 0.01);
}

export async function loadAnimation() {

    animationFrames = []

    folderName = document.getElementById("modelName").value;
    let response = await fetch(`/animation?name=${encodeURIComponent(folderName)}`);

    const json = await response.json();
    console.log(json);
    const frames = json.frames;
    for (let model of frames) {
        let frame = await loadModel(model)
        frame.name = model;
        animationFrames.push(frame);

    }
    animationFrames.sort((a, b) => {
    const getIndex = name => {
        const match = name.match(/(\d+)/);
        return match ? parseInt(match[1], 10) : 0;
    };
    return getIndex(a.name) - getIndex(b.name);
    });
}

window.loadAnimation = loadAnimation;

let currentFrame = 0;
let lastObject = null;

setInterval(() => {

    // Add next frame
    const next = animationFrames[currentFrame];
    next.visible = true;
    if (lastObject != null) 
        lastObject.visible = false;
    lastObject = next;

    // Advance and wrap
    currentFrame = (currentFrame + 1) % animationFrames.length;
}, 1000 / 30);