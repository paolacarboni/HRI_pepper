let computerTurnTimeout = null;
let checkMatchTimeout = null;



const PASSION_COLORS = {
    fruits: 'orange',
    music: 'blue',
    gardening: 'green'
  };
  


// TODO: Strategy dell' accuracy del player

// Define image sets 
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
        4: 'images/music_images/glockenspiel.jpg', 5: 'images/music_images/cembalo.jpg',
        6: 'images/music_images/microphone.jpg', 7: 'images/music_images/cello.jpg', 8: 'images/music_images/electric_guitar.jpg',
        9: 'images/music_images/drum_kit.jpg', 10: 'images/music_images/triangle.jpg', 11: 'images/music_images/xylophone.jpg',
        12: 'images/music_images/kalimba.jpg', 13: 'images/music_images/bongos.jpg', 14: 'images/music_images/trumpet.jpg',
        15: 'images/music_images/ukulele.jpg', 16: 'images/music_images/armonica.jpg', 17: 'images/music_images/clarinet.jpg',
        18: 'images/music_images/flute.jpg', 19: 'images/music_images/mandolin.jpg', 20: 'images/music_images/tamburine.jpg',
        21: 'images/music_images/acoustic_guitar.jpg', 22: 'images/music_images/piano.jpg'
    },
    gardening: {
        1: 'images/gardening_images/peperoni.jpg', 2: 'images/gardening_images/melone.jpg', 3: 'images/gardening_images/ravanelli.jpg',
        4: 'images/gardening_images/broccolo.jpg', 5: 'images/gardening_images/zucca.jpg', 6: 'images/gardening_images/soia.jpg',
        7: 'images/gardening_images/patata.jpg', 8: 'images/gardening_images/pianta.jpg', 9: 'images/gardening_images/guanti.jpg',
        10: 'images/gardening_images/spandiconcime.jpg', 11: 'images/gardening_images/radish.jpg', 12: 'images/gardening_images/tubo.jpg',
        13: 'images/gardening_images/carrot.jpg', 14: 'images/gardening_images/salad.jpg', 15: 'images/gardening_images/germogli.jpg',
        16: 'images/gardening_images/seeds.jpg', 17: 'images/gardening_images/rastrello.jpg', 18: 'images/gardening_images/annaffiatoio.jpg',
        19: 'images/gardening_images/pala.jpg', 20: 'images/gardening_images/carriola.jpg'
    }
};

// **** ADDED: Define theme styles ****
const themeStyles = {
    fruits: { // Original theme (matches your CSS :root defaults)
        primary: 'rgb(230, 126, 34)',
        secondary: '#F1C40F',
        dark: '#8f5e1d',
        light: '#FDEBD0',
        success: '#2ECC71',
        warning: '#E74C3C'
    },
    music: {
        primary: '#3498DB',   // Blue
        secondary: '#5DADE2', // Lighter blue
        dark: '#1A5276',   // Darker blue
        light: '#D6EAF8',  // Very light blue
        success: '#2ECC71',
        warning: '#E74C3C'
    },
    gardening: {
        primary: '#27AE60',   // Green
        secondary: '#58D68D', // Lighter green
        dark: '#196F3D',   // Darker green
        light: '#D5F5E3',  // Very light green
        success: '#2ECC71',
        warning: '#E74C3C'
    },
    default: { // Fallback theme (same as fruits)
        primary: 'rgb(230, 126, 34)',
        secondary: '#F1C40F',
        dark: '#8f5e1d',
        light: '#FDEBD0',
        success: '#2ECC71',
        warning: '#E74C3C'
    }
};
// *********************************

// **** MODIFIED: Initialize SELECTED_PASSION to null ****
let SELECTED_PASSION = null;
let SELECTED_NAME = null;
//let websocket = null;
// Game configuration
const config = {
    difficulties: {
        'very-easy': { rows: 2, cols: 3 },
        'easy': { rows: 3, cols: 4 },
        'medium': { rows: 4, cols: 5 },
        'hard': { rows: 5, cols: 6 },
        'very-hard': { rows: 5, cols: 8 }
    },
    cardImages: null, // Set later based on SELECTED_PASSION
    cardBacks: { 
        fruits: 'images/fruit_images/back_fruits.jpg',
        music: 'images/music_images/back_music.jpeg',
        gardening: 'images/gardening_images/back_gardening.jpeg'
    },
    emptyCard: 'images/empty_card.jpg'
};

// Game state
let gameState = {
    difficulty: null,
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
    gameOutcomeSent: false,
    meaningfulTurns: 0,
    successfulMeaningfulTurns: 0
};

// DOM elements
const elements = {
    preIntroScreen: document.getElementById('pre-intro-screen'),
    pepperImage: document.getElementById('pepper-image'),
    introScreen: document.getElementById('intro-screen'),
    introYesBtn: document.getElementById('intro-yes-btn'),
    introNoBtn: document.getElementById('intro-no-btn'),
    gameBoard: document.getElementById('game-board'),
    playerScore: document.getElementById('player-score'),
    computerScore: document.getElementById('computer-score'),
    message: document.getElementById('message'),
    startBtn: document.getElementById('start-btn'),
    backBtn: document.getElementById('back-btn'),
    helpBtn: document.getElementById('help-btn'),
    startScreenTitle: document.querySelector('#start-screen .logo'),
    gameScreenTitle: document.querySelector('#game-screen .game-title')
};

