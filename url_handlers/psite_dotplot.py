from flask import Blueprint, render_template, request, make_response, current_app
from flask_login import login_required, current_user
import json
import pandas as pd
import numpy as np


psite_dotplot = Blueprint('psite_dotplot', __name__)


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
    if aa is None:
        return render_template('psite_dotplot.html', error='Please select amino acid', contrasts=contrasts, amino_acids=amino_acids)

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

    norm = request.form.get('norm', 'tpm')

    p_series = {}
    a_series = {}
    e_series = {}
    for c in selected:
        sample, control = c.split('__vs__')
        sample = '{}_{}'.format(norm, sample)
        control = '{}_{}'.format(norm, control)

        # psite
        p_df = psite[['gene', 'Aa', 'codon', sample, control]]
        p_df = p_df.dropna()
        p_df = p_df.groupby(['gene']).agg({sample: 'sum', control: 'sum'}).reset_index()
        p_df['x'] = np.log2(p_df[sample]).round(3)
        p_df['y'] = np.log2(p_df[control]).round(3)
        p_df[sample] = p_df[sample].round(3)
        p_df[control] = p_df[control].round(3)
        p_series[c] = {'name': c, 'data': p_df.to_dict('records'), 'turboThreshold': len(p_df)}

        # asite
        a_df = asite[['gene', 'Aa', 'codon', sample, control]]
        a_df = a_df.dropna()
        a_df['x'] = np.log2(a_df[sample]).round(3)
        a_df['y'] = np.log2(a_df[control]).round(3)
        a_df[sample] = a_df[sample].round(3)
        a_df[control] = a_df[control].round(3)
        a_series[c] = {'name': c, 'data': a_df.to_dict('records'), 'turboThreshold': len(a_df)}

        # esite
        e_df = esite[['gene', 'Aa', 'codon', sample, control]]
        e_df = e_df.dropna()
        e_df['x'] = np.log2(e_df[sample]).round(3)
        e_df['y'] = np.log2(e_df[control]).round(3)
        e_df[sample] = e_df[sample].round(3)
        e_df[control] = e_df[control].round(3)
        e_series[c] = {'name': c, 'data': e_df.to_dict('records'), 'turboThreshold': len(e_df)}

    return render_template('psite_dotplot.html', amino_acids=amino_acids, contrasts=contrasts, selected_aa=aa,
                           selected_contrasts=selected, p_series=p_series, a_series=a_series, e_series=e_series,
                           norm=norm)
