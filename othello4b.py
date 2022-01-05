# Siddharth Shah Gabor Pd. 2
# 78% is 100, 76% is 98, Below 76 -> double the difference and subtract from 98
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
    # Sequences Dict
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
    return setPsblIndices, {idx:len(val) for idx, val in toConvert.items()}

def convertToValues(board, structure):
    return [board[idx] for idx in structure]

def convertBoardSegment(board, sym, segOfIndices):
    boardArray = list(board)
    for idx in segOfIndices: boardArray[idx] = sym
    return "".join(boardArray)

def makeMove(board, moveIdx, tokenToPlay):
    if moveIdx < 0: return board # Invalid move
    toCheck = []
    for const in idxToCONST[moveIdx]:
        splitIdx = const.index(moveIdx)
        upper, lower = const[:splitIdx][::-1], const[splitIdx+1:]
        upperVals, lowerVals = convertToValues(board, upper), convertToValues(board, lower)
        toCheck.append((upper, upperVals))
        toCheck.append((lower, lowerVals))
    sym, otherSym = tokenToPlay, symSWITCH[tokenToPlay]
    toConvert = {moveIdx}
    for seg, segVals in toCheck:
        if sym not in segVals: continue
        upToIdx = 0
        while segVals[upToIdx] == otherSym: upToIdx += 1 # No Segment if hits . or same sym
        if upToIdx != 0 and segVals[upToIdx] == sym: toConvert |= {*seg[:upToIdx]}
    return convertBoardSegment(board, tokenToPlay, toConvert)

def pickBestMove(board, psblIdxSet, numFlippedDct, tokenToPlay):
    psblH = {idx:0 for idx in psblIdxSet}
    for idx in psblIdxSet:
        if idx in CORNERS: psblH[idx] += 40
        if not idx in CORNERS and connectedToCorner(idx):
            if capturedCorner(board, tokenToPlay, idx): psblH[idx] += 40
            else: psblH[idx] -= 10
        newBoard = makeMove(board, idx, tokenToPlay)
        opponentMoveSet, oppFlippedDct = possibleNextMoves(newBoard, symSWITCH[tokenToPlay])
        for otherIdx in opponentMoveSet:
            if otherIdx in CORNERS: psblH[idx] -= 40
            psblH[idx] -= oppFlippedDct[otherIdx]
        #if endgame -> go for coins, else -> go for less coins
        if board.count("x") > 30 or board.count("o") > 30: psblH[idx] += numFlippedDct[idx]
        else: psblH[idx] -= numFlippedDct[idx]
    # Return idx with Max Heuristic value
    maxH, val = -1000, 0
    for idx, h in psblH.items():
        if h > maxH: maxH, val = h, idx
    return val

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
print(pickBestMove(board, psblIdxSet, numFlippedDct, tokenToPlay))