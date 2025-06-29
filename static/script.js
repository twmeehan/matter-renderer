async function loadModel() {
    const name = document.getElementById("modelName").value;
    const res = await fetch(`/model?name=${encodeURIComponent(name)}`);
    if (res.ok) {
        const objText = await res.text();
        console.log("Received OBJ:", objText.slice(0, 200)); // preview
        alert("OBJ file loaded successfully!");
    } else {
        alert("Failed to load OBJ file.");
    }
}
