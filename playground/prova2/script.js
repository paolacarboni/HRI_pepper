// Define image sets (no changes needed here)
const imageSets = {
    fruits: {
        1: 'images/fruit_images/apple.jpg', 2: 'images/fruit_images/banana.jpg', 3: 'images/fruit_images/orange.jpg',
        4: 'images/fruit_images/pear.jpg', 5: 'images/fruit_images/kiwi.jpg', 6: 'images/fruit_images/peach.jpg',
        7: 'images/fruit_images/cherry.jpg', 8: 'images/fruit_images/strawberry.jpg', 9: 'images/fruit_images/blueberry.jpg',
        10: 'images/fruit_images/watermelon.jpg', 11: 'images/fruit_images/raspberry.jpg', 12: 'images/fruit_images/apricot.jpg',
        13: 'images/fruit_images/coconut.jpg', 14: 'images/fruit_images/lemon.jpg', 15: 'images/fruit_images/grapes.jpg',
        16: 'images/fruit_images/mango.jpg', 17: 'images/fruit_images/papaya.jpg', 18: 'images/fruit_images/plum.jpg',
        19: 'images/fruit_images/pomegranate.jpg', 20: 'images/fruit_images/pineapple.jpg'
    },
    music: {
        1: 'images/music_images/campane_tubolari.jpg', 2: 'images/music_images/scacciapensieri.jpg', 3: 'images/music_images/maracas.jpg',
        4: 'images/music_images/glockenspiel.jpg', 5: 'images/music_images/cembalo.jpg', // Example: Changed duplicate scacciapensieri
        6: 'images/music_images/microphone.jpg', 7: 'images/music_images/cello.jpg', 8: 'images/music_images/electric_guitar.jpg',
        9: 'images/music_images/drum_kit.jpg', 10: 'images/music_images/triangle.jpg', 11: 'images/music_images/xylophone.jpg', // Example: Added an image for key 11
        12: 'images/music_images/kalimba.jpg', 13: 'images/music_images/bongos.jpg', 14: 'images/music_images/trumpet.jpg',
        15: 'images/music_images/ukulele.jpg', 16: 'images/music_images/armonica.jpg', 17: 'images/music_images/clarinet.jpg',
        18: 'images/music_images/flute.jpg', 19: 'images/music_images/mandolin.jpg', 20: 'images/music_images/tamburine.jpg',
        21: 'images/music_images/acoustic_guitar.jpg', 22: 'images/music_images/piano.jpg' // Note: You only use up to key 20 if max pairs is 20
    },
    gardening: {
        1: 'images/gardening_images/peperoni.jpg', 2: 'images/gardening_images/melone.jpg', 3: 'images/gardening_images/ravanelli.jpg',
        4: 'images/gardening_images/broccolo.jpg', 5: 'images/gardening_images/zucca.jpg', 6: 'images/gardening_images/soia.jpg',
        7: 'images/gardening_images/patata.jpg', 8: 'images/gardening_images/pianta.jpg', 9: 'images/gardening_images/guanti.jpg',
        10: 'images/gardening_images/spandiconcime.jpg', 11: 'images/gardening_images/radish.jpg', 12: 'images/gardening_images/tubo.jpg',
        13: 'images/gardening_images/carrot.jpg', 14: 'images/gardening_images/salad.jpg', 15: 'images/gardening_images/germogli.jpg',
        16: 'images/gardening_images/seeds.jpg', 17: 'images/gardening_images/rastrello.jpg', 18: 'images/gardening_images/annaffiatoio.jpg',
        19: 'images/gardening_images/pala.jpg', 20: 'images/gardening_images/carriola.jpg' // Example: Added images for 19, 20
    }
};

// **** REMOVE hardcoded passion ****
// const SELECTED_PASSION = 'music';
let SELECTED_PASSION = null; // Initialize to null, will be set by WebSocket

