import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

alignments = Blueprint('alignments', __name__)


@alignments.route('/cumulative_reads/<project_id>', methods=['GET', 'POST'])
@login_required
def get_cumulative_reads(project_id):
    from main import get_db
    rdb = get_db()

    list_of_samples = []
    rdb_data = rdb.get("sample_info_{}".format(project_id))
    if rdb_data is None:
        return render_template("cumulative_reads.html", error="No data found")

    samples_info = json.loads(rdb_data.decode('utf-8'))
    for sample in samples_info:
        list_of_samples.append(sample.get('sample'))

    bam_types = rdb.smembers('bam_types_{}'.format(project_id))

    trans = rdb.get('transcriptLength.txt')
    if not trans:
        return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types, error="transcriptLength.txt not found!!")

    list_of_genes = rdb.smembers('genes_{}'.format(project_id))
    if request.method == "GET":
        return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types, genes=list_of_genes)

    selected_gene = request.form.get('gene')
    selected_samples = request.form.getlist('selected_samples')
    bam_type = request.form.get('bam_type')
    if bam_type is None:
        bam_type = 'all_unique'

    normalization = request.form.get('normalization', 'raw_counts')

    trans = pd.read_msgpack(trans)
    trans = trans.loc[trans['gene_name'] == selected_gene]

    series = []
    error = ""
    warning = ""
    for sample in selected_samples:
        rdb_data = rdb.get('alignment__{}__{}__{}'.format(project_id, bam_type, sample))
        if rdb_data is None:
            error += "No data found for sample {} ({})___".format(sample, bam_type)
            continue

        df = pd.read_msgpack(rdb_data)
        df = pd.merge(df, trans, on="transcript", how="inner")

        if len(df) == 0:
            error += "No reads in selected gene for sample {}___".format(sample)
            continue

        df = df.loc[df['start'] > df['5utr_len']]
        if len(df) == 0:
            error += "No reads in CDS for sample {}___".format(sample)

        # only consider CDS
        df['start'] = df['start'] - df['5utr_len']
        df['dup'] = 1
        # remove duplicated sequences and sum their number
        df['dup'] = df.groupby(['seq'])['dup'].transform('sum')

        # new df -> length of transcript
        df1 = pd.DataFrame()
        df1['pos'] = [i for i in range(1, trans['cds_len'].iloc[0] + 1)]
        df1['counts'] = 0
        
        # assign total #reads in each position
        total = 0
        df = df.sort_values(by="start")
        for i, row in df.iterrows():
            total += row['dup']
            df1.loc[df1['pos'] == row['start'], 'counts'] = total

        # include last pos of transcript -> 100%
        df1.loc[df1['pos'] == trans['cds_len'].iloc[0], 'counts'] = total
        # remove positions with 0 counts
        df1 = df1.drop(df1.loc[df1['counts'] == 0].index)

        if normalization != 'raw_counts':
            counts_data = rdb.get('counts_{}_{}_{}'.format(project_id, bam_type, sample))
            if counts_data is None:
                # upload counts with:
                # 1. /icgc/dkfzlsdf/analysis/OE0532/software/diricore_subset/1_get_seq_from_bam.sh 18927 all_unique
                # 2. /icgc/dkfzlsdf/analysis/OE0532/software/scripts/normalize_counts.py 18927 all_unique
                # 3. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_counts.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt
                warning += 'Normalized counts are not found in DB. Showing raw counts. Sample: {}'.format(sample)
                # don't skip anyway -> will showing raw counts
            else:
                counts_data = counts_data.decode('utf-8')
                counts_data = json.loads(counts_data)
                counts_df = pd.DataFrame(counts_data)
                counts_df = counts_df.loc[counts_df['gene_name'] == selected_gene]

                # raw counts divide by norm_counts -> to see how many tpm/cpm/rpkm in 1 raw count
                norm_factor = 1
                if normalization == 'tpm':
                    norm_factor = counts_df['tpm'].astype(float).sum()
                elif normalization == 'cpm':
                    norm_factor = counts_df['cpm'].astype(float).sum()
                elif normalization == 'rpkm':
                    norm_factor = counts_df['rpkm'].astype(float).sum()
                elif normalization == 'percent':
                    norm_factor = df1['counts'].astype(int).max() * 0.01 # counts for 1 gene only
                else:
                    warning += 'Normalization method not found: {}. Showing raw counts.'.format(normalization)

                # and now we multiply this number by the real number of reads in each position
                df1['norm_counts'] = df1['counts'] / norm_factor
                df1['norm_counts'] = df1['norm_counts'].round(3)
                df1 = df1.drop('counts', axis=1)

        df1.columns = ['x', 'y']
        series.append({'name': sample, 'data': df1.to_dict('records'), 'turboThreshold': len(df1)})

    if error:
        return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types,
                               selected_gene=selected_gene, bam_type=bam_type, selected_samples=selected_samples,
                               error=error, genes=list_of_genes)
    return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types, selected_gene=selected_gene,
                           bam_type=bam_type, selected_samples=selected_samples, series=series, genes=list_of_genes,
                           normalization=normalization, error=warning)


