from flask import Blueprint, render_template, request, make_response, current_app
from flask_login import login_required, current_user
import json
import pandas as pd
import numpy as np


psite_dotplot = Blueprint('psite_dotplot', __name__)


def get_plot_series(project_id, aa, selected_contrasts, fc, genes_highlight, norm, search_genes=[]):
    from main import get_db
    rdb = get_db()
    amino_acids = rdb.smembers('aa_dotplot_{}'.format(project_id)) or []
    amino_acids = [aa.decode('utf-8') for aa in amino_acids]
    contrasts = rdb.smembers('contrasts_{}'.format(project_id)) or []
    contrasts = [c.decode('utf-8') for c in contrasts]

    psite = rdb.get('psite_dotplot_{}_{}'.format(project_id, aa))
    if psite is None:
        return render_template('psite_dotplot.html', error='No P-site data for {}'.format(aa), contrasts=contrasts,
                               amino_acids=amino_acids)

    asite = rdb.get('asite_dotplot_{}_{}'.format(project_id, aa))
    if asite is None:
        return render_template('psite_dotplot.html', error='No A-site data for {}'.format(aa), contrasts=contrasts,
                               amino_acids=amino_acids)

    esite = rdb.get('esite_dotplot_{}_{}'.format(project_id, aa))
    if esite is None:
        return render_template('psite_dotplot.html', error='No E-site data for {}'.format(aa), contrasts=contrasts,
                               amino_acids=amino_acids)

    psite = json.loads(psite.decode('utf-8'))
    psite = pd.DataFrame(psite)

    asite = json.loads(asite.decode('utf-8'))
    asite = pd.DataFrame(asite)

    esite = json.loads(esite.decode('utf-8'))
    esite = pd.DataFrame(esite)

    top_genes = []
    if genes_highlight is not None:
        if genes_highlight != 'do_not_highlight':
            n = int(genes_highlight.replace('top', ''))
            top_df = rdb.get('{}_top1000'.format(aa))
            if top_df is not None:
                top_df = json.loads(top_df)
                top_genes = pd.DataFrame(top_df).loc[:n]['gene'].tolist()

    p_series = {}
    a_series = {}
    e_series = {}
    all_genes = []
    for c in selected_contrasts:
        sample, control = c.split('__vs__')
        sample = '{}_{}'.format(norm, sample)
        control = '{}_{}'.format(norm, control)

        # psite
        p_df = psite[['gene', 'Aa', 'codon', sample, control]]
        p_df = p_df.dropna()
        all_genes += p_df['gene'].unique().tolist()
        p_df = p_df.groupby(['gene']).agg({sample: 'sum', control: 'sum'}).reset_index()
        p_df['x'] = np.log2(p_df[sample]).round(3)
        p_df['y'] = np.log2(p_df[control]).round(3)
        p_df[sample] = p_df[sample].round(3)
        p_df[control] = p_df[control].round(3)
        p_df[c] = np.log2(p_df[sample] / p_df[control])
        search_p = p_df.loc[p_df['gene'].isin(search_genes)].drop(c, axis=1)
        p_above_fc = p_df.loc[(p_df[c].abs() >= fc) & (~p_df['gene'].isin(search_genes))].drop(c, axis=1)
        top_p = p_df.loc[(p_df['gene'].isin(top_genes)) & (~p_df['gene'].isin(search_genes))].drop(c, axis=1)
        p_df = p_df.loc[(p_df[c].abs() < fc) & (~p_df['gene'].isin(top_genes)) & (~p_df['gene'].isin(search_genes))].drop(c, axis=1)

        p_series[c] = [{'name': c, 'data': p_df.to_dict('records'), 'turboThreshold': len(p_df)}]
        if len(p_above_fc) > 0:
            p_series[c].append({'name': 'Above threshold', 'data': p_above_fc.to_dict('records'),
                                'turboThreshold': len(p_above_fc), 'color': 'rgba(223, 83, 83, .5)'})
        if len(top_p) > 0:
            p_series[c].append({'name': genes_highlight, 'data': top_p.to_dict('records'), 'turboThreshold': len(top_p),
                        'color': '#00cc99'})
        if len(search_p) > 0:
            p_series[c].append({'name': 'Selected genes', 'data': search_p.to_dict('records'), 'color': '#ffcc00',
                                'marker': {'radius': 5}})
        # asite
        a_df = asite[['gene', 'Aa', 'codon', sample, control]]
        a_df = a_df.dropna()
        all_genes += a_df['gene'].unique().tolist()
        a_df = a_df.groupby(['gene']).agg({sample: 'sum', control: 'sum'}).reset_index()
        a_df['x'] = np.log2(a_df[sample]).round(3)
        a_df['y'] = np.log2(a_df[control]).round(3)
        a_df[sample] = a_df[sample].round(3)
        a_df[control] = a_df[control].round(3)
        a_df[c] = np.log2(a_df[sample] / a_df[control])

        search_a = a_df.loc[a_df['gene'].isin(search_genes)].drop(c, axis=1)
        a_above_fc = a_df.loc[(a_df[c].abs() >= fc) & (~a_df['gene'].isin(search_genes))].drop(c, axis=1)
        top_a = a_df.loc[(a_df['gene'].isin(top_genes)) & (~a_df['gene'].isin(search_genes))].drop(c, axis=1)
        a_df = a_df.loc[(a_df[c].abs() < fc) & (~a_df['gene'].isin(top_genes)) & (~a_df['gene'].isin(search_genes))].drop(c, axis=1)

        a_series[c] = [{'name': c, 'data': a_df.to_dict('records'), 'turboThreshold': len(a_df)}]
        if len(a_above_fc) > 0:
            a_series[c].append({'name': 'Above threshold', 'data': a_above_fc.to_dict('records'),
                                'turboThreshold': len(a_above_fc), 'color': 'rgba(223, 83, 83, .5)'})
        if len(top_a) > 0:
            a_series[c].append({'name': genes_highlight, 'data': top_a.to_dict('records'), 'turboThreshold': len(top_a),
                        'color': '#00cc99'})
        if len(search_a) > 0:
            a_series[c].append({'name': 'Selected genes', 'data': search_a.to_dict('records'), 'color': '#ffcc00',
                                'marker': {'radius': 5}})

        # esite
        e_df = esite[['gene', 'Aa', 'codon', sample, control]]
        e_df = e_df.dropna()
        all_genes += e_df['gene'].unique().tolist()
        e_df = e_df.groupby(['gene']).agg({sample: 'sum', control: 'sum'}).reset_index()
        e_df['x'] = np.log2(e_df[sample]).round(3)
        e_df['y'] = np.log2(e_df[control]).round(3)
        e_df[sample] = e_df[sample].round(3)
        e_df[control] = e_df[control].round(3)
        e_df[c] = np.log2(e_df[sample] / e_df[control])

        search_e = e_df.loc[e_df['gene'].isin(search_genes)].drop(c, axis=1)
        e_above_fc = e_df.loc[(e_df[c].abs() >= fc) & (~e_df['gene'].isin(search_genes))].drop(c, axis=1)
        top_e = e_df.loc[(e_df['gene'].isin(top_genes)) & (~e_df['gene'].isin(search_genes))].drop(c, axis=1)
        e_df = e_df.loc[(e_df[c].abs() < fc) & (~e_df['gene'].isin(top_genes)) & (~e_df['gene'].isin(search_genes))].drop(c, axis=1)

        e_series[c] = [{'name': c, 'data': e_df.to_dict('records'), 'turboThreshold': len(e_df)}]
        if len(e_above_fc) > 0:
            e_series[c].append({'name': 'Above threshold', 'data': e_above_fc.to_dict('records'),
                                'turboThreshold': len(e_above_fc), 'color': 'rgba(223, 83, 83, .5)'})
        if len(top_e) > 0:
            e_series[c].append({'name': genes_highlight, 'data': top_e.to_dict('records'), 'turboThreshold': len(top_e),
                        'color': '#00cc99'})
        if len(search_e) > 0:
            e_series[c].append({'name': 'Selected genes', 'data': search_e.to_dict('records'), 'color': '#ffcc00',
                                'marker': {'radius': 5}})
    all_genes = set(all_genes)
    return {'p_series': p_series, 'a_series': a_series, 'e_series': e_series, 'all_genes': all_genes}


