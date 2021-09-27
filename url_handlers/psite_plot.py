import pandas as pd
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
    p_df = pd.DataFrame(json.loads(p_data))
    a_df = pd.DataFrame(json.loads(a_data))
    e_df = pd.DataFrame(json.loads(e_data))

    # getting rid of stop and start codons
    p_df = p_df.loc[~p_df['aa'].isin(['Stp', 'Str'])]
    a_df = a_df.loc[~a_df['aa'].isin(['Stp', 'Str'])]
    e_df = e_df.loc[~e_df['aa'].isin(['Stp', 'Str'])]

    # check if any contrasts selected
    selected = request.form.getlist('selected_contrasts')
    if len(selected) == 0:
        return render_template('psite_plot.html', error='Please select contrasts', contrasts=contrasts)

    # group by site
    group_by_site = request.form.get('group_by_site') == 'site'

    # normalization
    norm = request.form.get('normalization', 'tpm')

    # group by codon or by amino acid
    group_by_aa = request.form.get('group_by_codon') != 'codon'

    if group_by_aa:
        p_df = p_df.groupby('aa').sum().reset_index()
        a_df = a_df.groupby('aa').sum().reset_index()
        e_df = e_df.groupby('aa').sum().reset_index()

    # get x categories for highcharts
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
            'ATG_M', '', # 'ATG_S', '',  # methionine & start codon
            'TTC', 'TTT', '',
            'CCA', 'CCC', 'CCG', 'CCT', '',
            'AGC', 'AGT', 'TCA', 'TCC', 'TCG', 'TCT', '',
            # 'TAA', 'TAG', 'TGA', '',  # skip Stop codons
            'ACA', 'ACC', 'ACG', 'ACT', '',
            'TGG', '',
            'TAC', 'TAT', '',
            'GTA', 'GTC', 'GTG', 'GTT']

    max_fc = None
    min_fc = None
    for contrast in selected:
        s1, s2 = contrast.split('__vs__')
        cols = ['aa', s1, s2, '{}_{}'.format(norm, s1), '{}_{}'.format(norm, s2)]
        if not group_by_aa:
            cols = cols + ['codon']

        # calculating fc as (sample - control) / control
        p_df[contrast] = (p_df['{}_{}'.format(norm, s1)] - p_df['{}_{}'.format(norm, s2)]) / p_df['{}_{}'.format(norm, s2)]
        a_df[contrast] = (a_df['{}_{}'.format(norm, s1)] - a_df['{}_{}'.format(norm, s2)]) / a_df['{}_{}'.format(norm, s2)]
        e_df[contrast] = (e_df['{}_{}'.format(norm, s1)] - e_df['{}_{}'.format(norm, s2)]) / e_df['{}_{}'.format(norm, s2)]

        # round values
        cols = cols + [contrast]
        p_df[cols] = p_df[cols].round(3)
        a_df[cols] = a_df[cols].round(3)
        e_df[cols] = e_df[cols].round(3)

        if min_fc is None:
            min_fc = min(p_df[contrast].min(), a_df[contrast].min(), e_df[contrast].min())
        else:
            min_fc = min(min_fc, p_df[contrast].min(), a_df[contrast].min(), e_df[contrast].min())
        if max_fc is None:
            max_fc = max(p_df[contrast].max(), a_df[contrast].max(), e_df[contrast].max())
        else:
            max_fc = max(max_fc, p_df[contrast].max(), a_df[contrast].max(), e_df[contrast].max())

    max_fc = max(abs(min_fc), abs(max_fc))
    min_fc = -1 * max_fc
    middle_val = 0

    e_series = []
    p_series = []
    a_series = []
    plot_series = []
    for c in range(len(selected)):
        contrast = selected[c]
        s1, s2 = contrast.split('__vs__')
        cols = ['aa', s1, s2, '{}_{}'.format(norm, s1), '{}_{}'.format(norm, s2), contrast]
        if not group_by_aa:
            cols = cols + ['codon']
        for i in range(len(x_categories)):
            cat = x_categories[i]
            if cat == '':
                plot_series += [{}]
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
                        aa = 'Str'
                    else:
                        cur_p = p_df.loc[p_df['codon'] == cat]
                        cur_e = e_df.loc[e_df['codon'] == cat]
                        cur_a = a_df.loc[a_df['codon'] == cat]
                        codon = cat
                        aa = cur_p['aa'].tolist()
                        if len(aa) != 0:
                            aa = aa[0]
                        else:
                            continue

                # select cols for current contrast
                cur_p = cur_p[cols]
                cur_a = cur_a[cols]
                cur_e = cur_e[cols]
                cur_p['value'] = cur_p[contrast]
                cur_a['value'] = cur_a[contrast]
                cur_e['value'] = cur_e[contrast]
                cur_p['contrast'] = contrast
                cur_a['contrast'] = contrast
                cur_e['contrast'] = contrast

                # getting plot series
                if len(cur_a) == 0:
                    plot_series += [{'x': i, 'y': 0 + c * 4, 'codon': codon, 'aa': aa, 'site': 'A', 'value': 0}]
                else:
                    cur_a['x'] = i
                    cur_a['site'] = 'A'
                    if not group_by_site:
                        cur_a['y'] = 0 + c * 4
                        plot_series += cur_a.to_dict('records')
                    else:
                        cur_a['y'] = c
                        a_series += cur_a.to_dict('records')

                if len(cur_p) == 0:
                    plot_series += [{'x': i, 'y': 1 + c * 4, 'codon': codon, 'aa': aa, 'site': 'P', 'value': 0}]
                else:
                    cur_p['x'] = i
                    cur_p['site'] = 'P'
                    if not group_by_site:
                        cur_p['y'] = 1 + c * 4
                        plot_series += cur_p.to_dict('records')
                    else:
                        cur_p['y'] = len(selected) + c + 1
                        p_series += cur_p.to_dict('records')

                if len(cur_e) == 0:
                    plot_series += [{'x': i, 'y': 2 + c * 4, 'codon': codon, 'aa': aa, 'site': 'E', 'value': 0}]
                else:
                    cur_e['x'] = i
                    cur_e['site'] = 'E'
                    if not group_by_site:
                        cur_e['y'] = 2 + c * 4
                        plot_series += cur_e.to_dict('records')
                    else:
                        cur_e['y'] = len(selected) * 2 + c + 2
                        e_series += cur_e.to_dict('records')
        if group_by_aa:
            if not group_by_site:
                plot_series += [{}]

    if group_by_site:
        plot_series = e_series + [{'y': len(selected) + 1}] + p_series + [{'y': len(selected) * 2 + 2}] + a_series

    y_categories = []
    if not group_by_site:
        for contrast in selected:
            y_categories += ['A-site ({})'.format(contrast), 'P-site ({})'.format(contrast), 'E-site ({})'.format(contrast), '']
    else:
        for contrast in selected:
            y_categories += ['A-site ({})'.format(contrast)]
        y_categories += ['']
        for contrast in selected:
            y_categories += ['P-site ({})'.format(contrast)]
        y_categories += ['']
        for contrast in selected:
            y_categories += ['E-site ({})'.format(contrast)]

    group_by_codon = not group_by_aa
    return render_template('psite_plot.html', psite_series=plot_series, contrasts=contrasts, y_categories=y_categories,
                           x_categories=x_categories, min_fc=min_fc, max_fc=max_fc, middle_val=middle_val,
                           group_by_codon=group_by_codon, norm=norm, selected_contrasts=selected, dataset_id=project_id,
                           group_by_site=group_by_site)
