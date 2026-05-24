"""Build hw3_report.pdf from precomputed results in _pdf_results.json."""
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

with open("_pdf_results.json") as f:
    r = json.load(f)

EC2_TEXT = (
    "For this assignment, I used an Amazon EC2 instance as my remote compute environment. "
    "After starting the EC2 instance through the Northwestern AWS portal, I connected to it "
    "from my local machine using SSH with port forwarding. The SSH command forwarded port 8888 "
    "on my local computer to port 8888 on the EC2 instance, which allowed me to access Jupyter "
    "Notebook in my local browser.\n\n"
    "On the EC2 instance, I ran Jupyter Notebook inside a Docker container using the Jupyter "
    "PySpark notebook image. The Docker command mapped the container's Jupyter port to the EC2 "
    "instance's port 8888 and mounted the EC2 project directory into the container. Specifically, "
    "the EC2 folder /home/ec2-user/my_project was mounted to /home/jovyan/work inside the "
    "container. This allowed files created in Jupyter to persist on the EC2 instance even if "
    "the Docker container was stopped or removed.\n\n"
    "I used the quay.io/jupyter/pyspark-notebook:latest Docker image because it includes Jupyter "
    "and PySpark tools needed for the assignment. After starting the container, I opened Jupyter "
    "Notebook locally at http://localhost:8888/tree using the token printed in the Docker output."
)

CLEAN_RULES = (
    "Cleaning rules applied to the unioned dataset:\n"
    "  1. Drop rows with null pickup or drop-off timestamps.\n"
    "  2. Drop trips with trip_distance <= 0 (zero/negative mileage is invalid).\n"
    "  3. Drop trips with fare_amount < 0 (negative fares treated as data errors).\n"
    "  4. Drop trips with total_amount < 0.\n"
    "  5. Drop trips where dropoff_datetime < pickup_datetime (impossible).\n"
    "  6. Drop trips longer than 24 hours (almost certainly meter errors or "
    "forgotten-running meters, not real rides).\n\n"
    f"Result: {r['before']:,} rows before cleaning -> {r['after']:,} after "
    f"({r['removed_pct']:.2f}% removed)."
)

COEFFS = [
    ("taxi_type_ohe[4]",   +3.6563),
    ("taxi_type_ohe[1]",   -2.7689),
    ("taxi_type_ohe[0]",   +2.7689),
    ("passenger_count",    +1.3351),
    ("taxi_type_ohe[5]",   +0.8030),
    ("pickup_dow",         -0.2785),
    ("trip_duration_min",  +0.2613),
    ("taxi_type_ohe[2]",   -0.2611),
    ("taxi_type_ohe[3]",   -0.1149),
    ("PULocationID",       -0.0310),
    ("DOLocationID",       -0.0171),
    ("trip_distance",      +0.0114),
    ("pickup_hour",        +0.0003),
]

PREDICTOR_ANALYSIS = (
    "Predictor analysis: The dominant magnitudes are the one-hot slots for "
    "taxi_type and payment_type (the printout labels every OHE slot 'taxi_type_ohe[i]' "
    "but only two are taxi_type; the rest are payment_type). The symmetric +-2.77 pair is a "
    "classic OHE level shift between taxi types. The most diagnostic numeric result is "
    "trip_distance = +0.0114, which is far below the real ~$3/mile NYC rate. This signals "
    "multicollinearity with trip_duration_min (+0.2613): the two features are highly "
    "correlated and the regression splits the metered-fare signal between them. "
    "passenger_count (+1.34) is too large to be causal -- NYC meters ignore rider count -- "
    "and is really a proxy for airport/group trips. pickup_hour (~0) and pickup_dow (-0.28) "
    "barely move the prediction once distance/duration are controlled. PULocationID and "
    "DOLocationID are tiny because they were treated as raw integers; one-hot encoding the "
    "zones would expose the real geographic effect."
)

