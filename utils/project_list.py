import os
import json
import click
import redis
import pandas as pd
import glob

BASE_DIR="/icgc/dkfzlsdf/analysis/OE0532/"
localhost="172.22.24.88" # local
remote_host="172.22.54.5" # remote
port = "6379"
host = localhost

# this script is to be run on the cluster!

@click.group()
def cli():
    # do nothing
    pass

@cli.command()
@click.option('--remote/--local', default=False)
def check_projects(remote):
    projects = []
    for project in os.listdir(BASE_DIR):
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
    if remote:
        rdb = redis.StrictRedis(host=remote_host)
    else:
        rdb = redis.StrictRedis(host=localhost)
    rdb_projects = rdb.smembers('projects')
    rdb_projects = [p.decode('utf-8') for p in rdb_projects]
    for project in projects:
        if project not in rdb_projects:
            rdb.sadd('projects', project)
            print(project)


def check_bc_stats(project, host):
        bc_file = os.path.join(BASE_DIR, project, "analysis/output/bc_split_stats.txt")
        if os.path.exists(bc_file):
            rdb = redis.StrictRedis(host=host)
            df = pd.read_csv(bc_file, sep="\t")
            rdb.set("bc_split_{}".format(project), df.to_msgpack())
            df = df[['Barcode', 'Count']]
            df.columns = ['sample', 'reads']
            df = df.loc[df['sample'] != 'total']
            df = df.loc[df['sample'] != 'unmatched']
            df['reads'] = df['reads'].apply(lambda x: x/1000000).round(decimals=2) # to get milion reads
            rdb.set("sample_info_{}".format(project), json.dumps(df.to_dict('recods')))


@cli.command()
@click.option("--remote/--local", default=False)
@click.argument('project')
def bc_stats(project, remote):
    if remote:
        host = remote_host
    else:
        host = localhost
    check_bc_stats(project, host)

def check_cutadapt_stats(project, host):
        cutadapt_file = os.path.join(BASE_DIR, project, "analysis/output/cutadapt_plot_stats.txt")
        if os.path.exists(cutadapt_file):
            rdb = redis.StrictRedis(host=host)
            df = pd.read_csv(cutadapt_file, sep="\t", header=None)
            print(df)
            df = df.transpose()
            print(df)
            df.columns = df.iloc[0]
            print(df.columns)
            #df.columns = [col.strip() for col in df.columns]
            print(df.columns)
            df = df.rename({"Total reads:": "total", "With adapters:": "with_adapter", "Too short:": "too_short", "Passed filters:": "passed"}, axis='columns')
#            print(df)
            
            #df = df.loc[1]
#            df = df.loc[df['total'] != "Total reads:"]
            #import pdb; pdb.set_trace()
#            print(df)
            #df.columns = ['total', 'with_adapter', 'too_short', 'passed']
            rdb.set('cutadapt_stats_{}'.format(project), json.dumps(df.to_dict('records')))

@cli.command()
@click.option("--remote--local", default=False)
@click.argument('project')
def cutadapt_stats(project, remote):
    if remote:
        host = remote_host
    else:
        host = localhost
    check_cutadapt_stats(project, host)

def check_transcript_regions(project, host):
    print("Transcript regions")
    input_file = os.path.join(BASE_DIR, project, "analysis/output/transcript_regions/reads_per_region.tsv".format(project))
    print(input_file)
    if os.path.exists(input_file):
        rdb = redis.StrictRedis(host=host)
        df = pd.read_csv(input_file, sep="\t", header=0)
#        rdb.set('transcript_regions_{}'.format(project), df.to_msgpack())
        rdb.set('transcript_regions_{}'.format(project), json.dumps(df.to_dict('records')))

@cli.command()
@click.option('--remote/--local', default=False)
@click.argument('project')
def transcript_regions(project, remote):
    if remote:
        host = remote_host
    check_transcript_regions(project, host)

def check_diricore_stats(project, host):
    print("Diricore stats")
    input_file = os.path.join(BASE_DIR, project, "analysis/output/alignment_stats/diricore_stats.txt")
    if os.path.exists(input_file):
        rdb = redis.StrictRedis(host=host)
        df = pd.read_csv(input_file, sep="\t", header=0)
        rdb.set('diricore_stats_{}'.format(project), json.dumps(df.to_dict('records')))


@cli.command()
@click.option('--remote/--local', default=False)
@click.argument('project')
def diricore_stats(project, remote):
    host = remote_host if remote else localhost
    check_diricore_stats(project, host)

def check_ucsc(project, host=localhost):
    project_dir = os.path.join(BASE_DIR, project)
    ucsc_dir = os.path.join(project_dir, "analysis/output/gen_tracks")
    if os.path.isdir(ucsc_dir):
        ucsc_annotation = os.path.join(ucsc_dir, "ucsc_track_annotation.txt")
        if os.path.isfile(ucsc_annotation):
            print("File exists: {}. Updating redis".format(ucsc_annotation))
            ucsc_link = "http://genome.ucsc.edu/s/stephz/{}".format(project)
            rdb = redis.StrictRedis(host=host)
            rdb.set("ucsc_link_{}".format(project), ucsc_link)


@cli.command()
@click.option("--remote/--local", default=False)
@click.argument('project')
def ucsc(project, remote):
    host = remote_host if remote == True else localhost
    check_ucsc(project, host)


def check_ma_plot(project, host):
    rdb = redis.StrictRedis(host=host)
    ma_files = os.path.join(BASE_DIR, project, "analysis/output/ma_plot/ma_plot_all*.tsv")
    for ma_file in glob.glob(ma_files):
        df = pd.read_csv(ma_file, sep="\t")
        contrast = os.path.basename(ma_file).replace('ma_plot_all_', '').replace('.tsv', '')
