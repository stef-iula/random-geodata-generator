import geopandas as gpd
import numpy as np
import pandas as pd
import argparse
from randomtimestamp import randomtimestamp


def plot(w, pts):
    base = w.plot(color='white', edgecolor='black')
    points_df = gpd.GeoDataFrame(pts, geometry=gpd.points_from_xy(pts.longitude, pts.latitude))
    points_df.plot(ax=base, marker='o', color='red', markersize=5)


def make_random_points_in_region(region_df):
    x_min, y_min, x_max, y_max = region_df.total_bounds

    x = np.random.uniform(x_min, x_max, n)
    y = np.random.uniform(y_min, y_max, n)

    points = gpd.GeoSeries(gpd.points_from_xy(x, y))
    points = gpd.GeoDataFrame(points)
    points = points.rename(columns={0: 'geometry'}).set_geometry('geometry')
    points = pd.DataFrame(points)

    good_points = pd.DataFrame(columns=['longitude', 'latitude'])
    for i, r in region_df.iterrows():
        for p in points.geometry:
            if r.geometry.contains(p):
                good_points = good_points.append({'longitude': p.x, 'latitude': p.y}, ignore_index=True)

    return good_points


def add_random_info(d):
    d['timestamp'] = d.apply(lambda x: randomtimestamp(start_year=2015, text=False), axis=1)
    return d.sort_values(by='timestamp').reset_index(drop=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-np", "--n_points", help="number of points randomly generated", default=1000)
    parser.add_argument("-c", "--countries", nargs='*', help="list selected country ISO_A2", default=['IT'])
    parser.add_argument("-o", "--output_file", help="output file path", default="./data.csv")
    parser.add_argument("-i", "--input_file", help="input file path", default="./src/geometries/world.geojson")

    args = parser.parse_args()

    n = int(args.n_points)

    output_file = args.output_file
    selected_countries = args.countries
    input_file = args.input_file

    try:
        print('Getting world geometry from ', input_file)
        world = gpd.read_file(input_file)
        is_selected = world.iso_a2.isin(selected_countries)
        not_valid_states = np.setdiff1d(selected_countries, world.iso_a2.unique())

        if len(not_valid_states) == len(selected_countries):
            print('States must be in ', world.iso_a2.unique())
            raise Exception('No valid states')

        if len(not_valid_states) > 0:
            print('These states are not valid: ', not_valid_states)

        df = world[is_selected]

        print('Generating for ', df.admin.unique())
        random_points = make_random_points_in_region(df)

        random_data = add_random_info(random_points)
        random_data.to_csv(output_file, sep='|', index=False)
        print('file written at', output_file)
    except Exception as error:
        print('error: ', error)
        raise Exception(error)