def add_text_page(pdf, title, body, fontsize=10):
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.08, 0.94, title, fontsize=16, fontweight="bold")
    fig.text(0.08, 0.05, body, fontsize=fontsize, wrap=True,
             verticalalignment="bottom", horizontalalignment="left",
             family="DejaVu Sans")
    ax = fig.add_axes([0.08, 0.08, 0.84, 0.84])
    ax.axis("off")
    ax.text(0, 1, body, fontsize=fontsize, va="top", ha="left", wrap=True,
            family="DejaVu Sans")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def add_table_page(pdf, title, sections):
    """sections = list of (heading, body_text_or_None, table_rows_or_None)."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.08, 0.95, title, fontsize=16, fontweight="bold")
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.88])
    ax.axis("off")

    y = 0.95
    for heading, body, table in sections:
        ax.text(0, y, heading, fontsize=12, fontweight="bold", va="top")
        y -= 0.035
        if body:
            ax.text(0, y, body, fontsize=10, va="top", wrap=True)
            n_lines = body.count("\n") + 1
            y -= 0.022 * n_lines + 0.015
        if table:
            col_labels, rows = table
            tbl = ax.table(
                cellText=rows, colLabels=col_labels, loc="upper left",
                bbox=[0.0, y - 0.05 * (len(rows) + 1), 0.6, 0.05 * (len(rows) + 1)],
                cellLoc="left",
            )
            tbl.auto_set_font_size(False)
            tbl.set_fontsize(10)
            for (rrow, ccol), cell in tbl.get_celld().items():
                if rrow == 0:
                    cell.set_facecolor("#dddddd")
                    cell.set_text_props(weight="bold")
            y -= 0.05 * (len(rows) + 1) + 0.03
        y -= 0.01

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def add_coef_plot_page(pdf):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 8.5))
    fig.suptitle("Question 5 — Linear Regression Results", fontsize=14, fontweight="bold")

    names = [c[0] for c in COEFFS]
    vals = [c[1] for c in COEFFS]
    colors = ["#2a7" if v >= 0 else "#c33" for v in vals]
    ax1.barh(range(len(names)), vals, color=colors)
    ax1.set_yticks(range(len(names)))
    ax1.set_yticklabels(names, fontsize=9)
    ax1.invert_yaxis()
    ax1.axvline(0, color="black", linewidth=0.5)
    ax1.set_xlabel("Coefficient value")
    ax1.set_title("Coefficients (intercept = 19.8562)", fontsize=11)
    ax1.grid(axis="x", alpha=0.3)

    ax2.axis("off")
    metrics_text = (
        f"Training RMSE: {r['q5_train_rmse']:.4f}\n"
        f"Testing  RMSE: {r['q5_test_rmse']:.4f}\n\n"
        f"Train/test gap is small -> the model is not overfitting,\n"
        f"it is simply structurally limited (see analysis below)."
    )
    ax2.text(0, 1, "Model performance", fontsize=12, fontweight="bold", va="top")
    ax2.text(0, 0.92, metrics_text, fontsize=10, va="top", family="DejaVu Sans Mono")

    ax2.text(0, 0.65, "Predictor analysis", fontsize=12, fontweight="bold", va="top")
    ax2.text(0, 0.62, PREDICTOR_ANALYSIS, fontsize=9, va="top", wrap=True)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

out = "hw3_report.pdf"
with PdfPages(out) as pdf:
    # Page 1: title + EC2 + dataset + cleaning
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.9])
    ax.axis("off")

    ax.text(0, 1.0, "Homework 3 — NYC Taxi Analytics", fontsize=18, fontweight="bold", va="top")
    ax.text(0, 0.97, "Evan Barnett", fontsize=11, va="top", color="#555")

    ax.text(0, 0.93, "Dataset", fontsize=13, fontweight="bold", va="top")
    ax.text(0, 0.905,
            "January 2026 NYC TLC trip records\n"
            "  - yellow_tripdata_2026-01.parquet\n"
            "  - green_tripdata_2026-01.parquet",
            fontsize=10, va="top", family="DejaVu Sans Mono")

    ax.text(0, 0.83, "EC2 Setup", fontsize=13, fontweight="bold", va="top")
    ax.text(0, 0.805, EC2_TEXT, fontsize=9.5, va="top", wrap=True)

    ax.text(0, 0.36, "Data Cleaning Assumptions", fontsize=13, fontweight="bold", va="top")
    ax.text(0, 0.335, CLEAN_RULES, fontsize=9.5, va="top", family="DejaVu Sans")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # Page 2: Q1-Q4
    fig = plt.figure(figsize=(8.5, 11))
    ax = fig.add_axes([0.08, 0.05, 0.84, 0.9])
    ax.axis("off")
    ax.text(0, 1.0, "Analytics Questions 1–4", fontsize=16, fontweight="bold", va="top")

    # Q1
    y = 0.94
    ax.text(0, y, "Q1. Which taxi type had more trips?", fontsize=12, fontweight="bold", va="top")
    y -= 0.03
    yellow_n = r["q1"]["yellow"]; green_n = r["q1"]["green"]
    ax.text(0, y, f"Yellow had more trips: {yellow_n:,} vs. green {green_n:,} "
                  f"(yellow is ~{yellow_n/green_n:.0f}x larger).",
            fontsize=10, va="top")
    y -= 0.04
    tbl = ax.table(cellText=[["yellow", f"{yellow_n:,}"], ["green", f"{green_n:,}"]],
                   colLabels=["taxi_type", "trip count"],
                   bbox=[0, y - 0.10, 0.4, 0.10], cellLoc="left")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for (rr, cc), cell in tbl.get_celld().items():
        if rr == 0:
            cell.set_facecolor("#dddddd"); cell.set_text_props(weight="bold")
    y -= 0.13

    # Q2
    ax.text(0, y, "Q2. What hour of day had the most pickups?", fontsize=12, fontweight="bold", va="top")
    y -= 0.03
    top_h, top_n = r["q2_top"][0]
    ax.text(0, y, f"Hour {top_h:02d}:00 (6 PM) had the most pickups: {top_n:,}.",
            fontsize=10, va="top")
    y -= 0.04
    rows = [[f"{h:02d}:00", f"{c:,}"] for h, c in r["q2_top"]]
    tbl = ax.table(cellText=rows, colLabels=["pickup_hour", "trips"],
                   bbox=[0, y - 0.13, 0.4, 0.13], cellLoc="left")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for (rr, cc), cell in tbl.get_celld().items():
        if rr == 0:
            cell.set_facecolor("#dddddd"); cell.set_text_props(weight="bold")
    y -= 0.16

    # Q3
    ax.text(0, y, "Q3. What percentage of trips were under 2 miles?", fontsize=12, fontweight="bold", va="top")
    y -= 0.03
    ax.text(0, y,
            f"{r['q3_pct']:.2f}% of trips were under 2 miles "
            f"({r['q3_n']:,} of {r['q3_total']:,}).",
            fontsize=10, va="top")
    y -= 0.05

    # Q4
    ax.text(0, y, "Q4. Average trip distance by taxi type", fontsize=12, fontweight="bold", va="top")
    y -= 0.03
    ax.text(0, y, "Green trips are roughly twice as long on average as yellow trips, "
                  "consistent with green cabs serving outer-borough longer-haul rides.",
            fontsize=10, va="top", wrap=True)
    y -= 0.05
    rows = [[k, f"{v:.3f}"] for k, v in r["q4"].items()]
    tbl = ax.table(cellText=rows, colLabels=["taxi_type", "avg trip_distance (mi)"],
                   bbox=[0, y - 0.08, 0.45, 0.08], cellLoc="left")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for (rr, cc), cell in tbl.get_celld().items():
        if rr == 0:
            cell.set_facecolor("#dddddd"); cell.set_text_props(weight="bold")

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

    # Page 3: Q5
    add_coef_plot_page(pdf)

    # Page 4: predicted vs actual scatter
    import matplotlib.image as mpimg
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.08, 0.95, "Q5 — Predicted vs. Actual Fare", fontsize=16, fontweight="bold")
    ax_img = fig.add_axes([0.1, 0.30, 0.8, 0.6])
    ax_img.imshow(mpimg.imread("predicted_vs_actual.png"))
    ax_img.axis("off")
    caption = (
        "Scatter of predicted vs. actual fare on a 5% sample of the test set, with a red "
        "y = x reference line. Most predictions cluster between ~$10–$40 regardless of the "
        "actual fare, so the model systematically under-predicts long/expensive rides "
        "(actuals > ~$100 fall well below the y = x line). This is consistent with the "
        "diagnosis from the coefficients: trip_distance was deflated by multicollinearity "
        "with trip_duration_min, and the flat-rate / airport fare structure is not modelled, "
        "so the linear model cannot reach into the high-fare regime."
    )
    fig.text(0.08, 0.22, caption, fontsize=10, wrap=True, va="top", ha="left")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

print(f"wrote {out}")