// Screens
const screens = {
    preIntro: document.getElementById('pre-intro-screen'),
    intro: document.getElementById('intro-screen'),
    start: document.getElementById('start-screen'),
    game: document.getElementById('game-screen')
};


// --- Standard WebSocket Connection ---
let websocket = null;

function connectWebSocket() {
    // Determine WebSocket protocol: 'ws' for http, 'wss' for https
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Use the same host as the page was loaded from
    const wsHost = window.location.host; // This will be e.g., "your-id.ngrok-free.app" or "localhost:8888"

    const wsUrl = `${wsProtocol}//${wsHost}/ws`;
    console.log("Attempting WebSocket connection to: " + wsUrl); // Log the URL we're trying to connect to
    websocket = new WebSocket(wsUrl);

    websocket.onopen = function(event) {
        console.log("WebSocket connection opened to " + wsUrl); // Log the successful connection URL
        if (elements.message) {
            updateMessage("Connected. Waiting for game theme...");
        }
        elements.startBtn.disabled = true; // Keep disabled until theme received
    };

    // **** MODIFIED: WebSocket onmessage handler (This part remains as you had it) ****
    websocket.onmessage = function(event) {
        console.log("Message received from server: " + event.data);

        if (event.data.startsWith("name ")) {
            const receivedName = event.data.split(" ")[1];
            SELECTED_NAME = receivedName;
            console.log("Name set by server:", SELECTED_NAME);

            // Update all player name displays immediately
            document.querySelectorAll('.player-label').forEach(el => {
                el.textContent = SELECTED_NAME;
            });

            // Update the intro greeting immediately if we're on the intro screen
            updateIntroGreeting();

            // Also update the intro screen logo if it exists
            if (elements.introScreen) {
                const logoElement = elements.introScreen.querySelector('.logo');
                if (logoElement) {
                    logoElement.textContent = `Good to see you, ${SELECTED_NAME}!`;
                }
            }
        }
        else if (event.data.startsWith("theme ")) {
            const receivedPassion = event.data.split(" ")[1];
            // Check if theme exists in both imageSets AND themeStyles
            if (imageSets[receivedPassion] && themeStyles[receivedPassion]) {
                SELECTED_PASSION = receivedPassion;
                config.cardImages = imageSets[SELECTED_PASSION];
                console.log("Theme set by server:", SELECTED_PASSION);

                // **** APPLY THEME STYLES AND UPDATE TITLE ****
                applyThemeStyles(SELECTED_PASSION); // Apply the new styles
                updateGameTitle(); // Update titles

                elements.startBtn.disabled = false; // Enable start button
                if (elements.message) {
                    updateMessage(`Theme set to ${SELECTED_PASSION}! Select difficulty and press Start.`);
                }
            } else {
                console.error("Received unknown or incomplete theme from server:", receivedPassion);
                // Fallback to 'fruits' theme and styles
                SELECTED_PASSION = 'fruits';
                config.cardImages = imageSets[SELECTED_PASSION];

                // **** APPLY DEFAULT (FRUITS) STYLES AND UPDATE TITLE ****
                applyThemeStyles(SELECTED_PASSION); // Apply default styles
                updateGameTitle();
                // updateStartScreenColors(SELECTED_PASSION); // This line was in your original, ensure it's defined if you need it

                elements.startBtn.disabled = false; // Enable start button even on fallback
                 if (elements.message) {
                     updateMessage(`Received unknown theme. Using default (fruits). Select difficulty and press Start.`);
                 }
            }
        } else {
             // Handle other messages if needed
        }
    };
    // ********************************************

    websocket.onerror = function(event) {
        console.error("WebSocket error observed:", event);
         if (elements.message) {
            updateMessage("Error connecting to game server.");
         }
         elements.startBtn.disabled = true;
    };

    websocket.onclose = function(event) {
        console.log("WebSocket connection closed. Code:", event.code, "Reason:", event.reason);
         if (elements.message) {
            updateMessage("Connection to game server lost. Please refresh.");
         }
        websocket = null;
        elements.startBtn.disabled = true;
        // Optional: Revert to default styles on disconnect?
        // applyThemeStyles('default');
        // updateGameTitle(); // Reset title
    };
}
// --- End Standard WebSocket ---


function updateIntroGreeting() {
    // Update the greeting text
    const greetingElement = document.getElementById('intro-greeting');
    if (greetingElement) {
        greetingElement.textContent = SELECTED_NAME 
            ? `Good to see you, ${SELECTED_NAME}!` 
            :  `Good to see you!` ;
    }

    // Also update the logo in case it's different
    const logoElement = document.querySelector('#intro-screen .logo');
    if (greetingElement && SELECTED_NAME) {
        logoElement.textContent = `Good to see you, ${SELECTED_NAME}!`;
    }
}



