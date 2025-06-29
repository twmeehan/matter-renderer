from fastapi import FastAPI, HTTPException, Query, Response, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
from pathlib import Path
from plyfile import PlyData
import trimesh


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MODELS_DIR = Path("../matter/output/collapse")

@app.get("/", response_class=HTMLResponse)
def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/model")
def convert(name: str = Query(..., description="Name of the .ply file without extension")):
    ply_path = MODELS_DIR / f"{name}.ply"
    if not ply_path.exists():
        raise HTTPException(status_code=404, detail="PLY file not found")

    try:
        obj_bytes = convert_ply_to_obj_memory(ply_path)
        return Response(
            content=obj_bytes,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={name}.obj"
            }
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


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
