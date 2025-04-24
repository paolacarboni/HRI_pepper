// Game configuration
const config = {

    // Determines board size per difficulty
    difficulties: {
        'very-easy': { rows: 2, cols: 3 },
        'easy': { rows: 3, cols: 4 },
        'medium': { rows: 4, cols: 5 },
        'hard': { rows: 5, cols: 6 },
        'very-hard': { rows: 5, cols: 8 }
    },

    // Maps numbers to fruit images
    cardImages: {
        1: 'images/apple.jpg',
        2: 'images/banana.jpg',
        3: 'images/orange.jpg',
        4: 'images/pear.jpg',
        5: 'images/kiwi.jpg',
        6: 'images/peach.jpg',
        7: 'images/cherry.jpg',
        8: 'images/strawberry.jpg',
        9: 'images/blueberry.jpg',
        10: 'images/watermelon.jpg',
        11: 'images/raspberry.jpg',
        12: 'images/apricot.jpg',
        13: 'images/coconut.jpg',
        14: 'images/lemon.jpg',
        15: 'images/grapes.jpg',
        16: 'images/mango.jpg',
        17: 'images/papaya.jpg',
        18: 'images/plum.jpg',
        19: 'images/pomegranate.jpg',
        20: 'images/pineapple.jpg'
    },
    cardBack: 'images/card_back.jpg',
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
    turnsTaken: 0
};


// DOM elements: access HTML elements
const elements = {
    gameBoard: document.getElementById('game-board'),
    playerScore: document.getElementById('player-score'),
    computerScore: document.getElementById('computer-score'),
    message: document.getElementById('message'),
    startBtn: document.getElementById('start-btn'),
    backBtn: document.getElementById('back-btn'),
    helpBtn: document.getElementById('help-btn')
};


// Screens: to switch between the start menu and the game screen
const screens = {
    start: document.getElementById('start-screen'),
    game: document.getElementById('game-screen')
};

// Initialize difficulty buttons
document.querySelectorAll('.difficulty-btn').forEach(button => {
    button.addEventListener('click', () => {
        // Remove active class from all buttons
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to clicked button
        button.classList.add('active');
        gameState.difficulty = button.dataset.difficulty;
        updateMessage(`Selected difficulty: ${button.textContent}`);
    });
});

// Start game button
elements.startBtn.addEventListener('click', startGame);

// Back to menu button
elements.backBtn.addEventListener('click', () => {
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');
});




// Add these event listeners at the end of your initialization code:

// Play Again button - shows difficulty change question
document.getElementById('play-again-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.add('active');
    document.querySelector('.difficulty-change-screen').classList.add('active');
    document.getElementById('difficulty-change-message').textContent = ''; // Clear previous message
});


// Yes button - increases difficulty and starts game
document.getElementById('increase-difficulty-yes').addEventListener('click', () => {
    const difficulties = ['very-easy', 'easy', 'medium', 'hard', 'very-hard'];
    const currentIndex = difficulties.indexOf(gameState.difficulty);
    const messageElement = document.getElementById('difficulty-change-message');
    
    if (currentIndex < difficulties.length - 1) {
        gameState.difficulty = difficulties[currentIndex + 1];
        messageElement.textContent = `Difficulty increased to: ${gameState.difficulty.replace('-', ' ')}`;
    } else {
        messageElement.textContent = 'Already at maximum difficulty!';
    }
    
    // Start the game after a brief delay (so the user sees the message)
    setTimeout(() => {
        document.querySelector('.difficulty-change-overlay').classList.remove('active');
        document.querySelector('.difficulty-change-screen').classList.remove('active');
        elements.helpBtn.style.display = 'block';
        startGame();
    }, 1500); // 1.5-second delay before proceeding
});




// No button - keeps same difficulty and starts game
document.getElementById('increase-difficulty-no').addEventListener('click', () => {
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    startGame();
});

// End Game button - returns to start screen
document.getElementById('end-game-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    document.querySelector('.difficulty-change-overlay').classList.remove('active');
    document.querySelector('.difficulty-change-screen').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');
});



