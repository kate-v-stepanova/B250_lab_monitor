import os

import click
import redis

# this script is to be run on the cluster!

@click.group()
def cli():
    # do nothing
    pass

@cli.command()
@click.option('--host', default="localhost") #default="172.22.54.5")
@click.option('--port', default='6379')
def check_projects(host, port):
    BASE_DIR="/icgc/dkfzlsdf/analysis/OE0532/"
    projects = []
    for project in os.path.listdir(BASE_DIR):
        analysis_path = os.path.join(BASE_DIR, project, "analysis/output")
        if os.path.isdir(analysis_path):
            # if analysis dir exists
            projects.append(project)
            # demultiplexed
            # umi extracted
            # clean (without rRNA and tRNA)
            # tophat_out
            # alignments (with star)
            # rpf_5p_density
            # subsequence_data
            # rrna_fragments
            # trna_fragments
            # gen_tracks
            # bc_split_stats, cutadapt_plot_stats, diricore_stats
            # figures
    print(projects)
    rdb = redis.StrictRedis(host=host, port=port)
    rdb_projects = rdb.smembers('projects')
    rdb_projects = [p.decode('utf-8') for p in rdb_projects]
    print(rdb_projects)
    for project in projects:
        if project not in rdb_projects:
            print(project)




if __name__ == '__main__':
    cli()