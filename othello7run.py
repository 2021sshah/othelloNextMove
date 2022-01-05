# Siddharth Shah Gabor Pd. 2
import sys, time

def manageInputs(sysList):
    board, tokenToPlay = "."*27+"ox......xo"+"."*27, ""
    for sysIn in sysList:
        sysIn = sysIn.lower()
        if len(sysIn) == 64: board = sysIn
        elif sysIn in symSWITCH: tokenToPlay = sysIn
    if not tokenToPlay:
        periods = board.count(".")
        if periods%2: tokenToPlay = "o"
        else: tokenToPlay = "x"
    return board, tokenToPlay

def setGlobals():
    # Constraints
    h = w = 8
    horiz = [[*range(i, i+w)] for i in range(0, h*w, w)]
    vert = [[*range(i, h*w, w)] for i in range(0, w)]
    mainDiag = [[idx for idx in range(i, h*w, 1+w) if idx%w - i%w == idx//w - i//w] for i in range(0, w*h) if not i//w or not i%w]
    offDiag = [[idx for idx in range(i, h*w, w-1) if i%w - idx%w == idx//w - i//w] for i in range(0, w*h) if not i//w or i%w == w-1]
    CONSTRAINTS = horiz + vert + mainDiag + offDiag
    idxToCONST = [[] for i in range(h*w)]
    for const in CONSTRAINTS:
        for idx in const:
            idxToCONST[idx].append(const)
    # Sequences Dictionary
    let, num = "abcdefgh", "12345678"
    noteToIDX = {let[r]+num[c]:r*8+c for r in range(8) for c in range(8)}
    return CONSTRAINTS, idxToCONST, noteToIDX

def setCornerConsts():
    cornerLsts = [[0,1,2,3,4,5,6,7], [0,8,16,24,32,40,48,56], [56,57,58,59,60,61,62,63], [7,15,23,31,39,47,55,63]]
    return [(lst,{*lst}) for lst in cornerLsts]

def possibleNextMoves(board, tokenToPlay):
    toCheck = []
    for idx, value in enumerate(board):
        if value != ".": continue
        for const in idxToCONST[idx]:
            splitIdx = const.index(idx)
            upper, lower = const[:splitIdx][::-1], const[splitIdx+1:]
            upperVals, lowerVals = convertToValues(board, upper), convertToValues(board, lower)
            toCheck.append((idx, upper, upperVals))
            toCheck.append((idx, lower, lowerVals))
    setPsblIndices, toConvert = set(), {tup[0]:{tup[0]} for tup in toCheck}
    sym, otherSym = tokenToPlay, symSWITCH[tokenToPlay]
    for idx, seg, segVals in toCheck:
        if sym not in segVals: continue
        upToIdx = 0
        while segVals[upToIdx] == otherSym: upToIdx += 1
        if upToIdx != 0 and segVals[upToIdx] == sym: 
            setPsblIndices.add(idx)
            toConvert[idx] |= {*seg[:upToIdx]}
    return setPsblIndices, toConvert

def convertToValues(board, structure):
    return [board[idx] for idx in structure]

def convertBoardSegment(board, sym, segOfIndices):
    boardArray = list(board)
    for idx in segOfIndices: boardArray[idx] = sym
    return "".join(boardArray)

def connectedToCorner(idx):
    return idx%8 == 0 or idx%8 == 7 or idx//8 == 0 or idx//8 == 7

def capturedCorner(board, tokenToPlay, idx):
    for cornerConstLst, cornerConstSet in cornerConst:
        if idx in cornerConstSet:
            splitIdx = cornerConstLst.index(idx)
            upper, lower = cornerConstLst[:splitIdx], cornerConstLst[splitIdx+1:]
            upperVals, lowerVals = convertToValues(board, upper), convertToValues(board, lower)
            if upperVals == [tokenToPlay]*len(upperVals) or lowerVals == [tokenToPlay]*len(lowerVals): return True
    return False

# Othello 4 Heuristic
def pickBestMove(board, tokenToPlay, psblIdxSet, numFlippedDct):
    psblH = {idx:0 for idx in psblIdxSet}
    for idx in psblIdxSet:
        if idx in CORNERS: psblH[idx] += 40
        if not idx in CORNERS and connectedToCorner(idx):
            if capturedCorner(board, tokenToPlay, idx): psblH[idx] += 40
            else: psblH[idx] -= 10
        newBoard = convertBoardSegment(board, tokenToPlay, numFlippedDct[idx])
        opponentMoveSet, oppFlippedDct = possibleNextMoves(newBoard, symSWITCH[tokenToPlay])
        for otherIdx in opponentMoveSet:
            if otherIdx in CORNERS: psblH[idx] -= 40
            psblH[idx] -= len(oppFlippedDct[otherIdx])
        #if endgame -> go for coins, else -> go for less coins
        if board.count("x") > 30 or board.count("o") > 30: psblH[idx] += len(numFlippedDct[idx])
        else: psblH[idx] -= len(numFlippedDct[idx])
    # Return idx with Max Heuristic value
    hToIdx = [(h,idx) for idx, h in psblH.items()]
    return sorted(hToIdx)[::-1]

CACHE = {} # Board, Token to negaList
def alphaBetaTerminal(board, tokenToPlay, lower, upper, level):
    if (board,tokenToPlay,lower,upper) in CACHE: return CACHE[(board,tokenToPlay,lower,upper)] # Already Visited
    if not "." in board: # Terminal Board
        CACHE[(board,tokenToPlay,lower,upper)] = [2*board.count(tokenToPlay) - 64]
        return CACHE[(board,tokenToPlay,lower,upper)]
    psblIdxSet, numFlippedDct = possibleNextMoves(board, tokenToPlay)
    hToIdx = pickBestMove(board, tokenToPlay, psblIdxSet, numFlippedDct)
    if not psblIdxSet:
        otherToken = symSWITCH[tokenToPlay]
        otherIdxTup = possibleNextMoves(board, otherToken) # (otherIdxSet, otherFlippedDct)
        if not otherIdxTup[0]: # Terminal Board
            CACHE[(board,tokenToPlay,lower,upper)] = [board.count(tokenToPlay) - board.count(otherToken)]
            return CACHE[(board,tokenToPlay,lower,upper)]
        nm = alphaBetaTerminal(board, symSWITCH[tokenToPlay], -upper, -lower, level)
        nmScore = [-nm[0]] + nm[1:]
        CACHE[(board,tokenToPlay,lower,upper)] = nmScore
        return nmScore
    # Recursion Loop
    best = [-len(board)-1]
    for moveTup in hToIdx: # (h, idx) in decreasing order of h
        idx = moveTup[1]
        nm = alphaBetaTerminal(convertBoardSegment(board, tokenToPlay, numFlippedDct[idx]), symSWITCH[tokenToPlay], -upper, -lower, level+1)+[idx]
        nmScore = [-nm[0]] + nm[1:] # Negate enemy for myScore
        if nmScore[0] > upper: return [nmScore[0]] # Terminate right away
        if nmScore[0] > lower:
            best = nmScore
            lower = nmScore[0]
            if level == 0: print(best[-1])
    CACHE[(board,tokenToPlay,lower,upper)] = best
    return best

# Othello 7 Midgame Board Weighting
idxToWeight =   [20, -3, 11, 8, 8, 11, -3, 20,
    	        -3, -7, -4, 1, 1, -4, -7, -3,
    	        11, -4, 2, 2, 2, 2, -4, 11,
    	        8, 1, 2, -3, -3, 2, 1, 8,
    	        8, 1, 2, -3, -3, 2, 1, 8,
    	        11, -4, 2, 2, 2, 2, -4, 11,
    	        -3, -7, -4, 1, 1, -4, -7, -3,
    	        20, -3, 11, 8, 8, 11, -3, 20]

def calcPositions(board, myTkn, oppTkn):
    dct = {myTkn:0, oppTkn:0}
    for idx, val in enumerate(board):
        if not idx == ".": dct[val] += idxToWeight[idx]
    return dct[myTkn], dct[oppTkn]

adjIndices = {1, 8, 9, 6, 14, 15, 48, 49, 57, 54, 55, 62}
def calcCloseness(board, myTkn, oppTkn):
    dct = {myTkn:0, oppTkn:0}
    for idx in adjIndices:
        idxVal = board[idx]
        if idxVal == ".": continue
        dct[idxVal] += 1
    return dct[myTkn], dct[oppTkn]

def boardScore(board, tokenToPlay):
    # Piece Weighting
    myPosition, oppPosition = calcPositions(board, tokenToPlay, symSWITCH[tokenToPlay])
    weight = (myPosition-oppPosition)/(myPosition-oppPosition)
    # Coin Parity
    myTkns, oppTkns = board.count(tokenToPlay), board.count(symSWITCH[tokenToPlay])
    if myTkns > oppTkns: parity = (100*myTkns)/(myTkns+oppTkns)
    elif oppTkns > myTkns: parity = -(100*oppTkns)/(myTkns+oppTkns)
    else: parity = 0
    # Mobility
    myMoves, oppMoves = len(possibleNextMoves(board, tokenToPlay)), len(possibleNextMoves(board, symSWITCH[tokenToPlay]))
    if myMoves > oppMoves: mobility = (100*myMoves)/(myMoves+oppMoves)
    elif oppMoves > myMoves: mobility = -(100*oppMoves)/(myMoves+oppMoves)
    else: mobility = 0
    # Corners Captured
    myCorners, oppCorners = len([idx for idx in CORNERS if board[idx] == tokenToPlay]), len([idx for idx in CORNERS if board[idx] == symSWITCH[tokenToPlay]])
    corners = 25*(myCorners-oppCorners)
    # Stability
    myClose, oppClose = calcCloseness(board, tokenToPlay, symSWITCH[tokenToPlay])
    stabil = -12.5*(myClose-oppClose)
    score = (10 * weight) + (10 * parity) + (801.724 * corners) + (382.026 * stabil) + (78.922 * mobility)
    return score

midCACHE = {} # Board, Token to negaList
def alphaBetaMidgame(board, tokenToPlay, lower, upper, level, targetLevel):
    if (board,tokenToPlay,lower,upper) in midCACHE: return midCACHE[(board,tokenToPlay,lower,upper)] # Already Visited
    if level == targetLevel: return boardScore(board, tokenToPlay)
    psblIdxSet, numFlippedDct = possibleNextMoves(board, tokenToPlay)
    hToIdx = pickBestMove(board, tokenToPlay, psblIdxSet, numFlippedDct)
    if not psblIdxSet:
        otherToken = symSWITCH[tokenToPlay]
        otherIdxTup = possibleNextMoves(board, otherToken) # (otherIdxSet, otherFlippedDct)
        if not otherIdxTup[0]: # Terminal Board
            score = (board.count(tokenToPlay)-board.count(otherToken))/board.count(tokenToPlay)
            midCACHE[(board,tokenToPlay,lower,upper)] = [score]
            return midCACHE[(board,tokenToPlay,lower,upper)]
        nm = alphaBetaMidgame(board, symSWITCH[tokenToPlay], -upper, -lower, level+1, targetLevel) # Forced Pass
        nmScore = [-nm[0]] + nm[1:]
        CACHE[(board,tokenToPlay,lower,upper)] = nmScore
        return nmScore
    # Recursion Loop
    best = [1-lower]
    for moveTup in hToIdx: # (h, idx) in decreasing order of h
        idx = moveTup[1]
        ab = alphaBetaMidgame(convertBoardSegment(board, tokenToPlay, numFlippedDct[idx]), symSWITCH[tokenToPlay], -upper, -lower, level+1, targetLevel)+[idx]
        if -ab[0] > upper: return [-ab[0]] # Terminate right away
        if ab[0] < best[0]:
            best = nm
            lower = -best[0]+1
    midCACHE[(board,tokenToPlay,lower,upper)] = [-best[0]] + best[1:] 
    return [-best[0]] + best[1:] 

def midGame(board, tokenToPlay):
    psblIdxSet, numFlippedDct = possibleNextMoves(board, tokenToPlay)
    hToIdx = pickBestMove(board, tokenToPlay, psblIdxSet, numFlippedDct)
    upper = 100000
    best = [upper]                                              # The negative of lower
    for targetLevel in range(3,9,1):                               # Iterative deepening to level 6
        for moveTup in hToIdx:
            idx = moveTup[1]
            ab = alphaBetaMidgame(convertBoardSegment(board, tokenToPlay, numFlippedDct[idx]), symSWITCH[tokenToPlay], -upper, best[0], 1, targetLevel)+[idx]
            if -ab[0] < -best[0]: continue                  # ab[0] & best[0] from the enemy's pt of view
            best = ab + [idx]                                                # A new personal best
            print ("At depth {} AB-MG returns {}".format(targetLevel, best))   # An improved move
            midCACHE.clear()

startTime = time.time()
# Inputs
symSWITCH = {"x":"o", "o":"x"}
board, tokenToPlay = manageInputs(sys.argv[1:])
# Initializations
CONSTRAINTS, idxToCONST, noteToIDX = setGlobals()
CORNERS = {0, 7, 56, 63}
cornerConst = setCornerConsts()
# Solve Routine
psblIdxSet, numFlippedDct = possibleNextMoves(board, tokenToPlay)
hToIdx = pickBestMove(board, tokenToPlay, psblIdxSet, numFlippedDct)
print(hToIdx[0][1])
if board.count(".") < 14: alphaBetaTerminal(board, tokenToPlay, -len(board), len(board), 0)
else: midGame(board, tokenToPlay)
print("Total Time: {}s".format(round(time.time()-startTime,3)))