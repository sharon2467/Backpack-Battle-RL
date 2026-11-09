"""Source-based statistics; independent uniform draws, not Godot PRNG replay."""
from pathlib import Path
import hashlib
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261009


def range_step(acc, raw, low, high):
    """Translate BalancedRange.randIntRange, retaining the ORIGINAL dif."""
    dif = raw - 0.5 * (low + high)
    malus = np.where(acc >= 1, np.minimum(raw - low, acc.astype(np.int64)), 0)
    bonus = np.where(acc <= -1, np.minimum(high - raw, np.abs(acc).astype(np.int64)), 0)
    value = raw - malus + bonus
    return value, acc - malus + bonus + dif


def roll_step(expected, wins, last, target, uniform):
    """Keep expectedWins separately, matching the source addition order."""
    target = np.broadcast_to(target, expected.shape)
    active = (target > 0) & (target < 1)
    chance = target.copy()
    dif = expected - wins
    positive = active & (dif > 0.3)
    negative = active & (dif < -0.3)
    chance[positive] *= 3.0 * np.minimum(1.0, dif[positive])
    chance[negative] /= 3.0 * np.minimum(1.0, -dif[negative])
    new_expected = expected + np.where(active, target, 0)
    chance[last & (target < 0.4)] *= 0.5
    chance[~last & (target > 0.6)] *= 2.0
    result = (uniform <= chance) & active | (target >= 1)
    new_last = np.where(active, result, last)
    new_wins = wins + (result & active)
    return result, new_expected, new_wins, new_last


def roll_probability(expected, wins, last, target):
    if target <= 0:
        return 0.0
    if target >= 1:
        return 1.0
    chance = target
    dif = expected - wins
    if dif > 0.3:
        chance *= 3.0 * min(1.0, dif)
    elif dif < -0.3:
        chance /= 3.0 * min(1.0, -dif)
    if last and target < 0.4:
        chance *= 0.5
    elif not last and target > 0.6:
        chance *= 2.0
    return float(np.clip(chance, 0, 1))


def exact_roll_counts(target, steps, bias=0.0):
    if target <= 0 or target >= 1:
        counts = np.zeros(steps + 1)
        counts[steps if target >= 1 else 0] = 1
        return counts
    mass = {(0, False): 1.0}
    expected = bias
    for _ in range(steps):
        next_mass = {}
        for (wins, last), weight in mass.items():
            q = roll_probability(expected, wins, last, target)
            for key, probability in (((wins, False), 1 - q), ((wins + 1, True), q)):
                if probability > 0:
                    next_mass[key] = next_mass.get(key, 0.0) + weight * probability
        mass = next_mass
        expected += target
    counts = np.zeros(steps + 1)
    for (wins, _), weight in mass.items():
        counts[wins] += weight
    return counts


def range_stationary(width):
    # States are 2*acc integers, so reachability is exact even for odd widths.
    states = [0]
    transitions = {}
    for state in states:
        edges = []
        for raw in range(width + 1):
            value, acc = range_step(np.array([state / 2]), np.array([raw]), 0, width)
            next_state = int(2 * acc[0])
            edges.append((next_state, int(value[0])))
            if next_state not in states:
                states.append(next_state)
        transitions[state] = edges
    index = {state: i for i, state in enumerate(states)}
    matrix = np.zeros((len(states), len(states)))
    emissions = np.zeros((len(states), width + 1))
    for state, edges in transitions.items():
        for next_state, value in edges:
            matrix[index[state], index[next_state]] += 1 / (width + 1)
            emissions[index[state], value] += 1 / (width + 1)
    stationary = np.linalg.lstsq(
        np.vstack([matrix.T - np.eye(len(states)), np.ones(len(states))]),
        np.r_[np.zeros(len(states)), 1.0], rcond=None,
    )[0]
    pmf = stationary @ emissions
    values = np.arange(width + 1)
    mean = float(pmf @ values)
    variance = float(pmf @ (values - mean) ** 2)
    next_mean = emissions @ values
    product = 0.0
    for state, edges in transitions.items():
        for next_state, value in edges:
            product += stationary[index[state]] * value * next_mean[index[next_state]] / (width + 1)
    return {
        "width": width, "states": [s / 2 for s in states],
        "state_mass": stationary.tolist(), "pmf": pmf.tolist(), "mean": mean,
        "variance": variance, "iid_variance": width * (width + 2) / 12,
        "lag1": (product - mean**2) / variance if variance else None,
        "residual": float(np.max(np.abs(stationary @ matrix - stationary))),
    }