// Game configuration - cardImages will be set dynamically
const config = {
    difficulties: {
        'very-easy': { rows: 2, cols: 3 },
        'easy': { rows: 3, cols: 4 },
        'medium': { rows: 4, cols: 5 },
        'hard': { rows: 5, cols: 6 },
        'very-hard': { rows: 5, cols: 8 }
    },
    // **** cardImages will be set after theme is received ****
    cardImages: null, // Set later
    cardBack: 'images/card_back.jpg',
    emptyCard: 'images/empty_card.jpg'
};

// Game state (no changes needed here)
let gameState = {
    difficulty: null,
    currentTheme: 'default', // This isn't really used now, SELECTED_PASSION is key
    board: [],
    faceUp: [],
    matchedPairs: [],
    playerScore: 0,
    computerScore: 0,
    playerTurn: true,
    firstCard: null,
    waiting: false,
    seen_cards: [],
    turnsTaken: 0,
    gameOutcomeSent: false
};

// DOM elements (no changes needed here)
const elements = {
    gameBoard: document.getElementById('game-board'),
    playerScore: document.getElementById('player-score'),
    computerScore: document.getElementById('computer-score'),
    message: document.getElementById('message'),
    startBtn: document.getElementById('start-btn'),
    backBtn: document.getElementById('back-btn'),
    helpBtn: document.getElementById('help-btn'),
    // Add references to title elements if you want to update them
    startScreenTitle: document.querySelector('#start-screen .logo'),
    gameScreenTitle: document.querySelector('#game-screen .game-title')
};

// Screens (no changes needed here)
const screens = {
    start: document.getElementById('start-screen'),
    game: document.getElementById('game-screen')
};

// --- Standard WebSocket Connection ---
let websocket = null; // Global variable

function connectWebSocket() {
    websocket = new WebSocket('ws://localhost:8888/ws');

    websocket.onopen = function(event) {
        console.log("WebSocket connection opened to ws://localhost:8888/ws");
        // **** REMOVED fetch data.json ****
        // const response =  fetch('data.json');
        // const data =  response.json();
        // let myVar = data.message;
        // console.log("myVar inside async function:", 3);

        // Update UI - indicate waiting for theme
        if (elements.message) {
            updateMessage("Connected. Waiting for game theme...");
        }
        // Keep start button disabled until theme is received
        elements.startBtn.disabled = true;
    };

    websocket.onmessage = function(event) {
        console.log("Message received from server: " + event.data);

        // **** HANDLE THEME MESSAGE ****
        if (event.data.startsWith("theme ")) {
            const receivedPassion = event.data.split(" ")[1];
            if (imageSets[receivedPassion]) { // Check if the theme exists
                SELECTED_PASSION = receivedPassion;
                config.cardImages = imageSets[SELECTED_PASSION]; // Set the correct image set
                console.log("Theme set by server:", SELECTED_PASSION);
                updateGameTitle(); // Update titles with the passion
                // Enable the start button now that the theme is set
                elements.startBtn.disabled = false;
                if (elements.message) {
                    updateMessage(`Theme set to ${SELECTED_PASSION}! Select difficulty and press Start.`);
                }
            } else {
                console.error("Received unknown theme from server:", receivedPassion);
                // Handle error - maybe default to fruits?
                SELECTED_PASSION = 'fruits';
                config.cardImages = imageSets[SELECTED_PASSION];
                updateGameTitle();
                elements.startBtn.disabled = false;
                 if (elements.message) {
                     updateMessage(`Received unknown theme. Using default (fruits). Select difficulty and press Start.`);
                 }
            }
        } else {
             // Handle other messages if needed in the future
            // updateMessage("Server: " + event.data); // Example
        }
    };


    websocket.onerror = function(event) {
        console.error("WebSocket error observed:", event);
         if (elements.message) {
            updateMessage("Error connecting to game server.");
         }
         // Disable start button on error
         elements.startBtn.disabled = true;
    };

    websocket.onclose = function(event) {
        console.log("WebSocket connection closed. Code:", event.code, "Reason:", event.reason);
         if (elements.message) {
            updateMessage("Connection to game server lost. Please refresh.");
         }
        websocket = null;
        // Disable start button on close
        elements.startBtn.disabled = true;
        // Optional: Add reconnect logic here if desired
        // setTimeout(connectWebSocket, 5000);
    };
}

