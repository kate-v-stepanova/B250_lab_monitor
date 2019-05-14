import os
import glob

import click
import pymongo
import redis
import pandas as pd

# from main import app

@click.group()
def cli():
    # do nothing
    pass

BASE_DIR = "/Users/b250-admin/analysis/"
rrna_positions_dir = "rrna_positions"

@cli.command()
@click.argument('project_id')
def reads_per_position(project_id):
    """
    Reads the data from *_reads_per_position.txt files,
    aggregates all samples into one DataFrame,
    converts it to pandas binary string and saves to Redis.
    This will update an existing record, or create a new one if does not exist.
    """
    # default host: 127.0.0.1, default port: 6379.
    # to change, use redis.StrictRedis(host=HOST, port=PORT)
    # but we are not going to change this

    # mongo_client = pymongo.MongoClient()
    # projects = mongo_client.projects

    rdb = redis.StrictRedis()
    projects = rdb.smembers('projects')

    if project_id not in projects:
        rdb.sadd('projects', project_id)

    path = os.path.join(BASE_DIR, project_id, rrna_positions_dir, '*_reads_per_position.txt')
    input_files = glob.glob(path)
    if not input_files:
        print("No input files found: {}".format(path))
        exit(0)
    full_df = None
    for input_file in input_files:
        df = pd.read_csv(input_file, sep='\t')
        filename = os.path.basename(input_file)
        plot_name = filename.replace('_reads_per_position.txt', '')
        sample_name, gene_name = plot_name.rsplit('_', 1)
        df['sample'] = sample_name
        df['gene'] = gene_name
        if full_df is None:
            full_df = df
        else:
            full_df = full_df.append(df, ignore_index=True)
    key = "{}_reads_per_position".format(project_id)

    # save a binary string
    rdb.set(key, full_df.to_msgpack())


if __name__ == '__main__':
    cli()