@alignments.route('/reads_distribution/<project_id>', methods=['GET', 'POST'])
def get_reads(project_id):
    from main import get_db
    rdb = get_db()

    list_of_samples = []
    rdb_data = rdb.get("sample_info_{}".format(project_id))
    if rdb_data is None:
        # Upload data with:
        # 1. /icgc/dkfzlsdf/analysis/OE0532/software/diricore_subset/1_get_seq_from_bam.sh 18927 all_unique
        # 2. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_transcriptome_alignment.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt local
        # 3. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/normalize_counts.py 18927 all_unique
        # 4. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_counts.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt
        return render_template("ucsc_browser.html", error="No data found")

    samples_info = json.loads(rdb_data.decode('utf-8'))
    for sample in samples_info:
        list_of_samples.append(sample.get('sample'))

    bam_types = rdb.smembers('bam_types_{}'.format(project_id))

    trans = rdb.get('transcriptLength.txt')
    if not trans:
        return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types, error="transcriptLength.txt not found!!")

    list_of_genes = rdb.smembers('genes_{}'.format(project_id))
    if request.method == "GET":
        return render_template("ucsc_browser.html", samples=list_of_samples, bam_types=bam_types, genes=list_of_genes)

    selected_gene = request.form.get('gene')
    selected_samples = request.form.getlist('selected_samples')
    bam_type = request.form.get('bam_type')
    if bam_type is None:
        bam_type = 'hq_unique'

    trans = pd.read_msgpack(trans)
    trans = trans.loc[trans['gene_name'] == selected_gene]
    one_plot = request.form.get('subplots', 'one_plot')

    normalization = request.form.get('normalization', 'raw_counts')

    series = []
    error = ""
    warning = ""
    for sample in selected_samples:
        rdb_data = rdb.get('alignment__{}__{}__{}'.format(project_id, bam_type, sample))
        if rdb_data is None:
            error += "No data found for sample {} ({})___".format(sample, bam_type)
            continue

        df = pd.read_msgpack(rdb_data)
        df = pd.merge(df, trans, on="transcript", how="inner")

        if len(df) == 0:
            error += "No reads in selected gene for sample {}___".format(sample)
            continue

        df['dup'] = 1
        df['dup'] = df.groupby(['seq'])['dup'].transform('sum')
        df['start'] = df['start'] - df['5utr_len']

        # df1 has length of selected transcript length
        # one row is one position
        df1 = pd.DataFrame()
        df1['pos'] = [i for i in range(1, trans['cds_len'].iloc[0] + 1)]
        df1['counts'] = 0

        # in each read we add +1 count to the positions, where this read maps (between start and start + length of seq)
        for i, row in df.iterrows():
            df1.loc[(df1['pos'] >= row['start']) & (df1['pos'] <= row['start'] + len(row['seq'])), 'counts'] += 1

        if normalization != 'raw_counts':
            counts_data = rdb.get('counts_{}_{}_{}'.format(project_id, bam_type, sample))
            if counts_data is None:
                # upload counts with:
                # 1. /icgc/dkfzlsdf/analysis/OE0532/software/diricore_subset/1_get_seq_from_bam.sh 18927 all_unique
                # 2. /icgc/dkfzlsdf/analysis/OE0532/software/scripts/normalize_counts.py 18927 all_unique
                # 3. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_counts.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt
                warning += 'Normalized counts are not found in DB. Showing raw counts. Sample: {}'.format(sample)
                # don't skip anyway -> will showing raw counts
            else:
                counts_data = counts_data.decode('utf-8')
                counts_data = json.loads(counts_data)
                counts_df = pd.DataFrame(counts_data)
                counts_df = counts_df.loc[counts_df['gene_name'] == selected_gene]
                counts = counts_df['counts'].astype(int).sum() # counts for 1 gene only

                # raw counts divide by norm_counts -> to see how many tpm/cpm/rpkm in 1 raw count
                norm_factor = 1
                if normalization == 'tpm':
                    norm_factor = counts_df['tpm'].astype(float).sum()
                elif normalization == 'cpm':
                    norm_factor = counts_df['cpm'].astype(float).sum()
                elif normalization == 'rpkm':
                    norm_factor = counts_df['rpkm'].astype(float).sum()
                else:
                    warning += 'Normalization method not found: <b>{}</b>. Showing raw counts. Sample: {}'.format(normalization, sample)
                # and now we multiply this number by the real number of reads in each position
                df1['norm_counts'] = df1['counts'] / norm_factor
                df1['norm_counts'] = df1['norm_counts'].round(3)
                df1 = df1.drop('counts', axis=1)
        df1.columns = ['x', 'y']
        series.append({'name': sample, 'data': df1.to_dict('records'), 'turboThreshold': len(df1)})

    if error:
        return render_template("ucsc_browser.html", samples=list_of_samples, bam_types=bam_types,
                               selected_gene=selected_gene, bam_type=bam_type, selected_samples=selected_samples,
                               error=error, genes=list_of_genes)
    return render_template('ucsc_browser.html', samples=list_of_samples, bam_types=bam_types, selected_gene=selected_gene,
                           bam_type=bam_type, selected_samples=selected_samples, series=series, genes=list_of_genes,
                           one_plot=one_plot, error=warning, normalization=normalization)