function updateIntroScreen() {
    const greetingElement = document.getElementById('intro-greeting');
    if (SELECTED_NAME && greetingElement) {
        greetingElement.textContent = `Hi ${SELECTED_NAME}!`;
    }
}


function applyThemeStyles(theme) {
    const styles = themeStyles[theme] || themeStyles.default;
    const root = document.documentElement;

    // Update CSS variables
    Object.keys(styles).forEach(key => {
        const cssVarName = `--${key}`;
        const cssVarValue = styles[key];
        root.style.setProperty(cssVarName, cssVarValue);
    });

    // Update theme classes on relevant elements
    const themeClass = theme || 'default';
    
    // Update game title and logo
    document.querySelectorAll('.game-title, .logo, .subtitle').forEach(el => {
        el.classList.remove('fruits', 'music', 'gardening', 'default');
        el.classList.add(themeClass);
    });

    // Update buttons
    document.querySelectorAll('.difficulty-btn, .start-btn').forEach(el => {
        el.classList.remove('fruits', 'music', 'gardening', 'default');
        el.classList.add(themeClass);
    });

    // Force update titles
    updateGameTitle();
}


// Function to update game titles based on SELECTED_PASSION
function updateGameTitle() {
    const passionTitle = SELECTED_PASSION ? 
        SELECTED_PASSION.charAt(0).toUpperCase() + SELECTED_PASSION.slice(1) : 'Memory';
    
    if (elements.startScreenTitle) {
        elements.startScreenTitle.textContent = `${passionTitle} Memory`;
        // Remove any inline styles that might override our CSS
        elements.startScreenTitle.style.color = '';
        elements.startScreenTitle.style.background = '';
        elements.startScreenTitle.style.webkitBackgroundClip = '';
        elements.startScreenTitle.style.backgroundClip = '';
    }
    
    if (elements.gameScreenTitle) {
        elements.gameScreenTitle.textContent = `${passionTitle} Memory`;
        elements.gameScreenTitle.style.color = '';
    }
}

function updateStartScreenColors() {
    const color = PASSION_COLORS[SELECTED_PASSION] || 'black';
  
    document.querySelector('.logo').style.color = color;
    document.querySelector('.subtitle').style.color = color;
  
    document.querySelectorAll('.difficulty-button').forEach(btn => {
      btn.style.backgroundColor = color;
    });
  
    document.querySelector('.start-button').style.backgroundColor = color;
  }
  




  function applyThemeStyles(theme) {
    const styles = themeStyles[theme] || themeStyles.fruits;
    const root = document.documentElement;

    // Update CSS variables
    Object.keys(styles).forEach(key => {
        root.style.setProperty(`--${key}`, styles[key]);
    });

    // Apply theme class to body
    document.body.classList.remove('fruits', 'music', 'gardening');
    document.body.classList.add(theme);

    // Update game titles
    updateGameTitle();
}



// Initialize difficulty buttons
document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.difficulty-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        gameState.difficulty = button.dataset.difficulty;
        // Update message based on whether theme is set yet
        if (elements.message) {
            if (SELECTED_PASSION) {
                updateMessage(`Selected difficulty: ${button.textContent}. Ready to start!`);
            } else {
                updateMessage(`Selected difficulty: ${button.textContent}. Waiting for theme...`);
            }
        }
    });
});






// Transition from pre-intro to intro
elements.pepperImage.addEventListener('click', () => {
    // Update greeting with current name (if received)
    updateIntroGreeting();
    
    // Hide pre-intro
    screens.preIntro.classList.remove('active');
    screens.preIntro.classList.add('hidden');
    
    // Show intro
    screens.intro.classList.remove('hidden');
    screens.intro.classList.add('active');
});
// Transition from intro to other screens
elements.introYesBtn.addEventListener('click', () => {
    screens.intro.classList.add('hidden');
    screens.intro.classList.remove('active');
    
    setTimeout(() => {
        screens.start.classList.remove('hidden');
        screens.start.classList.add('active');
    }, 300);
});


elements.introNoBtn.addEventListener('click', () => {
    screens.intro.classList.add('hidden');
    screens.intro.classList.remove('active');
    
    setTimeout(() => {
        screens.preIntro.classList.remove('hidden');
        screens.preIntro.classList.add('active');
    }, 300);
});





// Start game button event listener
elements.startBtn.addEventListener('click', () => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        console.log("WebSocket not connected. Attempting to connect...");
        connectWebSocket();
        updateMessage("Connecting... Waiting for theme.");
    } else if (!SELECTED_PASSION) {
        console.log("WebSocket open, but theme not yet received.");
        updateMessage("Still waiting for game theme from server...");
    } else if (!gameState.difficulty) {
        updateMessage('Please select a difficulty first!');
    }
    else {
        startGame(); // Proceed only if connected, theme received, and difficulty selected
    }
});

// Back to menu button event listener

