let pyodide;

async function startEngine() {
    pyodide = await loadPyodide();

    let response = await fetch("rules.py");
    let pythonCode = await response.text();
    pyodide.runPython(pythonCode);

    wpawn_getLegalMoves = pyodide.globals.get("wpawn_getLegalMoves");
    bpawn_getLegalMoves = pyodide.globals.get("bpawn_getLegalMoves");
    king_getLegalMoves = pyodide.globals.get("king_getLegalMoves");

    get_valid_moves = pyodide.globals.get("get_valid_moves");

    find_best_move = pyodide.globals.get("find_best_move");
    check_winner = pyodide.globals.get("check_winner");

    console.log("Python rules engine connected!");
}

let wpawn_getLegalMoves;
let bpawn_getLegalMoves;
let king_getLegalMoves;
let find_best_move;
let get_valid_moves;
let check_winner;
let currentTurn = "b";
let gameOver = false;
startEngine();





let squares = document.querySelectorAll("td");
let selectedpiece = null;
let result = null;
let orignalsquare = null;

squares.forEach(square => {
    square.addEventListener("click", function () {

        let piece = this.querySelector(".piece");

        //stops if gameover
        if (gameOver) {
            return;
        }

        // First click
        if (selectedpiece === null && piece !== null) {
            if (!piece.classList.contains("bpiece") || currentTurn !== "b") {
                return;
            }
            this.style.filter = "brightness(0.7)";
            orignalsquare = this;

            selectedpiece = piece;

            let board = getBoard();

            result = get_valid_moves(
                pyodide.toPy(board),
                orignalsquare.id
            );

            return;
        }

        else if (selectedpiece === null && piece === null) {
            this.style.filter = "brightness(1)";
        }

        else if (selectedpiece !== null) {
            this.style.filter = "brightness(0.7)";
        }

        // Second click: MOVING
        if (selectedpiece !== null) {

            let possibleMoves = result.toJs();

            if (possibleMoves.includes(this.id)) {
                console.log("Valid move!");

                let existingpiece = this.querySelector(".piece");

                if (existingpiece !== null) {
                    existingpiece.remove();
                }

                this.appendChild(selectedpiece);


                orignalsquare.style.filter = "brightness(1)";
                square.style.filter = "brightness(1)";

                orignalsquare = null;
                selectedpiece = null;
                result = null;
                console.log("PLAYER MOVED!");
                if (checkGameOver()) {
                    return;
                }
                currentTurn = "w";
                computerMove();
                currentTurn = "b";

                return;
            }
            else {
                console.log("Invalid move!");
                selectedpiece = null;
                orignalsquare.style.filter = "brightness(1)";
                square.style.filter = "brightness(1)";
                orignalsquare = null;
                result = null;

            }
        }
    });
});

//Board 
function getBoard() {
    let board = {};

    squares.forEach(square => {
        let piece = square.querySelector(".piece");

        if (piece !== null) {
            board[square.id] = piece.dataset.type;
        }
    });

    return board;
}

//Computer Code
function computerMove() {

    let board = getBoard();

    let move = find_best_move(
        pyodide.toPy(board),
        7
    );
    console.log("AI CHOSE:", move);

    if (move === null) return;

    let start = move.get(0);
    let end = move.get(1);

    let from = document.getElementById(start);
    let to = document.getElementById(end);

    let piece = from.querySelector(".piece");

    let existing = to.querySelector(".piece");

    if (existing !== null) {
        existing.remove();
    }
    to.appendChild(piece);
    //checking if game is over
    checkGameOver();
}

//result of game
function checkGameOver() {

    let board = getBoard();

    let winner = check_winner(pyodide.toPy(board));

    if (winner === "Draw") {
        gameOver = true;
        alert("It's a draw!");
        return true;
    }

    if (winner !== null && winner !== undefined) {
        gameOver = true;
        alert(winner + " wins!");
        return true;
    }

    return false;
}