def summarize(samples):
    return {
        "mean": float(np.mean(samples)), "std": float(np.std(samples)),
        "sem": float(np.std(samples) / np.sqrt(len(samples))),
        "quantiles": np.quantile(samples, [0.01, 0.5, 0.99]).tolist(),
    }


def run_experiments(output):
    rng = np.random.default_rng(SEED)
    results = {"seed": SEED, "runtime": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
               "sources": {}, "range": [], "roll_long": [], "roll_reset": [], "mixed": []}
    for source in ["Utility/BalancedRandom.gd", "Utility/BalancedRange.gd", "Utility/Util.gd", "Core/Character.gd", "Items/Item.gd"]:
        results["sources"][source] = hashlib.sha256((ROOT / "Backpack Battles" / source).read_bytes()).hexdigest()
    results["range"] = [range_stationary(width) for width in range(11)]
    paths, steps, burn = 2048, 4096, 1024
    results["long_config"] = {"paths": paths, "steps_after_burn": steps, "burn": burn}
    for p in [0.01, 0.05, 0.1, 0.25, 0.39, 0.4, 0.5, 0.6, 0.61, 0.75, 0.9, 0.95, 0.99]:
        expected = np.zeros(paths)
        wins = np.zeros(paths, dtype=np.int64)
        last = np.zeros(paths, dtype=bool)
        counts = np.zeros(paths, dtype=np.int64)
        pair_sum = 0
        left_sum = right_sum = 0
        for t in range(burn + steps):
            previous = last
            result, expected, wins, last = roll_step(expected, wins, last, p, rng.random(paths))
            if t >= burn:
                counts += result
                if t > burn:
                    pair_sum += np.count_nonzero(previous & result)
                    left_sum += np.count_nonzero(previous)
                    right_sum += np.count_nonzero(result)
        sample_count = (steps - 1) * paths
        mean = counts.mean() / steps
        covariance = pair_sum / sample_count - left_sum * right_sum / sample_count**2
        results["roll_long"].append({
            "p": p, "rate": summarize(counts / steps),
            "lag1": float(covariance / (mean * (1 - mean))),
            "block_count_std": float(counts.std()), "iid_count_std": float(np.sqrt(steps * p * (1 - p))),
            "terminal_deficit": summarize(expected - wins),
        })
    for p in [0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]:
        for n in [1, 2, 4, 8, 16, 32, 128]:
            for bias in [-0.2, 0.0, 0.2]:
                pmf = exact_roll_counts(p, n, bias)
                values = np.arange(n + 1)
                mean = float(pmf @ values)
                results["roll_reset"].append({
                    "p": p, "n": n, "bias": bias, "mean_count": mean, "rate": mean / n,
                    "count_std": float(np.sqrt(pmf @ (values - mean)**2)), "pmf": pmf.tolist(),
                })
    # Two targets share ONE stream; inspect each target group as well as the total.
    for schedule in [[0.1, 0.9], [0.25, 0.75], [0.01, 0.5]]:
        expected = np.zeros(paths)
        wins = np.zeros(paths, dtype=np.int64)
        last = np.zeros(paths, dtype=bool)
        grouped = np.zeros((2, paths))
        for t in range(burn + steps):
            group = t % 2
            result, expected, wins, last = roll_step(expected, wins, last, schedule[group], rng.random(paths))
            if t >= burn:
                grouped[group] += result
        results["mixed"].append({"schedule": schedule, "rates": [summarize(c / (steps / 2)) for c in grouped],
                                 "total_rate": float(grouped.sum() / (paths * steps))})
    # A large ensemble verifies finite-state range results and captures fresh 32-draw blocks.
    paths_range = 65536
    acc = np.zeros(paths_range)
    histogram = np.zeros(5, dtype=np.int64)
    for t in range(256):
        raw = rng.integers(0, 5, paths_range)
        value, acc = range_step(acc, raw, 0, 4)
        if t >= 128:
            histogram += np.bincount(value, minlength=5)
    results["range_empirical_width4"] = (histogram / histogram.sum()).tolist()
    acc = np.zeros(paths_range)
    balanced_total = np.zeros(paths_range)
    iid_total = np.zeros(paths_range)
    max_identity_error = 0.0
    for _ in range(32):
        raw = rng.integers(0, 5, paths_range)
        value, acc = range_step(acc, raw, 0, 4)
        balanced_total += value
        iid_total += raw
        max_identity_error = max(max_identity_error, float(np.max(np.abs(acc - (balanced_total - (_ + 1) * 2)))))
    results["range_block32_width4"] = {"paths": paths_range, "balanced": summarize(balanced_total / 32),
                                        "iid": summarize(iid_total / 32), "identity_error": max_identity_error}
    np.savez_compressed(output / "samples.npz", range_mean_balanced=balanced_total / 32, range_mean_iid=iid_total / 32)
    return results