@alignments.route('/density_plot/<project_id>', methods=['GET', 'POST'])
def get_density_plot(project_id):
    from main import get_db
    rdb = get_db()
    list_of_samples = []
    rdb_data = rdb.get("sample_info_{}".format(project_id))
    if rdb_data is None:
        # Upload data with:
        # 1. /icgc/dkfzlsdf/analysis/OE0532/software/diricore_subset/1_get_seq_from_bam.sh 18927 all_unique
        # 2. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_density_plots.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt local
        # 3. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/normalize_counts.py 18927 all_unique
        # 4. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_counts.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt
        return render_template("density_plot.html", error="No data found")

    samples_info = json.loads(rdb_data.decode('utf-8'))
    for sample in samples_info:
        list_of_samples.append(sample.get('sample'))

    bam_types = rdb.smembers('bam_types_{}'.format(project_id))

    trans = rdb.get('transcriptLength.txt')
    if not trans:
        return render_template("density_plot.html", samples=list_of_samples, bam_types=bam_types, error="transcriptLength.txt not found!!")

    list_of_genes = rdb.smembers('genes_{}'.format(project_id))
    if request.method == "GET":
        return render_template("density_plot.html", samples=list_of_samples, bam_types=bam_types, genes=list_of_genes)

    selected_gene = request.form.get('gene')
    selected_samples = request.form.getlist('selected_samples')
    bam_type = request.form.get('bam_type')
    if bam_type is None:
        bam_type = 'all_unique'

    trans = pd.read_msgpack(trans)
    trans = trans.loc[trans['gene_name'] == selected_gene]
    one_plot = request.form.get('subplots', 'one_plot')

    normalization = request.form.get('normalization', 'raw_counts')

    series = []
    error = ""
    warning = ""
    for sample in selected_samples:

        rdb_data = rdb.get('density__{}__{}__{}'.format(project_id, bam_type, sample))
        if rdb_data is None:
            error += "No data found for sample {} ({})___".format(sample, bam_type)
            continue

        rdb_data = json.loads(rdb_data)
        df = pd.DataFrame(rdb_data)
        df = pd.merge(df, trans, on="transcript", how="inner")

        if len(df) == 0:
            error += "No reads in selected gene for sample {}___".format(sample)
            continue

        df['start'] = df['start'] - df['5utr_len']

        # df1 has length of selected transcript length
        # one row is one position
        df1 = pd.DataFrame()
        df1['pos'] = [i for i in range(1, trans['cds_len'].iloc[0] + 1)]
        df1['counts'] = 0

        # in each read we add +1 count to the positions, where this read maps (between start and start + length of seq)
        for i, row in df.iterrows():
            df1.loc[df1['pos'] == row['start'], 'counts'] += int(row['dup'])

        if normalization != 'raw_counts':
            counts_data = rdb.get('counts_{}_{}_{}'.format(project_id, bam_type, sample))
            if counts_data is None:
                # upload counts with:
                # 1. /icgc/dkfzlsdf/analysis/OE0532/software/diricore_subset/1_get_seq_from_bam.sh 18927 all_unique
                # 2. /icgc/dkfzlsdf/analysis/OE0532/software/scripts/normalize_counts.py 18927 all_unique
                # 3. python /icgc/dkfzlsdf/analysis/OE0532/software/scripts/upload_counts.py 18927 all_unique /icgc/dkfzlsdf/analysis/OE0532/18927/analysis/input/metadata/density_plot_top150.txt
                warning += 'Normalized counts are not found in DB. Showing raw counts. Sample: {}'.format(sample)
                # don't skip anyway -> will showing raw counts
            else:
                counts_data = counts_data.decode('utf-8')
                counts_data = json.loads(counts_data)
                counts_df = pd.DataFrame(counts_data)
                counts_df = counts_df.loc[counts_df['gene_name'] == selected_gene]

                # raw counts divide by norm_counts -> to see how many tpm/cpm/rpkm in 1 raw count
                norm_factor = 1
                if normalization == 'tpm':
                    norm_factor = counts_df['tpm'].astype(float).sum()
                elif normalization == 'cpm':
                    norm_factor = counts_df['cpm'].astype(float).sum()
                elif normalization == 'rpkm':
                    norm_factor = counts_df['rpkm'].astype(float).sum()
                else:
                    warning += 'Normalization method not found: <b>{}</b>. Showing raw counts. Sample: {}'.format(normalization, sample)
                # and now we multiply this number by the real number of reads in each position
                df1['norm_counts'] = df1['counts'] / norm_factor
                df1['norm_counts'] = df1['norm_counts'].round(3)
                df1 = df1.drop('counts', axis=1)
        df1.columns = ['x', 'y']
        series.append({'name': sample, 'data': df1.to_dict('records'), 'turboThreshold': len(df1)})

    if error:
        return render_template("cumulative_reads.html", samples=list_of_samples, bam_types=bam_types,
                               selected_gene=selected_gene, bam_type=bam_type, selected_samples=selected_samples,
                               error=error, genes=list_of_genes)
    return render_template('density_plot.html', samples=list_of_samples, bam_types=bam_types, selected_gene=selected_gene,
                           bam_type=bam_type, selected_samples=selected_samples, series=series, genes=list_of_genes,
                           one_plot=one_plot, error=warning, normalization=normalization)

