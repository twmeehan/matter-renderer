from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
from pathlib import Path
from plyfile import PlyData
import trimesh
import re


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OUTPUT_DIR = Path("../matter/output")
pattern = re.compile(r"particles_f\d+\.ply")


@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/model")
def serve_or_convert_model(name: str = Query(..., description="Name of the .ply or .obj file")):
    if name.endswith(".obj"):
        obj_path = OUTPUT_DIR / name
        if not obj_path.exists():
            raise HTTPException(status_code=404, detail="OBJ file not found")
        return FileResponse(
            path=obj_path,
            media_type="text/plain",
            filename=name
        )

    ply_path = OUTPUT_DIR / name
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="PLY file not found")

    obj_name = Path(name).with_suffix(".obj").name
    obj_path = OUTPUT_DIR / obj_name

    # If already converted, just return it
    if obj_path.exists():
        return FileResponse(
            path=obj_path,
            media_type="text/plain",
            filename=obj_name
        )

    try:
        obj_bytes = convert_ply_to_obj_memory(ply_path)
        return Response(
            content=obj_bytes,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={obj_name}"
            }
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/animation")
def list_animation_frames(name: str):
    folder = OUTPUT_DIR / name
    if not folder.exists():
        return JSONResponse(status_code=404, content={"error": "Folder not found"})

    pattern = re.compile(r"particles_f\d+\.(ply|obj)")

    matching_files = sorted(
        [f.name for f in folder.iterdir() if pattern.match(f.name)]
    )
    return {"frames": matching_files}

def convert_ply_to_obj_memory(ply_path: Path) -> bytes:
    try:
        plydata = PlyData.read(ply_path)
        vertex_data = plydata['vertex'].data

        # Ensure x and y exist
        if 'x' not in vertex_data.dtype.names or 'y' not in vertex_data.dtype.names:
            raise ValueError("Missing 'x' or 'y' in vertex data")

        x = vertex_data['x']
        y = vertex_data['y']
        z = vertex_data['z'] if 'z' in vertex_data.dtype.names else np.zeros(len(x))  # handle 2D

        vertices = np.stack([x, y, z], axis=1)
        mesh = trimesh.points.PointCloud(vertices)

        # Export to OBJ in memory
        obj_bytes = mesh.export(file_type='obj')
        if isinstance(obj_bytes, str):
            obj_bytes = obj_bytes.encode('utf-8')
        return obj_bytes

    except Exception as e:
        raise RuntimeError(f"Failed to convert {ply_path.name}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
