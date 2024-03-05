from requests import Response
import json
import numpy as np
import os
import matplotlib.pyplot as plt

logs = []


def dump_response(api_name, request: dict, response: Response):
    logs.append("*" * 50 + "\n")
    logs.append(f"API name: {api_name}".center(50) + "\n")
    logs.append("*" * 50 + "\n")
    logs.append("Request data: \n")
    logs.append(str(request))
    logs.append("\n\n")

    logs.append(f"Response Status Code: {response.status_code}: \n")
    logs.append("Response data: \n")
    try:
        logs.append(str(response.json()))
    except:
        logs.append(str(response.text))
    logs.append("\n" + "*" * 50 + "\n\n")


def save_logs(name):
    with open(name, "w") as f:
        f.writelines(logs)


def evaluate_footprints(footprints: dict, model) -> int:
    spectro1, spectro2, spectro3 = (
        _process_footprint(footprints["1"]),
        _process_footprint(footprints["2"]),
        _process_footprint(footprints["3"]),
    )
    ys = []
    for spectro in [spectro1, spectro2, spectro3]:
        y = model.predict(spectro, verbose=0)
        ys.append(y)
    real_channels = np.where(np.array(ys) > 0)[0]
    if len(real_channels) == 0:
        return 0
    if len(real_channels) == 1:
        return real_channels[0] + 1
    return int(np.argmax(ys) + 1)


def _process_footprint(footprint: dict):
    spectro = np.array(footprint)
    spectro[spectro == np.inf] = np.float16(65500.0)
    spectro = spectro.reshape(1, *spectro.shape, 1)

    return spectro


def load_dataset(path):
    real_ds = np.load(os.path.join(path, "real.npz"))
    fake_ds = np.load(os.path.join(path, "fake.npz"))
    x_real, y_real = real_ds["x"], real_ds["y"]
    x_fake, y_fake = fake_ds["x"], fake_ds["y"]
    return x_real, y_real, x_fake, y_fake


def plot_spectrogram(spectrogram, ax=None):
    if len(spectrogram.shape) > 2:
        assert len(spectrogram.shape) == 3
        spectrogram = np.squeeze(spectrogram, axis=-1)
    log_spec = np.log(spectrogram.T + np.finfo(np.float32).eps)
    height = log_spec.shape[0]
    width = log_spec.shape[1]
    X = np.linspace(0, width, num=width, dtype=int)
    Y = range(height)
    if ax is None:
        plt.pcolormesh(X, Y, log_spec)
        plt.colorbar(label="Intensity")
        plt.xlabel("Time (ms)")
        plt.ylabel("Frequency (Hz)")
        plt.title("Spectrogram")
    else:
        ax.pcolormesh(X, Y, log_spec)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Frequency (Hz)")
        ax.set_title("Spectrogram")


def expand_y(y, new_size):
    scalar = new_size // y.shape[0]
    y_processed = np.zeros((new_size,))
    for i in range(y.shape[0]):
        y_processed[i * scalar : i * scalar + scalar] = y[i]
    return y_processed
