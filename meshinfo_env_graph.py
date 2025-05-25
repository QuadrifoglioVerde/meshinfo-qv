import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import io
import base64
import random

def draw_env_graph(telemetry):
    data = {
        "temperature": [],
        "relative_humidity": [],
        "barometric_pressure": [],
        "gas_resistance": [],
        "ts_created": []
    }

    for datapoint in telemetry:
        for key in data:
            data[key].append(datapoint[key])

    if not data["temperature"]:
        return None

    # Převod timestampů
    time_stamps = [
        datetime.datetime.fromtimestamp(int(t)) for t in data["ts_created"]
    ]

    fig, ax1 = plt.subplots(figsize=(10, 4))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %Hh'))

    ax1.set_xlabel("Čas")
    ax1.set_ylabel("Teplota (°C) / Relativní vlhkost (%)", color="tab:red")
    ax1.plot(time_stamps, data["temperature"], label="Teplota", marker="o", color="tab:red")
    ax1.plot(time_stamps, data["relative_humidity"], label="Relativní vlhkost", marker="s", linestyle="--", color="tab:orange")
    ax1.tick_params(axis='y', labelcolor="tab:red")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Tlak (hPa) / Odpor plynu (Ω)", color="tab:blue")
    ax2.plot(time_stamps, data["barometric_pressure"], label="Tlak", marker="^", linestyle="-.", color="tab:blue")
    ax2.plot(time_stamps, data["gas_resistance"], label="Odpor plynu", marker="x", linestyle=":", color="tab:green")
    ax2.tick_params(axis='y', labelcolor="tab:blue")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Telemetrie Senzorů za posledních 24h")
    fig.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return img_base64