// --- End Standard WebSocket ---

// **** Function to update game titles ****
function updateGameTitle() {
    const passionTitle = SELECTED_PASSION ? SELECTED_PASSION.charAt(0).toUpperCase() + SELECTED_PASSION.slice(1) : 'Game';
    if (elements.startScreenTitle) {
        elements.startScreenTitle.textContent = `Memory (${passionTitle})`;
    }
    if (elements.gameScreenTitle) {
        elements.gameScreenTitle.textContent = `Memory (${passionTitle})`;
    }
}


// Initialize difficulty buttons (no changes needed here)
document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
        gameState.difficulty = button.dataset.difficulty;
        if (elements.message && SELECTED_PASSION) updateMessage(`Selected difficulty: ${button.textContent}. Ready to start!`);
        else if (elements.message) updateMessage(`Selected difficulty: ${button.textContent}. Waiting for theme...`);

    });
});

// Start game button
elements.startBtn.addEventListener('click', () => {
    // Check if WebSocket is connected AND theme is set
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        console.log("WebSocket not connected. Attempting to connect...");
        connectWebSocket(); // Try to connect if not already connected
        // Don't start game immediately, wait for theme message
        updateMessage("Connecting... Waiting for theme.");
    } else if (!SELECTED_PASSION) {
        // WebSocket is open, but theme hasn't arrived yet
        console.log("WebSocket open, but theme not yet received.");
        updateMessage("Still waiting for game theme from server...");
    }
    else {
        // WebSocket is open and theme is set, proceed with starting
        startGame();
    }
});


// Back to menu button (no changes needed)
elements.backBtn.addEventListener('click', () => {
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');
    // Re-disable start button when going back, require theme again potentially
    elements.startBtn.disabled = true;
    if (websocket && websocket.readyState === WebSocket.OPEN) {
        updateMessage("Connected. Waiting for game theme..."); // Reset message
    } else {
         updateMessage("Disconnected. Please refresh or wait for connection.");
    }
    // Reset difficulty selection visually and logically
    document.querySelectorAll('.difficulty-btn').forEach(btn => btn.classList.remove('active'));
    gameState.difficulty = null;
});

// Play Again / Difficulty Change / End Game buttons (Logic remains the same)
document.getElementById('play-again-btn').addEventListener('click', () => {
    // ... (no changes needed here) ...
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.add('active');
    document.querySelector('.difficulty-change-screen').classList.add('active');
    document.getElementById('difficulty-change-message').textContent = '';
});

document.getElementById('increase-difficulty-yes').addEventListener('click', () => {
    // ... (no changes needed here) ...
    const difficulties = ['very-easy', 'easy', 'medium', 'hard', 'very-hard'];
    const currentIndex = difficulties.indexOf(gameState.difficulty);
    const messageElement = document.getElementById('difficulty-change-message');
    if (currentIndex < difficulties.length - 1) {
        gameState.difficulty = difficulties[currentIndex + 1];
        messageElement.textContent = `Difficulty increased to: ${gameState.difficulty.replace('-', ' ')}`;
    } else {
        messageElement.textContent = 'Already at maximum difficulty!';
    }
    setTimeout(() => {
        document.querySelector('.difficulty-change-overlay').classList.remove('active');
        document.querySelector('.difficulty-change-screen').classList.remove('active');
        elements.helpBtn.style.display = 'block';
        startGame();
    }, 1500);
});

document.getElementById('increase-difficulty-no').addEventListener('click', () => {
    // ... (no changes needed here) ...
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    startGame();
});

