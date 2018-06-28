import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

snareGateValue = 0.7
kickGateValue = 0.7 / 5.0
mappingBlockSize = 512
maxDrumWidth = 5000

def normalize(s):
	maxAmplitude = np.max(np.absolute(s))

	normalized = s / maxAmplitude

	return normalized

def mapDrums(clip):
    positions = []
    types = []
    blockCount = int(len(clip) / mappingBlockSize)
    for blockNumber in range (0, blockCount):
        blockFirstIdx = blockNumber * mappingBlockSize
        blockLastIdx = min(blockFirstIdx + mappingBlockSize-1, len(clip) - 1)
        block = clip[blockFirstIdx:blockLastIdx]
        drumPosition, drumType = processBlock(block, blockFirstIdx)
        if type(drumPosition) == int:
            positions.append(drumPosition)
            types.append(drumType)

    print("Drums: ", positions)
    print("Types: ", types)
    positionsWithoutDublicates, typesWithoutDublicates = removeDublicates(positions, types)
    print("Positions without dublicates: ", positionsWithoutDublicates)
    print("Types without dublicates: ", typesWithoutDublicates)
    return separateDrums(positionsWithoutDublicates, typesWithoutDublicates)

def processBlock(block, offset):
    maxAmplitude = max(block)
    minAmplitude = min(block)

    loudestSample1 = max(abs(maxAmplitude[0]), abs(minAmplitude[0]))
    loudestSample2 = max(abs(maxAmplitude[1]), abs(minAmplitude[1]))
    loudestSample = max(loudestSample1, loudestSample2)

    if loudestSample >= snareGateValue:
        print("Snare drum on ", offset)
        return offset, "snare"
    if loudestSample >= kickGateValue:
        print("Kick drum on ", offset)
        return offset, "kick"

    return [], []

def removeDublicates(drums, types):
    needMoreIterations = True
    while needMoreIterations:
        needMoreIterations = False
        for i in range(0, len(drums) - 1):
            if drums[i+1] - drums[i] <= maxDrumWidth:
                if types[i] == "kick":
                    types.pop(i)
                    drums.pop(i)
                else:
                    types.pop(i+1)
                    drums.pop(i+1)
                needMoreIterations = True
                i += 1
                if i >= len(drums) - 1:
                    break
    return drums, types

def separateDrums(positions, types):
    snares = []
    kicks = []

    for i in range(0, len(positions)):
        if types[i] == "kick":
            kicks.append(positions[i])
        else:
            snares.append(positions[i])

    return kicks, snares


rate, s = wavfile.read('/home/whale/Desktop/rawBeat.wav')

s = normalize(s)

kicks, snares = mapDrums(s.tolist())
print("kicks: ", kicks)
print("snares: ", snares)

plt.plot(s)
plt.show()

wavfile.write('beatStage1.wav', rate, s)