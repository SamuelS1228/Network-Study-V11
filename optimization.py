import numpy as np
from sklearn.cluster import KMeans
from utils import transportation_cost, warehousing_cost

def assign_clusters(df, centers):
    df = df.copy()
    dists = np.linalg.norm(df[['Longitude','Latitude']].values[:,None,:] - centers[None,:,:], axis=2)
    df['Warehouse'] = dists.argmin(axis=1)
    df['DistMiles'] = dists.min(axis=1)
    return df

def evaluate_cost(df, centers, rate, sqft_per_lb, cost_per_sqft, fixed_cost):
    assigned = assign_clusters(df, centers)
    trans_cost = (assigned['DistMiles'] * assigned['DemandLbs'] * rate).sum()
    wh_cost = 0.0
    demand_per_wh = []
    for i in range(len(centers)):
        demand = assigned.loc[assigned['Warehouse']==i,'DemandLbs'].sum()
        demand_per_wh.append(demand)
        wh_cost += warehousing_cost(demand, sqft_per_lb, cost_per_sqft, fixed_cost)
    total = trans_cost + wh_cost
    return total, trans_cost, wh_cost, assigned, demand_per_wh

def optimize(df, k_values, rate, sqft_per_lb, cost_per_sqft, fixed_cost, seed=42):
    coords = df[['Longitude','Latitude']].values
    weights = df['DemandLbs'].values
    best = None
    for k in k_values:
        km = KMeans(n_clusters=k, n_init='auto', random_state=seed)
        km.fit(coords, sample_weight=weights)
        total, trans, wh, assigned, demand_list = evaluate_cost(
            df, km.cluster_centers_, rate, sqft_per_lb, cost_per_sqft, fixed_cost)
        if best is None or total < best['total_cost']:
            best = {
                'k': k,
                'total_cost': total,
                'trans_cost': trans,
                'wh_cost': wh,
                'centers': km.cluster_centers_,
                'assigned_df': assigned,
                'demand_per_wh': demand_list
            }
    return best