document.getElementById('end-game-btn').addEventListener('click', () => {
    // ... (no changes needed here) ...
     document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');
    // Also reset difficulty selection and disable start button when ending
    document.querySelectorAll('.difficulty-btn').forEach(btn => btn.classList.remove('active'));
    gameState.difficulty = null;
    elements.startBtn.disabled = true; // Require theme again
    updateMessage("Game ended. Connect and select theme to play again.");
});


// Start the game
function startGame() {
    // **** Add checks for theme and difficulty ****
    if (!SELECTED_PASSION || !config.cardImages) {
        if (elements.message) updateMessage('Error: Game theme not set. Waiting for server...');
        elements.startBtn.disabled = true; // Keep disabled
        return;
    }
     if (!gameState.difficulty) {
        if (elements.message) updateMessage('Please select a difficulty first!');
        return;
    }

    console.log(`Starting game with theme: ${SELECTED_PASSION}, difficulty: ${gameState.difficulty}`);
    screens.start.classList.add('hidden');
    screens.game.classList.add('active');

    resetGame(); // Resets scores, board state etc.
    initializeBoard(); // Creates the card layout based on difficulty and THEME
    renderBoard(); // Displays the cards

    const playerStarts = Math.random() < 0.5;
    gameState.playerTurn = playerStarts;
    if (elements.message) updateMessage(playerStarts ? 'You start first!' : 'Pepper starts first!');
    elements.helpBtn.disabled = !playerStarts;
    elements.helpBtn.style.display = 'block'; // Ensure help button is visible

    if (!playerStarts) {
        setTimeout(computerTurn, 1500);
    }
}

// Reset game state (no changes needed here, uses global SELECTED_PASSION indirectly via config)
function resetGame() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    gameState = {
        // Keep selected difficulty and theme
        difficulty: gameState.difficulty,
        // currentTheme: SELECTED_PASSION, // You could store it here too if needed

        // Reset game-specific state
        board: Array(rows).fill().map(() => Array(cols).fill(0)),
        faceUp: Array(rows).fill().map(() => Array(cols).fill(false)),
        matchedPairs: Array(rows).fill().map(() => Array(cols).fill(false)),
        playerScore: 0,
        computerScore: 0,
        playerTurn: true,
        firstCard: null,
        waiting: false,
        seen_cards: Array(rows).fill().map(() => Array(cols).fill(0)),
        turnsTaken: 0,
        gameOutcomeSent: false // Reset flag
    };
    updateScores();
    if (elements.message) updateMessage("Game reset. Select a card.");
    elements.helpBtn.disabled = false; // Re-enable help potentially
}

// Initialize the game board (no changes needed, uses global config.cardImages which is now dynamic)
function initializeBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const totalCards = rows * cols;
    if (totalCards % 2 !== 0) {
        console.error("Error: Odd number of cards required for difficulty", gameState.difficulty);
        // Handle this error - maybe adjust cols/rows or show message
        return;
    }
    const numPairs = totalCards / 2;
    const availableImageKeys = Object.keys(config.cardImages);
    if (availableImageKeys.length < numPairs) {
         console.warn(`Warning: Not enough unique images for ${numPairs} pairs in theme '${SELECTED_PASSION}'. Images will repeat sooner.`);
    }

    let cards = [];
    for (let i = 1; i <= numPairs; i++) {
        // Cycle through available image keys if numPairs exceeds available unique images
        const imageKeyIndex = (i - 1) % availableImageKeys.length;
        const imageKey = availableImageKeys[imageKeyIndex];
        cards.push(imageKey, imageKey); // Use the key (e.g., '1', '2')
    }
    shuffleArray(cards);
    let index = 0;
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            gameState.board[row][col] = cards[index++]; // Store the key
        }
    }
    // console.log("Initialized board layout:", gameState.board); // Debug
}

