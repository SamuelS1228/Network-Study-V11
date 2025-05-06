import numpy as np
from sklearn.cluster import KMeans
from utils import transportation_cost, warehousing_cost

def assign_clusters(df, centers):
    df = df.copy()
    dists = np.linalg.norm(df[['Longitude','Latitude']].values[:,None,:] - centers[None,:,:], axis=2)
    df['Warehouse'] = dists.argmin(axis=1)
    df['DistMiles'] = dists.min(axis=1)
    return df

def evaluate_cost(df, centers, cost_per_lb_mile, sqft_per_lb, cost_per_sqft, fixed_cost):
    assigned = assign_clusters(df, centers)
    trans_cost = (assigned['DistMiles'] * assigned['DemandLbs'] * cost_per_lb_mile).sum()
    wh_cost = 0.0
    for idx in range(len(centers)):
        demand = assigned.loc[assigned['Warehouse']==idx,'DemandLbs'].sum()
        wh_cost += warehousing_cost(demand, sqft_per_lb, cost_per_sqft, fixed_cost)
    return trans_cost + wh_cost, trans_cost, wh_cost, assigned

def optimize(df, k_range, cost_per_lb_mile, sqft_per_lb, cost_per_sqft, fixed_cost, random_state=42):
    coords = df[['Longitude','Latitude']].values
    weights = df['DemandLbs'].values
    best=None
    for k in k_range:
        km = KMeans(n_clusters=k, n_init='auto', random_state=random_state)
        km.fit(coords, sample_weight=weights)
        total_cost, trans_cost, wh_cost, assigned = evaluate_cost(
            df, km.cluster_centers_, cost_per_lb_mile, sqft_per_lb, cost_per_sqft, fixed_cost)
        if best is None or total_cost < best['total_cost']:
            best = {
                'k': k,
                'total_cost': total_cost,
                'trans_cost': trans_cost,
                'wh_cost': wh_cost,
                'centers': km.cluster_centers_,
                'assigned_df': assigned
            }
    return best