// Start the game
function startGame() {
    if (!gameState.difficulty) {
        updateMessage('Please select a difficulty first!');
        return;
    }

    // Switch screens
    screens.start.classList.add('hidden');
    screens.game.classList.add('active');

    resetGame();
    initializeBoard();
    renderBoard();
    
    // Determine who starts
    const playerStarts = Math.random() < 0.5;
    gameState.playerTurn = playerStarts;
    updateMessage(playerStarts ? 'You start first!' : 'Pepper starts first!');

    // Set help button state based on who starts
    elements.helpBtn.disabled = !playerStarts;
    
    if (!playerStarts) {
        setTimeout(computerTurn, 1500);
    }
}

// Reset game state
function resetGame() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    
    gameState = {
        difficulty: gameState.difficulty,
        board: Array(rows).fill().map(() => Array(cols).fill(0)),
        faceUp: Array(rows).fill().map(() => Array(cols).fill(false)),
        matchedPairs: Array(rows).fill().map(() => Array(cols).fill(false)),
        playerScore: 0,
        computerScore: 0,
        playerTurn: true,
        firstCard: null,
        waiting: false,
        seen_cards: Array(rows).fill().map(() => Array(cols).fill(0)),
        turnsTaken: 0

    };
    
    updateScores();
    elements.helpBtn.disabled = false; // Add this line
}

// Initialize the game board
function initializeBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const totalCards = rows * cols;
    const numPairs = totalCards / 2;
    
    // Create pairs of card values
    let cards = [];
    for (let i = 1; i <= numPairs; i++) {
        cards.push(i, i);
    }
    
    // Shuffle the cards
    shuffleArray(cards);
    
    // Fill the board
    let index = 0;
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            gameState.board[row][col] = cards[index++];
        }
    }
}

// Render the game board
function renderBoard() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    elements.gameBoard.innerHTML = '';
    elements.gameBoard.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const card = document.createElement('div');
            card.className = 'card';
            if (gameState.faceUp[row][col]) {
                card.classList.add('flipped');
            }
            card.dataset.row = row;
            card.dataset.col = col;

            if (gameState.matchedPairs[row][col]) {
                card.innerHTML = '<div class="empty-card"></div>';
                card.style.pointerEvents = 'none';
                card.style.opacity = '0.5';
            } else {
                const cardValue = gameState.board[row][col];
                card.innerHTML = `
                    <div class="card-inner">
                        <div class="card-front">
                            <img src="${config.cardImages[cardValue]}" 
                                 alt="Card ${cardValue}"
                                 onerror="this.src='${config.emptyCard}'">
                        </div>
                        <div class="card-back">
                            <img src="${config.cardBack}" alt="Card Back" onerror="this.src='${config.emptyCard}'">
                        </div>
                    </div>
                `;

                if (gameState.playerTurn && !gameState.waiting) {
                    card.addEventListener('click', () => handleCardClick(row, col));
                }
            }
            elements.gameBoard.appendChild(card);
        }
    }
}

// Handle card click
function handleCardClick(row, col) {
    if (gameState.waiting || !gameState.playerTurn || gameState.faceUp[row][col] || gameState.matchedPairs[row][col]) {
        return;
    }
    
    // Flip the card
    gameState.faceUp[row][col] = true;
    renderBoard();

    // Disable help button when first card is selected
    if (gameState.firstCard === null) {
        elements.helpBtn.disabled = true;
    }
    
    if (gameState.firstCard === null) {
        // First card selected
        gameState.firstCard = { row, col };
        gameState.seen_cards[row][col] = gameState.board[row][col];
    } else {
        // Second card selected
        gameState.waiting = true;
        const secondCard = { row, col };
        gameState.seen_cards[row][col] = gameState.board[row][col];

        console.log("Second card PLAYER:");
        console.log(secondCard);
        
        // Check for a match
        setTimeout(() => {
            checkMatch(gameState.firstCard, secondCard, 'player');
            gameState.firstCard = null;
            gameState.waiting = false;
   
            // If no match, switch turns
            if (!gameState.playerTurn) {
                setTimeout(computerTurn, 1500);
            }
        }, 1000);
    }

    console.log("First card PLAYER:");
    console.log(gameState.firstCard);

    
}