// Render the game board (no changes needed, uses dynamic config.cardImages)
function renderBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    elements.gameBoard.innerHTML = '';
    elements.gameBoard.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    // Ensure config.cardImages is set before rendering
    if (!config.cardImages) {
        console.error("Cannot render board: config.cardImages not set.");
        updateMessage("Error: Waiting for game theme images.");
        return;
    }

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const card = document.createElement('div');
            card.className = 'card';
            if (gameState.faceUp[row][col]) card.classList.add('flipped');
            card.dataset.row = row; card.dataset.col = col;
            if (gameState.matchedPairs[row][col]) {
                card.innerHTML = `<div class="empty-card"><img src="${config.emptyCard}" alt="Matched"></div>`;
                card.style.pointerEvents = 'none'; card.style.opacity = '0.6'; card.classList.add('matched');
            } else {
                const cardValueKey = gameState.board[row][col]; // This is the key ('1', '2', etc.)
                const imagePath = config.cardImages[cardValueKey]; // Get path from dynamic config

                if (!imagePath) {
                     console.error(`Error: Image path not found for key ${cardValueKey} in theme ${SELECTED_PASSION}`);
                     // Provide fallback or error image
                     card.innerHTML = `
                        <div class="card-inner">
                            <div class="card-front"><img src="${config.emptyCard}" alt="Error"></div>
                            <div class="card-back"><img src="${config.cardBack}" alt="Card Back"></div>
                        </div>`;
                } else {
                    card.innerHTML = `
                        <div class="card-inner">
                            <div class="card-front"><img src="${imagePath}" alt="Card ${cardValueKey}" onerror="this.src='${config.emptyCard}'"></div>
                            <div class="card-back"><img src="${config.cardBack}" alt="Card Back" onerror="this.src='${config.emptyCard}'"></div>
                        </div>`;
                }

                if (gameState.playerTurn && !gameState.waiting && !gameState.faceUp[row][col]) {
                     card.addEventListener('click', () => handleCardClick(row, col));
                } else { card.style.cursor = 'default'; }
            }
            elements.gameBoard.appendChild(card);
        }
    }
}

// Handle card click (no changes needed)
function handleCardClick(row, col) {
    // ... (no changes needed here) ...
    if (gameState.waiting || !gameState.playerTurn || gameState.faceUp[row][col] || gameState.matchedPairs[row][col]) return;
    gameState.faceUp[row][col] = true;
    renderBoard();
    gameState.seen_cards[row][col] = gameState.board[row][col];
    if (gameState.firstCard === null) {
        gameState.firstCard = { row, col };
        elements.helpBtn.disabled = true;
        if (elements.message) updateMessage("First card selected. Pick another.");
    } else {
        gameState.waiting = true;
        if (elements.message) updateMessage("Checking for a match...");
        const secondCard = { row, col };
        setTimeout(() => checkMatch(gameState.firstCard, secondCard, 'player'), 1000);
    }
}

// Computer's turn logic (no changes needed)
function computerTurn() {
    // ... (no changes needed here) ...
    if (gameState.playerTurn || gameState.waiting) return;
    if (isGameOver()) { checkGameOver(); return; }
    elements.helpBtn.disabled = true;
    if (elements.message) updateMessage('Pepper is thinking...');
    setTimeout(() => {
        let firstCard_p = selectRandomCard();
        if (!firstCard_p) { /* Handle error or end turn */ return; }
        gameState.faceUp[firstCard_p.row][firstCard_p.col] = true;
        gameState.seen_cards[firstCard_p.row][firstCard_p.col] = gameState.board[firstCard_p.row][firstCard_p.col];
        renderBoard();
        if (elements.message) updateMessage('Pepper selected the first card...');
        const playerAccuracy = getPlayerAccuracy();
        let pepperAccuracy = Math.min(1, Math.max(0.3, playerAccuracy + 0.2));
        setTimeout(() => {
            let secondCard_p = Strategy(firstCard_p, pepperAccuracy);
             if (!secondCard_p) { /* Handle error or end turn */ return; }
            gameState.faceUp[secondCard_p.row][secondCard_p.col] = true;
            gameState.seen_cards[secondCard_p.row][secondCard_p.col] = gameState.board[secondCard_p.row][secondCard_p.col];
            renderBoard();
             if (elements.message) updateMessage('Pepper selected the second card. Checking match...');
            setTimeout(() => checkMatch(firstCard_p, secondCard_p, 'computer'), 1000);
        }, 1500);
    }, 1000);
}
function Strategy(card1, acc) { // No changes needed
    // ... (no changes needed here) ...
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const card_type = gameState.board[card1.row][card1.col];
    const prob = Math.random();
    if (prob <= acc) {
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                if (gameState.seen_cards[row][col] === card_type &&
                    !(row === card1.row && col === card1.col) &&
                    !gameState.matchedPairs[row][col] && !gameState.faceUp[row][col]) {
                    return {row, col};
                }
            }
        }
    }
    return selectRandomCard(card1);
}
function selectRandomCard(exclude = null) { // No changes needed
    // ... (no changes needed here) ...
    const { rows, cols } = config.difficulties[gameState.difficulty];
    let availableCards = [];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.matchedPairs[row][col] && !gameState.faceUp[row][col]) {
                if (!exclude || row !== exclude.row || col !== exclude.col) {
                    availableCards.push({ row, col });
                }
            }
        }
    }
    if (availableCards.length === 0) return null;
    return availableCards[Math.floor(Math.random() * availableCards.length)];
}

