let pyodide;

async function startEngine() {
    pyodide = await loadPyodide();

    let response = await fetch("engine.py");
    let pythonCode = await response.text();

    pyodide.runPython(pythonCode);

    getLegalMoves = pyodide.globals.get("get_legal_moves");

    console.log("Python engine connected!");
}

let getLegalMoves;
startEngine();