// Computer's turn
function computerTurn() {
    if (!gameState.playerTurn) {

        // First check if game is over
        if (isGameOver()) {
            return;
        }

        // Disable help button during computer's turn
        elements.helpBtn.disabled = true;
        updateMessage('Pepper is thinking...');

        
        setTimeout(() => {
            // Select first random card
            let firstCard_p = selectRandomCard();
            gameState.faceUp[firstCard_p.row][firstCard_p.col] = true;

            console.log("Firt card PEPPER");
            console.log(firstCard_p);
            renderBoard();

            // Get player's current accuracy (0–1)
            const playerAccuracy = getPlayerAccuracy();
            console.log('accu PLAY', playerAccuracy)

            let pepperAccuracy = 0.5;
            // Scale Pepper's accuracy based on player performance:
            // - If player is strong (accuracy > 0.7), Pepper becomes stronger (up to 1.0)
            // - If player is weak (accuracy < 0.3), Pepper stays weaker (down to 0.3)
            pepperAccuracy = Math.min(1, Math.max(0.3, playerAccuracy + 0.2));
            console.log('accu pepper', pepperAccuracy)
            updateMessage(`Pepper's accuracy: ${Math.round(pepperAccuracy * 100)}%`);

            
            setTimeout(() => {
                // Select second random card
                let secondCard_p = Strategy(firstCard_p, pepperAccuracy);
                console.log("Second card PEPPER");
                console.log(secondCard_p);
                gameState.faceUp[secondCard_p.row][secondCard_p.col] = true;
                renderBoard();
               
                // Check for a match
                setTimeout(() => {
                    checkMatch(firstCard_p, secondCard_p, 'computer');
                    
                    // If no match, switch turns
                    if (!gameState.playerTurn) {
                        setTimeout(computerTurn, 1500);
                    }
                }, 1000);


            gameState.seen_cards[firstCard_p.row][firstCard_p.col] = gameState.board[firstCard_p.row][firstCard_p.col];
            gameState.seen_cards[secondCard_p.row][secondCard_p.col] = gameState.board[secondCard_p.row][secondCard_p.col];
            console.log(gameState.seen_cards)
            }, 1000);

        }, 1000);
    }
}


function Strategy(card1, acc) {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    const card_type = gameState.board[card1.row][card1.col];
    const prob = Math.random();

    console.log("Probability check:", prob, "Accuracy:", acc);

    // Only try to find a match if probability <= accuracy
    if (prob <= acc) {
        // First try to find a matching card
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                // Check if this is a matching card that's not the first card
                if (gameState.seen_cards[row][col] === card_type && 
                    !(row === card1.row && col === card1.col)) {
                    console.log("Found matching card at:", {row, col});
                    return {row, col};  // Return the matching card
                }
            }
        }
        // If we get here, no match was found despite prob <= acc
        console.log("No match found despite accuracy chance");
    } else {
        console.log("Random selection due to probability > accuracy");
    }

    // If either:
    // 1. prob > acc (random selection forced)
    // 2. prob <= acc but no match was found
    return selectRandomCard(card1);  // Return a random card
}



// Select a random card that's not already face up or matched
function selectRandomCard(exclude = null) {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    let availableCards = [];
    
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.faceUp[row][col] && !gameState.matchedPairs[row][col]) {
                if (!exclude || row !== exclude.row || col !== exclude.col) {
                    availableCards.push({ row, col });
                }
            }
        }
    }
    
    if (availableCards.length === 0) return null;
    return availableCards[Math.floor(Math.random() * availableCards.length)];
}

// Check if two cards match
function checkMatch(card1, card2, player) {
    const match = gameState.board[card1.row][card1.col] === gameState.board[card2.row][card2.col];
    
    if (player === 'player'){
        gameState.turnsTaken++; // Count every attempt
    }

    if (match) {
        // Mark as matched
        gameState.matchedPairs[card1.row][card1.col] = true;
        gameState.matchedPairs[card2.row][card2.col] = true;
        
        // Update score
        if (player === 'player') {
            
            // gameState.playerStats.correctMatches++; // Count successes (puo essere sostituito da playerScore)
            gameState.playerScore++;
            updateMessage('Well done! It\'s your turn again!');
            // Re-enable help button if player's turn continues
            elements.helpBtn.disabled = false;
        } else {
            gameState.computerScore++;
            updateMessage('Match found! It\'s Pepper turn again!');
            // Keep help button disabled during computer's turn
            elements.helpBtn.disabled = true;
        }
        
        updateScores();
        gameState.waiting = false;
        gameState.firstCard = null;
    } else {
        // Flip cards back after delay
        setTimeout(() => {
            gameState.faceUp[card1.row][card1.col] = false;
            gameState.faceUp[card2.row][card2.col] = false;
            gameState.playerTurn = !gameState.playerTurn;
            gameState.waiting = false;
            gameState.firstCard = null;
            
            renderBoard();
            
            if (player === 'player') {
               
                elements.helpBtn.disabled = true; // Disable during computer's turn
                updateMessage('No match! Pepper\'s turn!');
                
                setTimeout(computerTurn, 3000);
            } else {
                updateMessage('No match for Pepper, is your turn!');
                // Re-enable help button when turn switches back to player
                elements.helpBtn.disabled = false;
            }
        }, 1000);
    }
    
    console.log('turns: ', gameState.turnsTaken)
    const playerAccuracy = getPlayerAccuracy();
    console.log('accccc: ', playerAccuracy)
    renderBoard();
    checkGameOver();
}