// Check if two cards match (no changes needed)
function checkMatch(card1, card2, player) { // No changes needed in core logic
    // ... (no changes needed here) ...
    const match = gameState.board[card1.row][card1.col] === gameState.board[card2.row][card2.col];
    if (player === 'player') gameState.turnsTaken++;
    if (match) {
        gameState.matchedPairs[card1.row][card1.col] = true;
        gameState.matchedPairs[card2.row][card2.col] = true;
        gameState.faceUp[card1.row][card1.col] = true;
        gameState.faceUp[card2.row][card2.col] = true;
        if (player === 'player') {
            gameState.playerScore++;
             if (elements.message) updateMessage('Well done! It\'s your turn again!');
            elements.helpBtn.disabled = false;
        } else {
            gameState.computerScore++;
            if (elements.message) updateMessage('Pepper found a match! Pepper\'s turn again.');
            setTimeout(computerTurn, 1500); // Computer gets another turn
        }
        updateScores();
        gameState.firstCard = null; gameState.waiting = false;
    } else { // No Match
         if (player === 'player') { if (elements.message) updateMessage('No match! Pepper\'s turn!'); }
         else { if (elements.message) updateMessage('No match for Pepper. Your turn!'); }
        setTimeout(() => {
            gameState.faceUp[card1.row][card1.col] = false;
            gameState.faceUp[card2.row][card2.col] = false;
            gameState.playerTurn = !gameState.playerTurn;
            gameState.firstCard = null; gameState.waiting = false;
            renderBoard();
            if (!gameState.playerTurn) { elements.helpBtn.disabled = true; setTimeout(computerTurn, 1500); }
            else { elements.helpBtn.disabled = false; }
        }, 1000);
    }
    renderBoard();
    setTimeout(checkGameOver, 100); // Check shortly after processing
}

// Helper function to check if game is over (no changes needed)
function isGameOver() { // No changes needed
    // ... (no changes needed here) ...
     const { rows, cols } = config.difficulties[gameState.difficulty];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.matchedPairs[row][col]) return false;
        }
    }
    return true;
}

