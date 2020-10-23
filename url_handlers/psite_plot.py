import pandas as pd
import math
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

psite_plot = Blueprint('psite_plot', __name__)

codons = {'codon': ['AAA', 'AAC', 'AAG', 'AAT', 'ACA', 'ACC', 'ACG', 'ACT', 'AGA', 'AGC', 'AGG', 'AGT', 'ATA', 'ATC', 'ATG', 'ATT', 'CAA', 'CAC', 'CAG', 'CAT', 'CCA', 'CCC', 'CCG', 'CCT', 'CGA', 'CGC', 'CGG', 'CGT', 'CTA', 'CTC', 'CTG', 'CTT', 'GAA', 'GAC', 'GAG', 'GAT', 'GCA', 'GCC', 'GCG', 'GCT', 'GGA', 'GGC', 'GGG', 'GGT', 'GTA', 'GTC', 'GTG', 'GTT', 'TAA', 'TAC', 'TAG', 'TAT', 'TCA', 'TCC', 'TCG', 'TCT', 'TGA', 'TGC', 'TGG', 'TGT', 'TTA', 'TTC', 'TTG', 'TTT'], 'Aa': ['Lys', 'Asn', 'Lys', 'Asn', 'Thr', 'Thr', 'Thr', 'Thr', 'Arg', 'Ser', 'Arg', 'Ser', 'Ile', 'Ile', 'Met', 'Ile', 'Gln', 'His', 'Gln', 'His', 'Pro', 'Pro', 'Pro', 'Pro', 'Arg', 'Arg', 'Arg', 'Arg', 'Leu', 'Leu', 'Leu', 'Leu', 'Glu', 'Asp', 'Glu', 'Asp', 'Ala', 'Ala', 'Ala', 'Ala', 'Gly', 'Gly', 'Gly', 'Gly', 'Val', 'Val', 'Val', 'Val', 'Stp', 'Tyr', 'Stp', 'Tyr', 'Ser', 'Ser', 'Ser', 'Ser', 'Stp', 'Cys', 'Trp', 'Cys', 'Leu', 'Phe', 'Leu', 'Phe'], 'aa': ['K', 'N', 'K', 'N', 'T', 'T', 'T', 'T', 'R', 'S', 'R', 'S', 'I', 'I', 'M', 'I', 'Q', 'H', 'Q', 'H', 'P', 'P', 'P', 'P', 'R', 'R', 'R', 'R', 'L', 'L', 'L', 'L', 'E', 'D', 'E', 'D', 'A', 'A', 'A', 'A', 'G', 'G', 'G', 'G', 'V', 'V', 'V', 'V', 'O', 'Y', 'O', 'Y', 'S', 'S', 'S', 'S', 'O', 'C', 'W', 'C', 'L', 'F', 'L', 'F'], 'AA': ['Lysine', 'Asparagine', 'Lysine', 'Asparagine', 'Threonine', 'Threonine', 'Threonine', 'Threonine', 'Arginine', 'Serine', 'Arginine', 'Serine', 'Isoleucine', 'Isoleucine', 'Methionine', 'Isoleucine', 'Glutamine', 'Histidine', 'Glutamine', 'Histidine', 'Proline', 'Proline', 'Proline', 'Proline', 'Arginine', 'Arginine', 'Arginine', 'Arginine', 'Leucine', 'Leucine', 'Leucine', 'Leucine', 'Glutamic_acid', 'Aspartic_acid', 'Glutamic_acid', 'Aspartic_acid', 'Alanine', 'Alanine', 'Alanine', 'Alanine', 'Glycine', 'Glycine', 'Glycine', 'Glycine', 'Valine', 'Valine', 'Valine', 'Valine', 'Stop', 'Tyrosine', 'Stop', 'Tyrosine', 'Serine', 'Serine', 'Serine', 'Serine', 'Stop', 'Cysteine', 'Tryptophan', 'Cysteine', 'Leucine', 'Phenylalanine', 'Leucine', 'Phenylalanine']}

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

    codon_df = pd.DataFrame(codons)
    codon_df = codon_df.sort_values(by='Aa')
    codon_df = codon_df.drop(['AA', 'aa'], axis=1)
    p_df = p_df.merge(codon_df, on='codon').dropna()
    a_df = a_df.merge(codon_df, on='codon').dropna()
    e_df = e_df.merge(codon_df, on='codon').dropna()

    cols = ['codon', 'Aa', s1, s2, '{}_norm'.format(s1), '{}_norm'.format(s2)]

    p_df = p_df[cols].round(7)
    a_df = a_df[cols].round(7)
    e_df = e_df[cols].round(7)

    p_df['value'] = p_df['{}_norm'.format(s1)] / p_df['{}_norm'.format(s2)]
    p_df['value'] = p_df['value'].apply(lambda x: math.log2(x)).round(7)

    a_df['value'] = a_df['{}_norm'.format(s1)] / a_df['{}_norm'.format(s2)]
    a_df['value'] = a_df['value'].apply(lambda x: math.log2(x)).round(7)

    e_df['value'] = e_df['{}_norm'.format(s1)] / e_df['{}_norm'.format(s2)]
    e_df['value'] = e_df['value'].apply(lambda x: math.log2(x)).round(7)

    min_fc = min(p_df['value'].min(), a_df['value'].min(), e_df['value'].min())
    max_fc = max(p_df['value'].max(), a_df['value'].max(), e_df['value'].max())

    middle_val = abs(max_fc / min_fc)
    if abs(max_fc) < abs(min_fc):
        # positive
        middle_val = -1 * middle_val

    max_fc = max(abs(min_fc), max_fc)
    min_fc = -1 * max_fc

    x_categories = [
        'GCC', 'GCT', 'GCG', 'GCA', '',
        'AGA', 'CGC', 'CGA', 'CGG', 'CGT', 'AGG', '',
        'AAC', 'AAT', '',
        'GAT', 'GAC', '',
        'TGC', 'TGT', '',
        'CAA', 'CAG', '',
        'GAG', 'GAA', '',
        'GGG', 'GGT', 'GGC', 'GGA', '',
        'CAC', 'CAT', '',
        'ATT', 'ATC', 'ATA', '',
        'CTA', 'CTC', 'CTG', 'TTG', 'TTA', 'CTT', '',
        'AAA', 'AAG', '',
        'ATG', '',
        'TTT', 'TTC', '',
        'CCT', 'CCG', 'CCC', 'CCA', '',
        'TCA', 'AGT', 'TCT', 'AGC', 'TCC', 'TCG', '',
        'TGA', 'TAA', 'TAG', '',
        'ACA', 'ACC', 'ACT', 'ACG', '',
        'TGG', '',
        'TAT', 'TAC', '',
        'GTT', 'GTG', 'GTC', 'GTA']

    plot_series = []
    for i in range(len(x_categories)):
        codon = x_categories[i]
        if codon == '':
            plot_series += [{
                'x': i,
                'y': 0,
                'value': 'null',
            }, {
                'x': i,
                'y': 1,
                'value': 'null',
            }, {
                'x': i,
                'y': 2,
                'value': 'null'
            }]
        else:
            cur_p = p_df.loc[p_df['codon'] == codon]
            if len(cur_p) == 0:
                plot_series += [{'x': i, 'y': 0, 'codon': codon, 'Aa': codon_df.loc[codon_df['codon'] == codon].iloc[0]['Aa'],
                                 s1: 0, s2: 0, '{}_norm'.format(s1): 0, '{}_norm'.format(s2): 0, 'site': 'P'}]
            else:
                cur_p['x'] = i
                cur_p['y'] = 0
                cur_p['site'] = 'P'
                plot_series += cur_p.to_dict('records')

            cur_a = a_df.loc[a_df['codon'] == codon]
            if len(cur_a) == 0:
                plot_series += [{'x': i, 'y': 0, 'codon': codon, 'Aa': codon_df.loc[codon_df['codon'] == codon].iloc[0]['Aa'],
                                 s1: 0, s2: 0, '{}_norm'.format(s1): 0, '{}_norm'.format(s2): 0, 'site': 'P'}]
            else:
                cur_a['x'] = i
                cur_a['y'] = 1
                cur_a['site'] = 'A'
                plot_series += cur_a.to_dict('records')

            cur_e = e_df.loc[e_df['codon'] == codon]
            if len(cur_e) == 0:
                plot_series += [{'x': i, 'y': 0, 'codon': codon, 'Aa': codon_df.loc[codon_df['codon'] == codon].iloc[0]['Aa'],
                                 s1: 0, s2: 0, '{}_norm'.format(s1): 0, '{}_norm'.format(s2): 0, 'site': 'P'}]
            else:
                cur_e['x'] = i
                cur_e['y'] = 2
                cur_e['site'] = 'E'
                plot_series += cur_e.to_dict('records')

    return render_template('psite_plot.html', psite_series=plot_series, contrasts=contrasts, selected_contrast=contrast,
                           x_categories=x_categories, min_fc=min_fc, max_fc=max_fc, middle_val=middle_val)