// Helper function to check if game is over
function isGameOver() {
    const { rows, cols } = config.difficulties[gameState.difficulty];
    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            if (!gameState.matchedPairs[row][col]) {
                return false;
            }
        }
    }
    return true;
}


// Update checkGameOver to use isGameOver
function checkGameOver() {
    if (isGameOver()) {
        // Game over

        let message, title;
        if (gameState.playerScore > gameState.computerScore) {
            title = 'Congratulations!';
            message = 'You win!';
        } else if (gameState.playerScore < gameState.computerScore) {
            title = 'Game Over!';
            message = 'Pepper wins!';
        } else {
            title = 'Game Over!';
            message = 'It\'s a tie!';
        }
        
        // Show end game message
        document.getElementById('end-game-title').textContent = title;
        document.getElementById('end-game-message').textContent = message;
        document.getElementById('final-player-score').textContent = gameState.playerScore;
        document.getElementById('final-computer-score').textContent = gameState.computerScore;
        
        // Show overlay and message
        document.querySelector('.end-game-overlay').classList.add('active');
        document.querySelector('.end-game-message').classList.add('active');
        
        // Hide help button during end game
        elements.helpBtn.style.display = 'none';
        
        gameState.playerTurn = false;
    }
}



// Update scores display
function updateScores() {
    elements.playerScore.textContent = gameState.playerScore;
    elements.computerScore.textContent = gameState.computerScore;
}

// Update message display
function updateMessage(text) {
    elements.message.textContent = text;
}

// Helper function to shuffle an array
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}



// Add this function to flip all cards face up
function flipAllCards(faceUp) {
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


function handleHelp() {
    if (gameState.waiting || !gameState.playerTurn || gameState.firstCard !== null) return;
    
    elements.helpBtn.disabled = true;
    flipAllCards(true);
    
    let secondsLeft = 5;
    // Initial message with large number
    elements.message.innerHTML = `Memorize the cards! They will flip back in <span class="countdown-number">${secondsLeft}</span> seconds...`;
    
    const countdownInterval = setInterval(() => {
        secondsLeft--;
        
        if (secondsLeft > 0) {
            // Update just the number (more efficient)
            document.querySelector('.countdown-number').textContent = secondsLeft;
        } else {
            clearInterval(countdownInterval);
            flipAllCards(false);
            elements.helpBtn.disabled = false;
            elements.message.textContent = 'Cards hidden! Your turn continues...';
        }
    }, 1000);
    
    setTimeout(() => {
        clearInterval(countdownInterval);
    }, 5000);
}



// Add this event listener at the end of your initialization code
elements.helpBtn.addEventListener('click', handleHelp);


// Play Again button - restarts the game with same difficulty
document.getElementById('play-again-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    startGame();
});

// End Game button - returns to start screen
document.getElementById('end-game-btn').addEventListener('click', () => {
    document.querySelector('.end-game-overlay').classList.remove('active');
    document.querySelector('.end-game-message').classList.remove('active');
    elements.helpBtn.style.display = 'block';
    screens.game.classList.remove('active');
    screens.start.classList.remove('hidden');
});







function getPlayerAccuracy() {
    
    
    if (gameState.turnsTaken === 0) return 0; // Avoid division by zero
    
    const accuracy = (gameState.playerScore / gameState.turnsTaken);

   
    return accuracy; // Round to nearest integer

    
}