// Update checkGameOver to use standard WebSocket send (no changes needed here)
function checkGameOver() {
    // ... (no changes needed here) ...
     if (isGameOver() && !gameState.gameOutcomeSent) {
        gameState.gameOutcomeSent = true; // Set flag

        let message, title;

        if (gameState.playerScore > gameState.computerScore) {
            title = 'Congratulations!'; message = 'You win!';
            // --- SEND 'win' MESSAGE VIA STANDARD WEBSOCKET ---
            if (websocket && websocket.readyState === WebSocket.OPEN) { // Check state
                console.log("Game Over - Player Wins! Sending 'win' message via WebSocket.");
                websocket.send('win'); // Send the simple "win" string command
            } else {
                console.error("Cannot send win message: WebSocket not open or not connected.");
            }
            // -----------------------------------------------
        } else if (gameState.playerScore < gameState.computerScore) {
            title = 'Game Over!'; message = 'Pepper wins!';
            console.log("Game Over - Player Lost.");
             // Optional: Send 'lose' command if needed
             // if (websocket && websocket.readyState === WebSocket.OPEN) { websocket.send('lose'); }
        } else {
            title = 'Game Over!'; message = 'It\'s a tie!';
            console.log("Game Over - It's a Tie.");
             // Optional: Send 'tie' command if needed
             // if (websocket && websocket.readyState === WebSocket.OPEN) { websocket.send('tie'); }
        }

        // Show end game message UI (existing code)
        document.getElementById('end-game-title').textContent = title;
        document.getElementById('end-game-message').textContent = message;
        document.getElementById('final-player-score').textContent = gameState.playerScore;
        document.getElementById('final-computer-score').textContent = gameState.computerScore;
        document.querySelector('.end-game-overlay').classList.add('active');
        document.querySelector('.end-game-message').classList.add('active');
        elements.helpBtn.style.display = 'none';
    }
}

// Update scores display (no changes needed)
function updateScores() { // No changes needed
    elements.playerScore.textContent = gameState.playerScore;
    elements.computerScore.textContent = gameState.computerScore;
}

// Update message display (no changes needed)
function updateMessage(text) { // No changes needed
    // ... (no changes needed here) ...
     if (elements.message) {
         elements.message.innerHTML = text; // Use innerHTML to allow styling tags like span
    } else {
        console.log("UI Message (no element):", text); // Log if message element isn't available
    }
}

// Helper function to shuffle an array (no changes needed)
function shuffleArray(array) { // No changes needed
    // ... (no changes needed here) ...
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// Flip all cards for help function (no changes needed)
function flipAllCards(faceUp) { // No changes needed
    // ... (no changes needed here) ...
    const { rows, cols } = config.difficulties[gameState.difficulty];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.matchedPairs[row][col]) {
                gameState.faceUp[row][col] = faceUp;
            }
        }
    }
    renderBoard();
}

// Handle help button click (no changes needed)
function handleHelp() { // No changes needed
    // ... (no changes needed here) ...
    if (gameState.waiting || !gameState.playerTurn || gameState.firstCard !== null) return;
    elements.helpBtn.disabled = true;
    flipAllCards(true);
    let secondsLeft = 5;
    updateMessage(`Memorize! Flipping back in <span class="countdown-number">${secondsLeft}</span>...`);
    const countdownInterval = setInterval(() => {
        secondsLeft--;
        if (secondsLeft > 0) {
            const countdownSpan = document.querySelector('.countdown-number');
            if (countdownSpan) countdownSpan.textContent = secondsLeft;
        } else {
            clearInterval(countdownInterval);
            flipAllCards(false);
            elements.helpBtn.disabled = false;
            updateMessage('Cards hidden! Your turn continues...');
        }
    }, 1000);
}

// Add event listener for help button (no changes needed)
elements.helpBtn.addEventListener('click', handleHelp);

// Calculate player accuracy (no changes needed)
function getPlayerAccuracy() { // No changes needed
    // ... (no changes needed here) ...
    if (gameState.turnsTaken === 0) return 0.5;
    const accuracy = gameState.playerScore / gameState.turnsTaken;
    return Math.max(0, Math.min(1, accuracy));
}

// Ensure the WebSocket connection is attempted when the script loads
document.addEventListener('DOMContentLoaded', (event) => {
    console.log("DOM fully loaded and parsed. Attempting WebSocket connection.");
    // **** Disable start button initially ****
    elements.startBtn.disabled = true;
    updateMessage("Connecting to server..."); // Initial message

    connectWebSocket(); // Attempt connection
    updateGameTitle(); // Set initial title (will update again when theme received)
});