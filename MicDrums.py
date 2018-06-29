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
    maxAmplitude = block.max()
    minAmplitude = block.min()

    loudestSample = max(abs(maxAmplitude.max()), abs(minAmplitude.min()))

    if loudestSample >= snareGateValue:
        print("Snare drum on ", offset)
        return offset, "snare"
    if loudestSample >= kickGateValue:
        print("Kick drum on ", offset)
        return offset, "kick"

    return None, None

def removeDublicates(drums, types):
    needMoreIterations = True
    while needMoreIterations:
        needMoreIterations = False
        for i in range(0, len(drums) - 1):
            nextSample = drums[i+1]
            currentSample = drums[i]
            if nextSample - currentSample <= maxDrumWidth:
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

def convertSamplesToTime(kicksPosition, snaresPosition, rate):
    for i in range(0, len(kicksPosition)):
        kicksPosition[i] = kicksPosition[i] * 1.0 / rate
    for i in range(0, len(snaresPosition)):
        snaresPosition[i] = snaresPosition[i] * 1.0 / rate

    return kicksPosition, snaresPosition

def generate_drum_beat(drumSample, positions, rate):
    generatedClip = np.array([[0.0,0.0]] * (int(positions[len(positions) - 1] * rate) + len(drumSample)))
    for i in range(0, len(positions)):
        generatedClip = add_drum_to_clip(generatedClip, drumSample, positions[i], rate)
    return generatedClip

def add_drum_to_clip(clip, drumSample, time, rate):
    firstSampleIdx = int(time * rate)
    for i in range(firstSampleIdx, min(len(clip), firstSampleIdx + len(drumSample))):
        nextSample = drumSample[i - firstSampleIdx]
        clip[i] = nextSample
    return clip

def mix(firstTrack, secondTrack):
    if firstTrack.size > secondTrack.size:
        mix = firstTrack
        minSize = int(secondTrack.size / 2 - 1)
    else:
        mix = secondTrack
        minSize = int(firstTrack.size / 2 - 1)

    for i in range(0, minSize):
        mix[i] = firstTrack[i] + secondTrack[i]
    return mix


rate, s = wavfile.read('/home/whale/Desktop/rawBeat.wav')

s = normalize(s)

kicks, snares = mapDrums(s)
print("kicks: ", kicks)
print("snares: ", snares)

# we have sample numbers where all kicks and snares is
# now we need to make clip with kicks and snares sounds

# convert sample numbers to time according to input clip SampleRate
kicksTime, snaresTime = convertSamplesToTime(kicks, snares, rate)
print("kicksT: ", kicksTime)
print("snaresT: ", snaresTime)

# get kick and snares audio clips (must be prepared before loading)
kickRate, kickClip = wavfile.read('/home/whale/Desktop/kickClip.wav')
snareRate, snareClip = wavfile.read('/home/whale/Desktop/snareClip.wav')

generatedKicks = generate_drum_beat(kickClip, kicks, kickRate)
generatedSnares = generate_drum_beat(snareClip, snares, snareRate)

wavfile.write("generatedKickBeat.wav", kickRate, generatedKicks)
wavfile.write("generatedSnareBeat.wav", snareRate, generatedSnares)
wavfile.write("generatedMixtape.wav", kickRate, mix(generatedKicks, generatedSnares))

plt.plot(generatedKicks)
plt.show()