elements.backBtn.addEventListener('click', () => {
    // Clear any pending timeouts
    if (computerTurnTimeout) clearTimeout(computerTurnTimeout);
    if (checkMatchTimeout) clearTimeout(checkMatchTimeout);
    
    // Reset game state
    gameState = {
        difficulty: null,
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


    screens.game.classList.add('hidden');
    screens.game.classList.remove('active');
    

    screens.start.classList.remove('hidden');
    screens.start.classList.add('active');


    
    // Transition screens
    //
    // screens.game.classList.remove('active');
    // screens.start.classList.add('active');
    //elements.startBtn.disabled = true;

    //
    // Update message based on connection state
    if (websocket && websocket.readyState === WebSocket.OPEN && SELECTED_PASSION) {
        updateMessage(`Theme: ${SELECTED_PASSION}. Select difficulty and press Start.`);
    } else if (websocket && websocket.readyState === WebSocket.OPEN) {
        updateMessage("Connected. Waiting for game theme...");
    } else {
        updateMessage("Disconnected. Please refresh or wait for connection.");
    }
    
    document.querySelectorAll('.difficulty-btn').forEach(btn => btn.classList.remove('active'));
});

// Play Again / Difficulty Change / End Game button listeners (no changes needed in core logic)
document.getElementById('play-again-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.add('active');
    document.querySelector('.difficulty-change-screen').classList.add('active');
    document.getElementById('difficulty-change-message').textContent = '';
});

document.getElementById('increase-difficulty-yes').addEventListener('click', () => {
    const difficulties = ['very-easy', 'easy', 'medium', 'hard', 'very-hard'];
    const currentIndex = difficulties.indexOf(gameState.difficulty);
    const messageElement = document.getElementById('difficulty-change-message');
    if (currentIndex < difficulties.length - 1) {
        gameState.difficulty = difficulties[currentIndex + 1];
        const difficultyText = gameState.difficulty.replace('-', ' ');
        messageElement.innerHTML = `Difficulty increased to: <span class="difficulty-level">${difficultyText}</span>`;
    } else {
        messageElement.textContent = 'Already at maximum difficulty!';
    }
    setTimeout(() => {
        document.querySelector('.difficulty-change-overlay').classList.remove('active');
        document.querySelector('.difficulty-change-screen').classList.remove('active');
        elements.helpBtn.style.display = 'block';
        startGame(); // Restart with new difficulty
    }, 1500);
});

document.getElementById('increase-difficulty-no').addEventListener('click', () => {
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    startGame(); // Restart with same difficulty
});

document.getElementById('end-game-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');

    // Reset state for returning to start screen
    document.querySelectorAll('.difficulty-btn').forEach(btn => btn.classList.remove('active'));
    gameState.difficulty = null;
    elements.startBtn.disabled = true; // Require theme/difficulty again
    // Keep theme styles or reset? Let's keep them for now.
    // applyThemeStyles('default');
    // updateGameTitle();

    if (websocket && websocket.readyState === WebSocket.OPEN && SELECTED_PASSION) {
        updateMessage(`Theme: ${SELECTED_PASSION}. Select difficulty to play again.`);
    } else if (websocket && websocket.readyState === WebSocket.OPEN) {
        updateMessage("Connected. Waiting for game theme...");
    } else {
        updateMessage("Disconnected. Please refresh or wait for connection.");
    }
});

