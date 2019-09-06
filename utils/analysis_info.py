import os
import glob

import click
import redis
import pandas as pd


@click.group()
def cli():
    # do nothing
    pass

BASE_DIR = "/Users/b250-admin/analysis"


localhost = "172.22.24.88" # local
remote_host = "172.22.54.5" # remote


def get_analysis_info(project_id, rdb):
    analysis_file = os.path.join(BASE_DIR, project_id, "{}.md".format(project_id))
    if os.path.isfile(analysis_file):
        print("File found: {}".format(analysis_file))
        with open(analysis_file, 'r') as fff:
            content = fff.read()
            rdb.set('{}_analysis_info'.format(project_id), content)
    else:
        print("File not found: {}".format(analysis_file))


@cli.command()
@click.argument('project_id', required=False)
@click.option('--remote/--local', default=False)
def analysis_info(project_id, remote):
    host = remote_host if remote else localhost
    rdb = redis.StrictRedis(host=host)
    if project_id is None:
        projects = os.listdir(BASE_DIR)
        for project in projects:
            get_analysis_info(project, rdb)
    else:
        get_analysis_info(project_id, rdb)


if __name__ == '__main__':
    cli()
