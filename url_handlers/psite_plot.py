import pandas as pd
import math
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

psite_plot = Blueprint('psite_plot', __name__)

@psite_plot.route('/psite_plot/<project_id>', methods=['GET', 'POST'])
@login_required
def get_psite_plot(project_id):
    from main import get_db
    rdb = get_db()
    contrasts = rdb.smembers('contrasts_{}'.format(project_id))
    contrasts = sorted([c.decode('utf-8') for c in contrasts])
    if request.method == 'GET':
        return render_template("psite_plot.html", contrasts=contrasts)

    p_data = rdb.get('psites_{}'.format(project_id))
    a_data = rdb.get('asites_{}'.format(project_id))
    e_data = rdb.get('esites_{}'.format(project_id))
    if p_data is None and a_data is None and e_data is None:
        return render_template('psite_plot.html', error='No data for project {} found'.format(project_id))

    # if POST
    contrast = request.form.get('contrast')
    s1, s2 = contrast.split('__vs__')
    p_df = pd.DataFrame(json.loads(p_data))
    a_df = pd.DataFrame(json.loads(a_data))
    e_df = pd.DataFrame(json.loads(e_data))

    # normalization
    norm = request.form.get('normalization', 'tpm')

    # group by codon or by amino acid
    group_by_aa = request.form.get('group_by_codon') != 'codon'

    if group_by_aa:
        p_df = p_df.groupby('aa').sum().reset_index()
        a_df = a_df.groupby('aa').sum().reset_index()
        e_df = e_df.groupby('aa').sum().reset_index()

    cols = ['aa', s1, s2, '{}_{}'.format(norm, s1), '{}_{}'.format(norm, s2)]
    if not group_by_aa:
        cols = cols + ['codon']

    # calculating fc as (sample - control) / control
    p_df['value'] = (p_df['{}_{}'.format(norm, s1)] - p_df['{}_{}'.format(norm, s2)]) / p_df['{}_{}'.format(norm, s2)]
    a_df['value'] = (a_df['{}_{}'.format(norm, s1)] - a_df['{}_{}'.format(norm, s2)]) / a_df['{}_{}'.format(norm, s2)]
    e_df['value'] = (e_df['{}_{}'.format(norm, s1)] - e_df['{}_{}'.format(norm, s2)]) / e_df['{}_{}'.format(norm, s2)]

    p_df['value'] = p_df['value'].round(3)
    a_df['value'] = a_df['value'].round(3)
    e_df['value'] = e_df['value'].round(3)

    p_df[cols] = p_df[cols].round(3)
    a_df[cols] = a_df[cols].round(3)
    e_df[cols] = e_df[cols].round(3)

    min_fc = min(p_df['value'].min(), a_df['value'].min(), e_df['value'].min())
    max_fc = max(p_df['value'].max(), a_df['value'].max(), e_df['value'].max())

    max_fc = max(abs(min_fc), max_fc)
    min_fc = -1 * max_fc
    middle_val = 0

    if group_by_aa:
        x_categories = p_df['aa'].unique().tolist()
    else:
        x_categories = [
            'GCA', 'GCC', 'GCG', 'GCT', '',
            'AGA', 'CGC', 'CGA', 'CGG', 'CGT', 'AGG', '',
            'AAC', 'AAT', '',
            'GAC', 'GAT', '',
            'TGC', 'TGT', '',
            'CAA', 'CAG', '',
            'GAA', 'GAG', '',
            'GGA', 'GGC', 'GGG', 'GGT', '',
            'CAC', 'CAT', '',
            'ATA', 'ATC', 'ATT', '',
            'CTA', 'CTC', 'CTG', 'CTT', 'TTA', 'TTG', '',
            'AAA', 'AAG', '',
            'ATG_M', 'ATG_S', '',  # methionine & start codon
            'TTC', 'TTT', '',
            'CCA', 'CCC', 'CCG', 'CCT', '',
            'AGC', 'AGT', 'TCA', 'TCC', 'TCG', 'TCT', '',
            # 'TAA', 'TAG', 'TGA', '',  # skip Stop codons
            'ACA', 'ACC', 'ACG', 'ACT', '',
            'TGG', '',
            'TAC', 'TAT', '',
            'GTA', 'GTC', 'GTG', 'GTT']

    plot_series = []
    for i in range(len(x_categories)):
        cat = x_categories[i]
        # skip Stop codons
        if cat == 'Stp':
            continue
        elif cat == '':
            plot_series += [{}, {}, {}]
        else:
            if group_by_aa:
                cur_p = p_df.loc[p_df['aa'] == cat]
                cur_e = e_df.loc[e_df['aa'] == cat]
                cur_a = a_df.loc[a_df['aa'] == cat]
                codon = ''
                aa = cat
            else:
                if cat == 'ATG_M':
                    cur_p = p_df.loc[(p_df['codon'] == 'ATG') & (p_df['aa'] == 'Met')]
                    cur_e = e_df.loc[(e_df['codon'] == 'ATG') & (e_df['aa'] == 'Met')]
                    cur_a = a_df.loc[(a_df['codon'] == 'ATG') & (a_df['aa'] == 'Met')]
                    codon = 'ATG'
                    aa = 'Met'
                elif cat == 'ATG_S':
                    cur_p = p_df.loc[(p_df['codon'] == 'ATG') & (p_df['aa'] == 'Str')]
                    cur_e = e_df.loc[(e_df['codon'] == 'ATG') & (e_df['aa'] == 'Str')]
                    cur_a = a_df.loc[(a_df['codon'] == 'ATG') & (a_df['aa'] == 'Str')]
                    codon = 'ATG'
                    aa = 'Start'
                else:
                    cur_p = p_df.loc[p_df['codon'] == cat]
                    cur_e = e_df.loc[e_df['codon'] == cat]
                    cur_a = a_df.loc[a_df['codon'] == cat]
                    codon = cat
                    aa = cur_p.iloc[0]['aa']

            if len(cur_p) == 0:
                plot_series += [{ 'x': i, 'y': 0, 'codon': codon, 'aa': aa, 'site': 'P', 'value': 0}]
            else:
                cur_p['x'] = i
                cur_p['y'] = 0
                cur_p['site'] = 'P'
                plot_series += cur_p.to_dict('records')

            if len(cur_a) == 0:
                plot_series += [{'x': i, 'y': 1, 'codon': codon, 'aa': aa, 'site': 'A', 'value': 0}]
            else:
                cur_a['x'] = i
                cur_a['y'] = 1
                cur_a['site'] = 'A'
                plot_series += cur_a.to_dict('records')

            if len(cur_e) == 0:
                plot_series += [{'x': i, 'y': 2, 'codon': codon, 'aa': aa, 'site': 'E', 'value': 0}]
            else:
                cur_e['x'] = i
                cur_e['y'] = 2
                cur_e['site'] = 'E'
                plot_series += cur_e.to_dict('records')

    group_by_codon = not group_by_aa
    return render_template('psite_plot.html', psite_series=plot_series, contrasts=contrasts, selected_contrast=contrast,
                           x_categories=x_categories, min_fc=min_fc, max_fc=max_fc, middle_val=middle_val,
                           group_by_codon=group_by_codon, norm=norm)