// Start the game function
function startGame() {
    // Double-check conditions before starting
    if (!SELECTED_PASSION || !config.cardImages) {
        if (elements.message) updateMessage('Error: Game theme not set. Waiting for server...');
        elements.startBtn.disabled = true;
        return;
    }
     if (!gameState.difficulty) {
        if (elements.message) updateMessage('Error: Please select a difficulty first!');
        return;
    }

    console.log(`Starting game with theme: ${SELECTED_PASSION}, difficulty: ${gameState.difficulty}`);

    // **** ADDED: Ensure correct theme styles are applied when game screen shows ****
    applyThemeStyles(SELECTED_PASSION);
    // **************************************************************************

    screens.start.classList.add('hidden');
    screens.game.classList.add('active');

    resetGame(); // Resets scores, board state etc.
    initializeBoard(); // Creates card layout based on difficulty and THEME
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

// Reset game state
function resetGame() {
    if (!gameState.difficulty) {
        console.error("Cannot reset game without a difficulty selected.");
        // Maybe go back to start screen or show error?
        return;
    }
    const { rows, cols } = config.difficulties[gameState.difficulty];
    gameState = {
        // Keep selected difficulty
        difficulty: gameState.difficulty,
        // Reset game-specific state
        board: Array(rows).fill().map(() => Array(cols).fill(0)),
        faceUp: Array(rows).fill().map(() => Array(cols).fill(false)),
        matchedPairs: Array(rows).fill().map(() => Array(cols).fill(false)),
        playerScore: 0,
        computerScore: 0,
        playerTurn: true, // Will be potentially overridden in startGame
        firstCard: null,
        waiting: false,
        seen_cards: Array(rows).fill().map(() => Array(cols).fill(0)),
        turnsTaken: 0,
        gameOutcomeSent: false
    };
    updateScores();
    // Message updated in startGame after reset
    elements.helpBtn.disabled = false;
}

// Initialize the game board
function initializeBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const totalCards = rows * cols;
    if (totalCards % 2 !== 0) {
        console.error("Error: Odd number of cards for difficulty", gameState.difficulty);
        // Handle error - maybe fallback or alert
        updateMessage(`Error: Invalid card count for ${gameState.difficulty}.`);
        return;
    }
    const numPairs = totalCards / 2;

    // Ensure cardImages for the selected theme are loaded
    if (!config.cardImages) {
         console.error(`Error: Card images for theme ${SELECTED_PASSION} not loaded.`);
         updateMessage(`Error loading images for ${SELECTED_PASSION}.`);
         // Potentially stop game initialization here
         return;
    }

    const availableImageKeys = Object.keys(config.cardImages);
    if (availableImageKeys.length < numPairs) {
         console.warn(`Warning: Not enough unique images for ${numPairs} pairs in theme '${SELECTED_PASSION}'. Images will repeat.`);
    }

    let cards = [];
    for (let i = 1; i <= numPairs; i++) {
        // Cycle through available image keys if needed
        const imageKeyIndex = (i - 1) % availableImageKeys.length;
        const imageKey = availableImageKeys[imageKeyIndex];
        if (!config.cardImages[imageKey]) {
            console.error(`Error: Missing image path for key ${imageKey} in theme ${SELECTED_PASSION}`);
            // Handle missing image - maybe use a default placeholder key?
            continue; // Skip this pair for now
        }
        cards.push(imageKey, imageKey);
    }

    // Check if enough cards were generated (in case of errors above)
    if(cards.length !== totalCards) {
        console.error(`Error: Card generation failed. Expected ${totalCards}, got ${cards.length}`);
        updateMessage(`Error preparing game board.`);
        return;
    }

    shuffleArray(cards);
    let index = 0;
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            gameState.board[row][col] = cards[index++]; // Store the key
        }
    }
}

// Render the game board
function renderBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    elements.gameBoard.innerHTML = '';
    // Calculate optimal column width based on container width, consider adding max-width for cards
    elements.gameBoard.style.gridTemplateColumns = `repeat(${cols}, minmax(80px, 120px))`; // Example responsive columns

    if (!config.cardImages) {
        console.error("Cannot render board: config.cardImages not set.");
        updateMessage("Error: Waiting for game theme images.");
        return;
    }

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const card = document.createElement('div');
            card.className = 'card';
            card.dataset.row = row;
            card.dataset.col = col;

            if (gameState.matchedPairs[row][col]) {
                card.innerHTML = `<div class="empty-card"><img src="${config.emptyCard}" alt="Matched"></div>`;
                card.style.pointerEvents = 'none';
                card.style.opacity = '0.6';
                card.classList.add('matched');
            } else {
                const cardValueKey = gameState.board[row][col];
                const imagePath = config.cardImages[cardValueKey]; // Get path from dynamic config

                if (!imagePath) {
                     console.error(`Error: Image path not found for key ${cardValueKey} in theme ${SELECTED_PASSION}`);
                     // Fallback display
                     card.innerHTML = `
                        <div class="card-inner ${gameState.faceUp[row][col] ? 'flipped-manual' : ''}">
                            <div class="card-front" style="background:#ccc; display:flex; align-items:center; justify-content:center;">Error</div>
                            <div <div class="card-back"><img src="${config.cardBacks[SELECTED_PASSION] || config.cardBacks.fruits}" alt="Card Back" onerror="this.src='${config.emptyCard}'"></div>
                        </div>`;
                     // Add 'flipped-manual' class if needed for CSS targeting w/o JS interaction
                     if (gameState.faceUp[row][col]) card.querySelector('.card-inner').classList.add('flipped-manual');

                } else {
                    card.innerHTML = `
                        <div class="card-inner">
                            <div class="card-front"><img src="${imagePath}" alt="Card ${cardValueKey}" onerror="this.src='${config.emptyCard}'"></div>
                            <div class="card-back"><img src="${config.cardBacks[SELECTED_PASSION] || config.cardBacks.fruits}" alt="Card Back" onerror="this.src='${config.emptyCard}'"></div>
                        </div>`;
                }

                 if (gameState.faceUp[row][col]) {
                     card.classList.add('flipped'); // Use the class for the flip animation
                 }

                // Add click listener only if it's player's turn, not waiting, card not face up/matched
                if (gameState.playerTurn && !gameState.waiting && !gameState.faceUp[row][col]) {
                     card.addEventListener('click', () => handleCardClick(row, col));
                     card.style.cursor = 'pointer'; // Ensure cursor indicates clickable
                } else {
                     card.style.cursor = 'default';
                }
            }
            elements.gameBoard.appendChild(card);
        }
    }
     // Re-apply grid template columns just in case it gets reset by browser weirdness
    elements.gameBoard.style.gridTemplateColumns = `repeat(${cols}, minmax(80px, 120px))`;
}