def plot_results(results, output):
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5))
    color, iid_color = "#167e80", "#c47730"
    ax = axes[0, 0]
    positions = np.arange(5)
    ax.bar(positions - 0.18, results["range"][4]["pmf"], width=.36, color=color, label="Balanced stationary")
    ax.bar(positions + 0.18, np.ones(5) / 5, width=.36, color=iid_color, label="IID uniform")
    ax.set(title="A  Single range draw: [0, 4]", xlabel="Value", ylabel="Probability", xticks=positions)
    ax.legend(fontsize=9)
    ax = axes[0, 1]
    samples = np.load(output / "samples.npz")
    bins = np.arange(.95, 3.06, 1 / 32) - 1 / 64
    ax.hist(samples["range_mean_iid"], bins=bins, density=True, color=iid_color, alpha=.6, label="IID")
    ax.hist(samples["range_mean_balanced"], bins=bins, density=True, color=color, alpha=.8, label="Balanced")
    ax.set(title="B  Mean of 32 range draws", xlabel="Block mean", ylabel="Density")
    ax.legend(fontsize=9)
    ax = axes[0, 2]
    row = next(r for r in results["roll_reset"] if r["p"] == .25 and r["n"] == 32 and r["bias"] == 0)
    positions = np.arange(33)
    ax.bar(positions - .18, row["pmf"], width=.36, color=color, label="Balanced (exact)")
    ax.bar(positions + .18, binom.pmf(positions, 32, .25), width=.36, color=iid_color, label="Binomial IID")
    ax.set(title="C  Success count: p=0.25, n=32", xlabel="Successes", ylabel="Probability", xlim=(-.5, 18.5))
    ax.legend(fontsize=9)
    ax = axes[1, 0]
    for p, line_color in [(.25, "#167e80"), (.5, "#8363a1"), (.75, "#c47730")]:
        rows = [r for r in results["roll_reset"] if r["p"] == p and r["bias"] == 0]
        ax.plot([r["n"] for r in rows], [r["rate"] for r in rows], "o-", color=line_color, label=f"p={p:g}")
        ax.axhline(p, color=line_color, ls="--", alpha=.55)
    ax.set(title="D  Fresh reset: expected success rate", xlabel="Number of calls (log scale)", ylabel="E[successes] / n", xscale="log")
    ax.legend(fontsize=9)
    ax = axes[1, 1]
    rows = results["roll_long"]
    ax.plot([r["p"] for r in rows], [r["lag1"] for r in rows], "o-", color=color)
    ax.axhline(0, color=iid_color, ls="--", label="IID")
    ax.set(title="E  Success/failure serial dependence", xlabel="Fixed target p", ylabel="Lag-1 correlation")
    ax.legend(fontsize=9)
    ax = axes[1, 2]
    row = results["mixed"][0]
    positions = np.arange(2)
    ax.bar(positions - .18, [r["mean"] for r in row["rates"]], width=.36, color=color, label="Balanced group rate")
    ax.bar(positions + .18, row["schedule"], width=.36, color=iid_color, label="Nominal / IID")
    ax.set(title="F  Alternating targets, shared state", xlabel="Target group", ylabel="Success rate", xticks=positions, xticklabels=["p=0.1", "p=0.9"], ylim=(0, 1))
    ax.legend(fontsize=9)
    fig.suptitle("Balanced randomness: marginal shapes, cumulative concentration, and reset/shared-state effects", fontsize=15)
    fig.tight_layout(rect=(0, 0, 1, .96))
    fig.savefig(output / "balanced_rng_comparison.png", dpi=160)
    fig.savefig(output / "balanced_rng_comparison.pdf")
    plt.close(fig)


def main():
    output = ROOT / "data" / "balanced_rng_analysis"
    output.mkdir(parents=True, exist_ok=True)
    results = run_experiments(output)
    (output / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    plot_results(results, output)
    print("range [0,4]:", results["range"][4])
    print("range mean32:", results["range_block32_width4"])
    for row in results["roll_long"]:
        print("long", row["p"], row["rate"], "lag1", row["lag1"], "std", row["block_count_std"])
    for row in results["mixed"]:
        print("mixed", row)
    print("OUTPUT", output)


if __name__ == "__main__":
    main()