#        df1['contrast'] = contrast
        rdb.sadd('contrasts_{}'.format(project), contrast)
        print(contrast)
        rdb.set('ma_plot_all_{}_{}'.format(project, contrast), df.to_msgpack())
    ma_files = os.path.join(BASE_DIR, project, "analysis/output/ma_plot/ma_plot_coding*.tsv")
    for ma_file in glob.glob(ma_files):
        df = pd.read_csv(ma_file, sep="\t")
        contrast = os.path.basename(ma_file).replace('ma_plot_coding_', '').replace('.tsv', '')
#        df1['contrast'] = contrast
        rdb.sadd('contrasts_{}'.format(project), contrast)
        print(contrast)
        rdb.set('ma_plot_coding_{}_{}'.format(project, contrast), df.to_msgpack())
    
    #print(df)

@cli.command()
@click.option("--remote/--local", default=False)
@click.argument("project")
def ma_plot(project, remote):
    host = remote_host if remote else localhost
    check_ma_plot(project, host)

def check_fold_change(project, host):
#/icgc/dkfzlsdf/analysis/OE0532/14592/analysis/output/rna_seq/fc_data_for_contrasts.tsv
    fc_path = os.path.join(BASE_DIR, project, "analysis/output/fold_change/FC_all_genes.tsv")
    if os.path.isfile(fc_path):
        rdb = redis.StrictRedis(host=host)
        df = pd.read_csv(fc_path, sep="\t")
        rdb.set("fc_all_{}".format(project), df.to_msgpack())
    fc_path = os.path.join(BASE_DIR, project, "analysis/output/fold_change/FC_coding_genes.tsv")
    if os.path.isfile(fc_path):
        rdb = redis.StrictRedis(host=host)
        df = pd.read_csv(fc_path, sep="\t")
        rdb.set("fc_coding_{}".format(project), df.to_msgpack())

@cli.command()
@click.option("--remote/--local", default=False)
@click.argument("project")
def fold_change(project, remote):
    host = remote_host if remote else localhost
    check_fold_change(project, host)


def check_reads_per_position(project_id, host):
    rdb = redis.StrictRedis(host)

    rdb.sadd('projects', project_id)

    rrna_positions_dir = "analysis/output/rrna_positions"
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
    print("Saving key to redis: {}".format(key))
    rdb.set(key, full_df.to_msgpack())

@cli.command()
@click.argument('project_id')
@click.option('--remote/--local', default=False)
def reads_per_position(project_id, remote):
    """
    Reads the data from *_reads_per_position.txt files,
    aggregates all samples into one DataFrame,
    converts it to pandas binary string and saves to Redis.
    This will update an existing record, or create a new one if does not exist.
    """
    # default host: 127.0.0.1, default port: 6379.
    # to change, use redis.StrictRedis(host=HOST, port=PORT)
    # but we are not going to change this

    if remote:
        host="172.22.54.5"
    else:
        host = "localhost"
    check_reads_per_position(project_id, host)


def check_periodicity(project_id, host):
    rdb = redis.StrictRedis(host)
    rdb.sadd('projects', project_id)
    path = os.path.join(BASE_DIR, project_id, 'analysis/output/periodicity/*.heatmap.tsv')
    input_files = glob.glob(path)
    if not input_files:
        print("No input files found: {}".format(path))
        exit(0)
    full_df = None
    for input_file in input_files:
        df = pd.read_csv(input_file, sep='\t')
        samplename = os.path.basename(input_file).replace('.heatmap.tsv', '').replace('.', '_')
        df['sample'] = samplename
        if full_df is None:
            full_df = df
        else:
            full_df = full_df.append(df, ignore_index=True)
    key = "{}_periodicity_heatmap".format(project_id)

    if rdb.exists(key):
        rdb.delete(key)
    rdb.set(key, full_df.to_msgpack())

@cli.command()
@click.argument('project_id')
@click.option('--remote/--local', default=False)
def periodicity(project_id, remote):
    if remote:
        host = "172.22.54.5"
    else:
        host = "172.22.24.88"
    check_periodicity(project_id, host)


@cli.command()
@click.argument('project_id')
def copy_periodicity(project_id):
    remote = redis.StrictRedis('172.22.54.5')
    local = redis.StrictRedis('172.22.24.88')
    import pdb; pdb.set_trace()
    key = "{}_periodicity_heatmap".format(project_id)
    dt = pd.read_msgpack(remote.get(key))
    local.set(key, pd.to_msgpack(dt))

 
def get_all_stats(project, host=localhost):
    print("Getting all stats for {}".format(project))
    project_dir = os.path.join(BASE_DIR, project)
    analysis_dir = os.path.join(project_dir, "analysis/output")
    rdb = redis.StrictRedis(host=host)
    if os.path.isdir(analysis_dir):
        rdb.sadd("projects", project)
        check_cutadapt_stats(project, host)
        check_bc_stats(project, host)
        check_transcript_regions(project, host)
        check_diricore_stats(project, host)
        check_ma_plot(project, host)
        check_ucsc(project, host)
        check_reads_per_position(project, host)
        check_periodicity(project, host)


@cli.command()
@click.option('--remote/--local', default=False)
@click.argument('project')
def all_stats(project, remote):
    host = remote_host if remote else localhost
    get_all_stats(project, host)


@cli.command()
@click.option('--remote/--local', default=False)
def all_projects(remote):
    if remote:
        host = remote_host
    rdb = redis.StrictRedis(host=host)
    projects = rdb.smembers('projects')
    projects = [p.decode('utf-8') for p in projects]
    for project in projects:
        get_all_stats(project, host)

def clear_project_info(host, project):
    rdb = redis.StrictRedis(host=host)
    


if __name__ == '__main__':
    cli()