// Handle card click
function handleCardClick(row, col) {
    if (gameState.waiting || !gameState.playerTurn || gameState.faceUp[row][col] || gameState.matchedPairs[row][col]) {
        return; // Ignore clicks in these states
    }

    gameState.faceUp[row][col] = true;
    gameState.seen_cards[row][col] = gameState.board[row][col]; // Record seen card for computer AI

    // Visually flip the card immediately
    const cardElement = elements.gameBoard.querySelector(`.card[data-row="${row}"][data-col="${col}"]`);
    if (cardElement) cardElement.classList.add('flipped');

    if (gameState.firstCard === null) {
        // This is the first card flipped in a pair
        gameState.firstCard = { row, col };
        elements.helpBtn.disabled = true; // Disable help while selecting pair
        if (elements.message) updateMessage("First card selected. Pick another.");
        // No need to call renderBoard() here unless absolutely necessary,
        // as adding the 'flipped' class handles the visual change.
    } else {
        // This is the second card flipped
        gameState.waiting = true; // Prevent further clicks while checking
        if (elements.message) updateMessage("Checking for a match...");
        const secondCard = { row, col };

        // Disable clicks on all cards temporarily by updating cursor/styles or overlay
        // (renderBoard call below will partially handle this by changing cursors)
        renderBoard(); // Update board to reflect second card flip and disable clicks

        setTimeout(() => checkMatch(gameState.firstCard, secondCard, 'player'), 800); // Check after a short delay
    }
}


// Computer's turn logic
function computerTurn() {
    // Add check at start of function
    if (!gameState.difficulty || gameState.gameOutcomeSent) {
        console.log("Computer turn cancelled - no active game");
        return;
    }
    
    if (gameState.playerTurn || gameState.waiting) return;
    if (isGameOver()) { checkGameOver(); return; }

    elements.helpBtn.disabled = true;
    updateMessage('Pepper is thinking...');

    computerTurnTimeout = setTimeout(() => {
        let firstCard_p = selectRandomCard();
        if (!firstCard_p) {
            console.warn("Computer turn: No cards available to select (first).");
            gameState.playerTurn = true;
            renderBoard();
            updateMessage("Something went wrong. Your turn!");
            elements.helpBtn.disabled = false;
            return;
        }

        gameState.faceUp[firstCard_p.row][firstCard_p.col] = true;
        gameState.seen_cards[firstCard_p.row][firstCard_p.col] = gameState.board[firstCard_p.row][firstCard_p.col];
        renderBoard();
        updateMessage('Pepper selected the first card...');

        const playerAccuracy = getPlayerAccuracy();
        let pepperAccuracy = Math.min(0.95, Math.max(0.3, playerAccuracy + 0.15));

        computerTurnTimeout = setTimeout(() => {
            let secondCard_p = Strategy(firstCard_p, pepperAccuracy);
            if (!secondCard_p) {
                console.warn("Computer turn: No cards available to select (second).");
                gameState.faceUp[firstCard_p.row][firstCard_p.col] = false;
                gameState.playerTurn = true;
                renderBoard();
                updateMessage("Pepper got confused. Your turn!");
                elements.helpBtn.disabled = false;
                return;
            }

            gameState.faceUp[secondCard_p.row][secondCard_p.col] = true;
            gameState.seen_cards[secondCard_p.row][secondCard_p.col] = gameState.board[secondCard_p.row][secondCard_p.col];
            renderBoard();
            updateMessage('Pepper selected the second card. Checking match...');

            checkMatchTimeout = setTimeout(() => checkMatch(firstCard_p, secondCard_p, 'computer'), 1000);
        }, 1200);
    }, 800);
}


// Computer's strategy function
function Strategy(card1, acc) {

    if (!gameState.difficulty) {
        console.log("Strategy called with no difficulty set");
        return null;
    }
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const card_type = gameState.board[card1.row][card1.col];
    const prob = Math.random();

    // Try perfect memory based on accuracy
    if (prob <= acc) {
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                // Check if this card has been seen, matches the first card's type,
                // isn't the first card itself, isn't already matched, and isn't currently face up (shouldn't happen here)
                if (gameState.seen_cards[row][col] === card_type &&
                    !(row === card1.row && col === card1.col) &&
                    !gameState.matchedPairs[row][col] &&
                    !gameState.faceUp[row][col] ) { // Add check for faceUp just in case
                    console.log("Computer Strategy: Found known match.");
                    return {row, col}; // Found a known match
                }
            }
        }
         console.log("Computer Strategy: Tried perfect memory, but no known match found.");
    } else {
         console.log("Computer Strategy: Random chance applied (missed accuracy check).");
    }

    // If no known match found or accuracy check failed, select a random available card
    console.log("Computer Strategy: Selecting random second card.");
    return selectRandomCard(card1); // Pass card1 to exclude it
}

