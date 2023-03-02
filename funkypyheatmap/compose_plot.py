import matplotlib.pyplot as plt
import numpy as np

from funkypyheatmap.add_column_if_missing import add_column_if_missing
from matplotlib import collections as mc
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch


def compose_plot(positions, expand):
    fig, ax = plt.subplots()

    # Plot row backgrounds
    df = positions["row_pos"]
    df = df[df["color_background"]]

    if df.shape[0] > 0:
        for _, row in df.iterrows():
            rect = Rectangle(
                xy=(
                    np.min(positions["column_pos"]["xmin"]) - 0.25,
                    row["ymin"] - (positions["viz_params"] / 2),
                ),
                width=np.max(positions["column_pos"]["xmax"]) + 0.25,
                height=row["height"],
                color="#DDDDDD",
                zorder=0,
            )
            ax.add_patch(rect)

    # Plot segments
    if positions["segment_data"].shape[0] > 0:
        df = add_column_if_missing(
            positions["segment_data"], size=0.5, colour="black", linestyle="solid"
        )
        lines = [
            [(row["x"], row["y"]), (row["xend"], row["yend"])]
            for _, row in df.iterrows()
        ]
        lc = mc.LineCollection(
            lines, linewidths=df["size"], colors=df["colour"], linestyle=df["linestyle"]
        )
        lc.set_zorder(1)
        ax.add_collection(lc)

    # Plot rectangles
    if positions["rect_data"].shape[0] > 0:
        df = add_column_if_missing(
            positions["rect_data"], border_colour="black", border=True, alpha=1
        )
        df = df.assign(
            border_colour=[
                val if df["border"].iloc[i] else np.nan
                for i, val in enumerate(df["border_colour"])
            ]
        )
        for _, row in df.iterrows():
            rect = Rectangle(
                xy=(row["xmin"], row["ymin"]),
                width=row["xmax"] - row["xmin"],
                height=row["ymax"] - row["ymin"],
                fc=row["colour"],
                ec=row["border_colour"],
                alpha=row["alpha"],
                lw=0.5,
                zorder=2,
            )
            ax.add_patch(rect)

    # Plot circles
    if positions["circle_data"].shape[0] > 0:
        for _, row in positions["circle_data"].iterrows():
            circle = Circle(
                xy=(row["x"], row["y"]),
                radius=row["r"],
                ec="black",
                lw=0.5,
                fc=row["colour"],
                zorder=2,
            )
            ax.add_patch(circle)

    # Plot funky rectangles
    if positions["funkyrect_data"].shape[0] > 0:
        for _, row in positions["funkyrect_data"].iterrows():
            funkyrect = FancyBboxPatch(
                (row["x"] - row["w"] / 2, row["y"] - row["h"] / 2),
                row["w"],
                row["h"],
                boxstyle=f"round, pad = 0, rounding_size={row['corner_size']}",
                fc=row["colour"],
                ec="black",
                lw=0.5,
                zorder=2,
            )
            ax.add_patch(funkyrect)

    # Plot pies
    if positions["pie_data"].shape[0] > 0:
        pass

    if positions["text_data"].shape[0] > 0:
        df = add_column_if_missing(
            positions["text_data"],
            ha=0.5,
            va=0.5,
            size=7,
            fontweight="normal",
            colour="black",
            linespacing=1,
            angle=0,
            zorder=3,
        )
        df = df.assign(angle2=np.multiply(np.divide(df["angle"], 360), 2 * np.pi))
        df = df.assign(
            cosa=np.round(np.cos(df["angle2"]), 2),
            sina=np.round(np.sin(df["angle2"]), 2),
        )
        df = df.assign(
            alphax=np.add(
                (
                    np.multiply(
                        (
                            [
                                1 - df["ha"].iloc[i] if c < 0 else df["ha"].iloc[i]
                                for i, c in enumerate(df["cosa"])
                            ]
                        ),
                        np.abs(df["cosa"]),
                    )
                ),
                (
                    np.multiply(
                        (
                            [
                                np.subtract(1, df["va"].iloc[i])
                                if s > 0
                                else df["va"].iloc[i]
                                for i, s in enumerate(df["sina"])
                            ]
                        ),
                        np.abs(df["sina"]),
                    )
                ),
            ),
            alphay=np.add(
                (
                    np.multiply(
                        (
                            [
                                np.subtract(1, df["ha"].iloc[i])
                                if s < 0
                                else df["ha"].iloc[i]
                                for i, s in enumerate(df["sina"])
                            ]
                        ),
                        np.abs(df["sina"]),
                    )
                ),
                (
                    np.multiply(
                        (
                            [
                                np.subtract(1, df["va"].iloc[i])
                                if c < 0
                                else df["va"].iloc[i]
                                for i, c in enumerate(df["cosa"])
                            ]
                        ),
                        np.abs(df["cosa"]),
                    )
                ),
            ),
        )
        df = df.assign(
            x=np.add(
                np.multiply((np.subtract(1, df["alphax"])), df["xmin"]),
                np.multiply(df["alphax"], df["xmax"]),
            ),
            y=np.add(
                np.multiply((np.subtract(1, df["alphay"])), df["ymin"]),
                np.multiply(df["alphay"], df["ymax"]),
            ),
        )

        df = df[df["label_value"] != ""]
        for _, row in df.iterrows():
            if row["ha"] == 0.5:
                ha = "center"
            elif row["ha"] == 0:
                ha = "left"
            else:
                ha = "right"
            if row["va"] == 0.5:
                va = "center"
            elif row["va"] == 0:
                va = "bottom"
            else:
                va = "top"
            ax.text(
                x=row["x"],
                y=row["y"],
                s=row["label_value"],
                size=row["size"],
                color=row["colour"],
                rotation=row["angle"],
                fontweight=row["fontweight"],
                linespacing=row["linespacing"],
                ha=ha,
                va=va,
            )

    ax.axis("equal")
    plt.axis("off")
    plt.show()