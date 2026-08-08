"""
Optimization 1: EV Charging Hub Location Selection
---------------------------------------------------

Prototype formulation:
- Candidate locations are generated from existing station coordinates using
  spherical K-means clustering.
- Each cluster is represented by the nearest real charging station, ensuring
  proposed hubs are located at realistic observed locations.
- A Mixed-Integer Programming (MIP) maximum-coverage model selects K hubs.
- A station is considered geographically covered if it is within a user-defined
  radius of at least one selected hub.

This is the first prototype. The final UI can expose:
    - country/region filter
    - number of hubs K
    - coverage radius R
    - optional sparsity weighting

The model intentionally does NOT assume EV traffic, population, demand,
revenue, or electricity consumption because those variables are absent from
the dataset.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix, csr_matrix


EARTH_RADIUS_KM = 6371.0


def haversine_matrix(points_a, points_b):
    """Return pairwise great-circle distances in km."""
    a = np.radians(np.asarray(points_a, dtype=float))
    b = np.radians(np.asarray(points_b, dtype=float))

    lat1 = a[:, 0][:, None]
    lon1 = a[:, 1][:, None]
    lat2 = b[:, 0][None, :]
    lon2 = b[:, 1][None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    return EARTH_RADIUS_KM * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))


def generate_candidate_hubs(df, n_candidates=100, random_state=42):
    """
    Generate candidate hub locations from observed stations.

    K-means is performed on 3D unit-sphere coordinates to avoid treating
    latitude/longitude as ordinary Cartesian coordinates. Each cluster is
    represented by the observed station nearest to its cluster centroid.
    """
    geo = df.dropna(subset=["lat", "lon"]).copy()

    if len(geo) < n_candidates:
        n_candidates = len(geo)

    lat = np.radians(geo["lat"].to_numpy())
    lon = np.radians(geo["lon"].to_numpy())

    X = np.column_stack([
        np.cos(lat) * np.cos(lon),
        np.cos(lat) * np.sin(lon),
        np.sin(lat),
    ])

    model = KMeans(
        n_clusters=n_candidates,
        random_state=random_state,
        n_init=10,
    )
    labels = model.fit_predict(X)

    centers = model.cluster_centers_
    centers /= np.linalg.norm(centers, axis=1, keepdims=True)

    candidate_indices = []

    for cluster_id in range(n_candidates):
        members = np.where(labels == cluster_id)[0]
        if len(members) == 0:
            continue

        distances = np.sum(
            (X[members] - centers[cluster_id]) ** 2,
            axis=1,
        )

        candidate_indices.append(
            geo.index[members[np.argmin(distances)]]
        )

    candidates = (
        df.loc[candidate_indices]
        .drop_duplicates(subset=["id"])
        .reset_index(drop=True)
    )

    return candidates


def solve_max_coverage(
    df,
    candidates,
    n_hubs=10,
    radius_km=50,
    time_limit=120,
):
    """
    Solve the binary maximum-coverage MIP.

    Decision variables:
        y_j = 1 if candidate hub j is selected
        z_i = 1 if station i is covered

    Objective:
        maximize total number of covered stations

    Constraints:
        sum(y_j) <= n_hubs
        z_i <= sum(y_j for candidate j within radius of station i)
        y_j, z_i are binary
    """
    station_data = df.dropna(subset=["lat", "lon"]).copy()
    station_coords = station_data[["lat", "lon"]].to_numpy()
    candidate_coords = candidates[["lat", "lon"]].to_numpy()

    distances = haversine_matrix(station_coords, candidate_coords)
    neighbors = [np.flatnonzero(row <= radius_km) for row in distances]

    covered_rows = [
        i for i, candidate_neighbors in enumerate(neighbors)
        if len(candidate_neighbors) > 0
    ]

    n_candidates = len(candidates)
    n_covered_rows = len(covered_rows)
    n_variables = n_candidates + n_covered_rows

    # First n_candidates variables = y_j
    # Remaining variables = z_i for stations that have at least one candidate
    A = lil_matrix(
        (n_covered_rows + 1, n_variables),
        dtype=float,
    )

    lower = np.full(n_covered_rows + 1, -np.inf)
    upper = np.full(n_covered_rows + 1, np.inf)

    for row, station_idx in enumerate(covered_rows):
        A[row, n_candidates + row] = 1
        A[row, neighbors[station_idx]] = -1
        upper[row] = 0

    # At most K hubs
    A[n_covered_rows, :n_candidates] = 1
    upper[n_covered_rows] = n_hubs

    objective = np.zeros(n_variables)
    objective[n_candidates:] = -1  # maximize coverage via minimization

    result = milp(
        c=objective,
        integrality=np.ones(n_variables),
        bounds=Bounds(
            np.zeros(n_variables),
            np.ones(n_variables),
        ),
        constraints=LinearConstraint(
            csr_matrix(A),
            lower,
            upper,
        ),
        options={"time_limit": time_limit},
    )

    if not result.success:
        raise RuntimeError(result.message)

    selected_indices = np.flatnonzero(result.x[:n_candidates] > 0.5)
    selected_hubs = candidates.iloc[selected_indices].copy()

    coverage = int(round(-result.fun))

    # Coverage at the station level
    station_covered = np.zeros(len(station_data), dtype=bool)
    for station_idx in covered_rows:
        if np.any(result.x[neighbors[station_idx]] > 0.5):
            station_covered[station_idx] = True

    coverage_rate = station_covered.mean()

    return {
        "selected_hubs": selected_hubs,
        "covered_stations": station_covered.sum(),
        "coverage_rate": coverage_rate,
        "n_hubs": len(selected_hubs),
        "radius_km": radius_km,
        "solver_result": result,
    }


if __name__ == "__main__":
    import os
    DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ev_stations_2025.csv")

    df = pd.read_csv(DATA_PATH)

    candidates = generate_candidate_hubs(
        df,
        n_candidates=100,
    )

    result = solve_max_coverage(
        df,
        candidates,
        n_hubs=10,
        radius_km=50,
    )

    print("\n=== Optimization 1: Maximum Coverage MIP ===")
    print(f"Stations: {len(df):,}")
    print(f"Candidate hubs: {len(candidates)}")
    print(f"Hubs selected: {result['n_hubs']}")
    print(f"Coverage radius: {result['radius_km']} km")
    print(f"Covered stations: {result['covered_stations']:,}")
    print(f"Coverage rate: {result['coverage_rate']:.2%}")

    print("\nSelected candidate hubs:")
    print(
        result["selected_hubs"][
            ["id", "title", "lat", "lon", "state", "country"]
        ].to_string(index=False)
    )