// Select a random available card
function selectRandomCard(exclude = null) {

    if (!gameState.difficulty) {
        console.log("selectRandomCard called with no difficulty set");
        return null;
    }
    const { rows, cols } = config.difficulties[gameState.difficulty];
    let availableCards = [];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            // Card must not be matched and not currently face up
            if (!gameState.matchedPairs[row][col] && !gameState.faceUp[row][col]) {
                // If an exclude card is provided, don't include it
                if (!exclude || !(row === exclude.row && col === exclude.col)) {
                    availableCards.push({ row, col });
                }
            }
        }
    }

    if (availableCards.length === 0) {
        console.log("SelectRandomCard: No available cards found.");
        return null; // No cards left to choose
    }
    const randomIndex = Math.floor(Math.random() * availableCards.length);
    return availableCards[randomIndex];
}

// Check if two cards match
function checkMatch(card1, card2, player) {
    const match = gameState.board[card1.row][card1.col] === gameState.board[card2.row][card2.col];

    if (player === 'player') {
        gameState.turnsTaken++; // Only increment player turns for accuracy calculation
    }

    if (match) {
        // --- MATCH FOUND ---
        gameState.matchedPairs[card1.row][card1.col] = true;
        gameState.matchedPairs[card2.row][card2.col] = true;
        // Keep cards faceUp visually (handled by 'matched' class in renderBoard)
        gameState.faceUp[card1.row][card1.col] = true; // Keep state consistent
        gameState.faceUp[card2.row][card2.col] = true;

        if (player === 'player') {
            gameState.playerScore++;
            gameState.turnsTaken++;
            // Check if at least one card was seen before
            const card1Seen = gameState.seen_cards[card1.row][card1.col] !== 0;
            const card2Seen = gameState.seen_cards[card2.row][card2.col] !== 0;
            // Update the successfulMeaningfulTurns only if at least one of the two matched cards was seen before
            if (card1Seen || card2Seen) {
                gameState.meaningfulTurns++;
                if (match) {
                    gameState.successfulMeaningfulTurns++;
                }
            }
            if (elements.message) updateMessage('Well done! It\'s your turn again!');
            elements.helpBtn.disabled = false; // Re-enable help
            gameState.waiting = false; // Player can go again immediately
        } else { // Computer found a match
            gameState.computerScore++;
            if (elements.message) updateMessage('Pepper found a match! Pepper\'s turn again.');
            // Computer gets another turn, no need to change gameState.playerTurn
             gameState.waiting = false; // Reset waiting state before computer's next move
            setTimeout(computerTurn, 1500); // Delay before computer's next turn
        }
        updateScores();
        gameState.firstCard = null; // Reset first card selection
        // Render board to show matched state (greyed out/styled)
        renderBoard();

    } else {
        // --- NO MATCH ---
        if (player === 'player') {
            if (elements.message) updateMessage('No match! Pepper\'s turn!');
        } else { // Computer failed match
            if (elements.message) updateMessage('No match for Pepper. Your turn!');
        }

        // Flip cards back down after a delay
        setTimeout(() => {
            gameState.faceUp[card1.row][card1.col] = false;
            gameState.faceUp[card2.row][card2.col] = false;
            gameState.playerTurn = !gameState.playerTurn; // Switch turns
            gameState.firstCard = null; // Reset first card selection
            gameState.waiting = false; // Allow interaction again
            renderBoard(); // Re-render to show cards face down and update cursors

            // If it's now the computer's turn, trigger it
            if (!gameState.playerTurn) {
                elements.helpBtn.disabled = true;
                setTimeout(computerTurn, 1500);
            } else { // It's now the player's turn
                elements.helpBtn.disabled = false; // Enable help
            }
        }, 1000); // Delay before flipping back
    }

    // Check for game over after processing the match/no-match
    // Use a slight delay to ensure state updates are processed
    setTimeout(checkGameOver, match ? 100 : 1100); // Check sooner on match, later on no-match (after flip back)
}


// Helper function to check if game is over
function isGameOver() {
     const { rows, cols } = config.difficulties[gameState.difficulty];
     let totalPairs = (rows * cols) / 2;
     let matchedCount = gameState.playerScore + gameState.computerScore;
     if (!gameState.difficulty) return false;
     return matchedCount === totalPairs; // Game is over when all pairs are matched
}

