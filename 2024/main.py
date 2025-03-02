# from models import *

# mconf = GPTConfig(train_dataset.vocab_size, train_dataset.block_size,
#                   n_layer=8, n_head=8, n_embd=512)
# model = GPT(mconf)


import numpy as np
import librosa
import matplotlib.pyplot as plt

# Load the audio file
filename = '/Users/johncabrahams/Music/Spotify_Playlists/Milan-Darling-Milan/veggi, DijahSB - EXCEPTIONAL.wav'
y, sr = librosa.load(filename, sr=None)

# Apply FFT
N = len(y)
T = 1.0 / sr
yf = np.fft.fft(y)
xf = np.fft.fftfreq(N, T)[:N//2]

# Plot the frequency spectrum
plt.figure(figsize=(12, 6))
plt.plot(xf, 2.0/N * np.abs(yf[:N//2]))
plt.title('Frequency Spectrum')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()
plt.show()