@psite_dotplot.route('/psite_dotplot/<project_id>', methods=['GET', 'POST'])
@login_required
def get_psite_dotplot(project_id):
    from main import get_db
    rdb = get_db()
    amino_acids = rdb.smembers('aa_dotplot_{}'.format(project_id)) or []
    amino_acids = [aa.decode('utf-8') for aa in amino_acids]
    contrasts = rdb.smembers('contrasts_{}'.format(project_id)) or []
    contrasts = [c.decode('utf-8') for c in contrasts]
    if request.method == 'GET':
        return render_template('psite_dotplot.html', amino_acids=amino_acids, contrasts=contrasts)

    # if POST
    selected = request.form.getlist('selected_contrasts')
    if len(selected) == 0:
        return render_template('psite_dotplot.html', error='Please select contrasts', contrasts=contrasts, amino_acids=amino_acids)
    aa = request.form.get('amino_acid')
    if aa is None or aa == 'select':
        return render_template('psite_dotplot.html', error='Please select amino acid', contrasts=contrasts, amino_acids=amino_acids)

    norm = request.form.get('norm', 'tpm')
    genes_highlight = request.form.get('genes_highlight')

    fc = float(request.form.get('fc_highlight', 0))

    res = get_plot_series(project_id, aa, selected, fc, genes_highlight, norm)
    p_series = res['p_series']
    a_series = res['a_series']
    e_series = res['e_series']
    all_genes = res['all_genes']

    return render_template('psite_dotplot.html', amino_acids=amino_acids, contrasts=contrasts, selected_aa=aa,
                           selected_contrasts=selected, p_series=p_series, a_series=a_series, e_series=e_series,
                           norm=norm, fc_highlight=fc, genes_highlight=genes_highlight, all_genes=all_genes)


@psite_dotplot.route('/psite_dotplot/<project_id>/search_genes', methods=['POST'])
@login_required
def search_genes(project_id):
    data = request.get_json()
    res = get_plot_series(project_id, data['selected_aa'], data['selected_contrasts'], float(data['fc_highlight']),
                          data['genes_highlight'], data['norm'], data['search_genes'])
    p_series = res['p_series']
    a_series = res['a_series']
    e_series = res['e_series']
    return make_response({'status': 'success', 'p_series': p_series, 'a_series': a_series, 'e_series': e_series}, 200)