// Check game over and send result via WebSocket
function checkGameOver() {
     if (isGameOver() && !gameState.gameOutcomeSent) {
        gameState.gameOutcomeSent = true; // Prevent sending multiple messages

        let message, title;
        let outcome = 'tie'; // Default outcome

        if (gameState.playerScore > gameState.computerScore) {
            title = 'Congratulations!'; message = 'You win!';
            outcome = 'win';
        } else if (gameState.playerScore < gameState.computerScore) {
            title = 'Game Over!'; message = 'Pepper wins!';
            outcome = 'lose';
        } else {
            title = 'Game Over!'; message = 'It\'s a tie!';
            outcome = 'tie';
        }

        // Update final score labels with player name
        const finalScoreLabels = document.querySelectorAll('.final-score > div:first-child');
        if (finalScoreLabels[0] && SELECTED_NAME) {
            finalScoreLabels[0].textContent = SELECTED_NAME;
        }

        console.log(`Game Over - Player ${outcome}. Player: ${gameState.playerScore}, Computer: ${gameState.computerScore}`);

        // --- SEND OUTCOME VIA STANDARD WEBSOCKET ---
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            console.log(`Sending outcome '${outcome}' via WebSocket.`);
            websocket.send(outcome); // Send simple string: "win", "lose", or "tie"
        } else {
            console.error(`Cannot send game outcome '${outcome}': WebSocket not open or not connected.`);
        }
        // ---------------------------------------------

        // Show end game message UI
        document.getElementById('end-game-title').textContent = title;
        document.getElementById('end-game-message').textContent = message;
        document.getElementById('final-player-score').textContent = gameState.playerScore;
        document.getElementById('final-computer-score').textContent = gameState.computerScore;

        // Use a small delay to ensure UI updates (like final card match) render first
        setTimeout(() => {
            document.querySelector('.end-game-overlay').classList.add('active');
            document.querySelector('.end-game-message').classList.add('active');
            elements.helpBtn.style.display = 'none'; // Hide help button on game end
        }, 200);
    }
}

// Update scores display
function updateScores() {
    elements.playerScore.textContent = gameState.playerScore;
    elements.computerScore.textContent = gameState.computerScore;

        // Update score labels with player name
    const scoreLabels = document.querySelectorAll('.score-label');
    if (scoreLabels[0] && SELECTED_NAME) {
        scoreLabels[0].textContent = SELECTED_NAME;
    }
}

// Update message display
function updateMessage(text) {
     if (elements.message) {
         elements.message.innerHTML = text; // Use innerHTML for potential styling (like countdown)
    } else {
        console.log("UI Message (element not found):", text);
    }
}

// Helper function to shuffle an array (Fisher-Yates)
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

// Flip all non-matched cards (for help function)
function flipAllCards(faceUp) {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.matchedPairs[row][col]) { // Only flip non-matched cards
                gameState.faceUp[row][col] = faceUp;
            }
        }
    }
    renderBoard(); // Re-render to show the flips
}

// Handle help button click
function handleHelp() {
    if (gameState.waiting || !gameState.playerTurn || gameState.firstCard !== null) return;

    // Briefly flash the primary color
    const helpBtn = elements.helpBtn;
    helpBtn.style.backgroundColor = `var(--primary)`;
    setTimeout(() => {
        helpBtn.style.backgroundColor = `var(--secondary)`;
    }, 200);

    elements.helpBtn.disabled = true;
    flipAllCards(true);

    let secondsLeft = 5;
    updateMessage(`Memorize! Flipping back in <span class="countdown-number">${secondsLeft}</span>...`);

    const countdownInterval = setInterval(() => {
        secondsLeft--;
        const countdownSpan = elements.message.querySelector('.countdown-number');
        if (secondsLeft > 0) {
            if (countdownSpan) countdownSpan.textContent = secondsLeft;
        } else {
            clearInterval(countdownInterval);
            flipAllCards(false);
            elements.helpBtn.disabled = false;
            updateMessage('Cards hidden! Your turn continues...');
        }
    }, 1000);
}
// Add event listener for help button
elements.helpBtn.addEventListener('click', handleHelp);

// Calculate player accuracy
function getPlayerAccuracy() {
    
    if (gameState.turnsTaken === 0) return 0.5; // Default starting accuracy for AI adjustment
    // Accuracy = successful pairs found / number of pairs attempted 
   // const accuracy = gameState.playerScore / gameState.turnsTaken;
   // return Math.max(0.1, Math.min(0.9, accuracy)); // Clamp between 0.1 and 0.9
    
    // Count only turns where at least one card was seen before
    // Update these counters in the checkMatch function when player makes a match
    const accuracy = gameState.successfulMeaningfulTurns / Math.max(1, gameState.meaningfulTurns);
    console.log('--- Accuracy Calculation ---');
    console.log(`Total turns: ${gameState.turnsTaken}`);
    console.log(`Meaningful turns: ${gameState.meaningfulTurns}`);
    console.log(`Successful meaningful matches: ${gameState.successfulMeaningfulTurns}`);
    
    
    return Math.max(0.1, Math.min(0.9, accuracy)); // Clamp between 0.1 and 0.9


}

// Initialize connection when DOM is ready
document.addEventListener('DOMContentLoaded', (event) => {
    console.log("DOM fully loaded and parsed. Initializing...");
    elements.startBtn.disabled = true; // Start button disabled initially


    // Hide all screens except pre-intro
    screens.intro.classList.add('hidden');
    screens.start.classList.add('hidden');
    screens.game.classList.add('hidden');
    screens.preIntro.classList.add('active');


  
    updateMessage("Connecting to server...");
    applyThemeStyles('default'); // Apply default styles initially
    updateGameTitle(); // Set initial title (will update when theme received)
    connectWebSocket(); // Attempt WebSocket connection
});
