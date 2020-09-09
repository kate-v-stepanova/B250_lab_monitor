import pandas as pd
import math
from flask import Blueprint, render_template, request
from flask_login import login_required
import json

volcano_plot = Blueprint('volcano_plot', __name__)

# yeah, it's better to put it in DB, but ...
asp_top200 = ['PTGES3', 'SPP1', 'ANP32B', 'CALU', 'LEO1', 'C11orf58', 'CALR', 'ANP32A', 'ANAPC13', 'NUCKS1', 'HTATSF1', 'HSBP1', 'EIF3J', 'NPM1', 'RCN1', 'PTMA', 'CAMK2N1', 'CALM3', 'RCN2', 'CANX', 'CALM1', 'MYL12A', 'PGRMC1', 'THBS1', 'EEF1B2', 'SET', 'MYL12B', 'RCN3', 'CHMP5', 'UBE2R2', 'IWS1', 'NAP1L1', 'LSM7', 'CLNS1A', 'MYL9', 'CDC123', 'AHNAK', 'THBS2', 'COPRS', 'NCL', 'EIF3A', 'HNRNPC', 'ADI1', 'PPP3R1', 'PWP1', 'TSR2', 'EIF2S2', 'ABRACL', 'PPIL4', 'GLO1', 'HAX1', 'MPHOSPH10', 'LTV1', 'POLR2H', 'PPA1', 'SNRNP70', 'FIBP', 'HPRT1', 'PHPT1', 'URI1', 'RPLP2', 'WDR61', 'UBL5', 'TAF7', 'RGCC', 'PAF1', 'PDCD6', 'IFT43', 'ARL2BP', 'CAPZB', 'ANXA3', 'MTPN', 'IK', 'CBX1', 'ZC3H15', 'EAPP', 'PKIG', 'SAFB', 'EIF1', 'SPRED1', 'C14orf166', 'TCEAL3', 'MESDC2', 'ZBTB7A', 'CDC34', 'TXNDC9', 'GNB4', 'GNB1', 'GNB2', 'ATP6V1F', 'CD2BP2', 'NCAPH', 'PFDN4', 'RAD21', 'POLR2C', 'ANXA4', 'CBX3', 'CNST', 'CCDC47', 'TSSC1', 'CHP1', 'ANXA2', 'CDH11', 'LRP1', 'GPN3', 'RAB3B', 'DPF2', 'ERP44', 'YWHAE', 'SUB1', 'SNX6', 'CAST', 'SRSF9', 'LRP5', 'ATF4', 'LRP8', 'PDIA4', 'ANXA6', 'EPS15L1', 'DRAP1', 'P4HB', 'GADD45A', 'EFTUD2', 'NRAS', 'METTL22', 'TXNL4A', 'ARPC5', 'CFL2', 'RNF13', 'OSTF1', 'SPIN1', 'CTDSP1', 'SUMO2', 'NUCB2', 'ASCC2', 'ITGBL1', 'NDUFAB1', 'NCBP2', 'WDR82', 'NAP1L4', 'SRSF1', 'SDF4', 'WARS', 'GRB2', 'USP7', 'HPCAL1', 'CEBPZ', 'CASC4', 'AAGAB', 'PPM1G', 'AHNAK2', 'FABP3', 'SELRC1', 'CIB1', 'HDGFRP2', 'WDR73', 'POLR2F', 'SMS', 'MMP2', 'SUPT6H', 'MCFD2', 'INO80E', 'MAGOH', 'S100A10', 'CDH2', 'USP15', 'GNAI2', 'METAP2', 'NFKBIB', 'RHOB', 'CALM2', 'CKB', 'UBA2', 'PPP1R14B', 'HSP90B1', 'PPP2CB', 'PSMC2', 'MAGOHB', 'DENR', 'PRDX2', 'NTMT1', 'AAMP', 'PACSIN2', 'UBE2D3', 'PRDX1', 'PSMD7', 'TAF13', 'PEBP1', 'CAV2', 'HDAC2', 'MCM3', 'TPM1', 'CIAO1', 'RPS25', 'NT5C', 'SDC2', 'RAB9A', 'UTP3', 'SLBP', 'FAM127B']
pro_top200 = ['MAPK1IP1L', 'SF3A2', 'CYSTM1', 'SF1', 'CDIP1', 'COL8A1', 'SNRPC', 'NACA', 'COL10A1', 'CCNK', 'SNRPB', 'COL4A1', 'FAM168B', 'COL3A1', 'ZNF580', 'COL1A1', 'ZNF207', 'TMUB1', 'WBP11', 'COL5A1', 'ZYX', 'COL5A2', 'SHISA5', 'MNT', 'WASL', 'LCE2A', 'KLF2', 'COL13A1', 'COL16A1', 'BRD4', 'C19orf24', 'BCL9L', 'COL1A2', 'COL18A1', 'COL4A2', 'SHISA4', 'FLYWCH2', 'SCAF4', 'DAZAP1', 'WBP2', 'SFPQ', 'HMGA2', 'SSBP4', 'ZFP36', 'ATXN2L', 'RBM42', 'COL11A1', 'PRR16', 'PHLDA1', 'YLPM1', 'SRRM1', 'SS18', 'SLC2A4RG', 'CHCHD10', 'BAG3', 'PRCC', 'ERF', 'MED19', 'MT2A', 'PLEKHB2', 'KHSRP', 'CEBPB', 'SF3A1', 'C4orf48', 'FOSL1', 'C6orf226', 'VASP', 'INO80E', 'MED25', 'SSC5D', 'KMT2D', 'PPP1R35', 'EPN1', 'PELP1', 'COL7A1', 'ZMIZ1', 'HCFC1R1', 'RERE', 'CASC3', 'NAF1', 'LGALS3', 'VPS37B', 'IER5', 'BLVRB', 'PPRC1', 'CDK2AP2', 'HN1L', 'TSC22D4', 'FBLIM1', 'CCDC86', 'NDUFA3', 'ADAMTSL4', 'AKT1S1', 'SERF2', 'CHERP', 'ATXN2', 'RBM12', 'ETV5', 'PHF23', 'CDC42EP1', 'SNAPC2', 'CEBPD', 'TSC22D2', 'HSPB6', 'SHARPIN', 'TICAM1', 'TRNP1', 'SYDE1', 'DKFZP761J1410', 'CRTC2', 'LITAF', 'CARHSP1', 'BAG6', 'BRI3', 'PNRC1', 'TOX2', 'ZNF703', 'ABI1', 'SCAND1', 'KLF5', 'IRS2', 'TMEM261', 'SCAF1', 'SEC16A', 'RELA', 'ERRFI1', 'GRINA', 'NACAD', 'LTBR', 'KHDRBS1', 'APBB1IP', 'MEF2D', 'GORASP2', 'PRR11', 'DAZAP2', 'VEGFB', 'PRRC1', 'TENC1', 'AKIRIN1', 'PTPN23', 'ARID1A', 'MAP7D1', 'TP53I13', 'MRPS18A', 'PSMF1', 'IER5L', 'SAP130', 'FUBP1', 'MANBAL', 'TRIP6', 'MAVS', 'HSPB8', 'C9orf142', 'BCAR1', 'NCOR2', 'SDC3', 'PEG10', 'SYVN1', 'C1orf122', 'EIF4EBP1', 'MKL1', 'FOXE1', 'MED15', 'YBX1', 'CD248', 'PEAR1', 'MAGED1', 'ANXA11', 'RBPMS', 'HOXA10', 'SNRPA', 'CBX6', 'MZT2B', 'ACD', 'TMEM55B', 'BASP1', 'SCARF2', 'URM1', 'SRRM2', 'CPSF7', 'RAB11FIP5', 'PLSCR1', 'SCAF8', 'TFG', 'DPM2', 'AHNAK', 'ANAPC11', 'SF3B2', 'DAG1', 'CSTF2T', 'RAVER1', 'IRF3', 'ARHGAP17', 'NPDC1', 'UBALD2', 'HMGN2', 'ATF6B', 'KLF10', 'PPDPF', 'IRF2BPL']

@volcano_plot.route('/volcano_plot/<project_id>', methods=['GET', 'POST'])
@login_required
def get_volcano_plot(project_id):
    from main import get_db
    rdb = get_db()
    contrasts = rdb.smembers('contrasts_{}'.format(project_id))
    contrasts = sorted([c.decode('utf-8') for c in contrasts])
    if request.method == 'GET':
        return render_template("volcano_plot.html", contrasts=contrasts)

    #  dash lines
    left = float(request.form.get('left'))
    right = float(request.form.get('right'))
    bottom = float(request.form.get('bottom'))

    left_line = round(math.log2(left), 3)
    right_line = round(math.log2(right), 3)
    bottom_line = -round(math.log10(bottom), 3)

    # else: (if request is POST) #
    contrast = request.form.get('contrast')
    if contrast is None:
        return render_template("volcano_plot.html", contrasts=contrasts, error='Contrast is not selected')

    # else: (if contrast is not None) #
    data = rdb.get('volcano_{}_{}'.format(project_id, contrast))
    if data is None:
        return render_template("volcano_plot.html", contrasts=contrasts, error='No data found for contrast: {}'.format(contrast))

    # else: (if data is not None) #
    data = json.loads(data)
    df = pd.DataFrame(data)

    df = df.round(decimals=3)

    df['-log10(pval)'] = -1 * df['pvalue'].apply(lambda x: math.log10(x))

    df['fc'] = 2 ** df['log2FoldChange']
    df = df.drop('padj', axis=1)
    df.columns = ['x', 'pvalue', 'gene', 'y', 'fc']
    df = df.round(decimals=3)

    # thresholds
    asp_df = df.loc[df['gene'].isin(asp_top200)]
    pro_df = df.loc[df['gene'].isin(pro_top200)]

    left_df = df.loc[(df['fc'] <= left) & (df['pvalue'] <= bottom) & ~df['gene'].isin(asp_top200) & ~df['gene'].isin(pro_top200)]
    right_df = df.loc[(df['fc'] >= right) & (df['pvalue'] <= bottom) & ~df['gene'].isin(asp_top200) & ~df['gene'].isin(pro_top200)]
    bottom_df = df[~df.isin(left_df) & ~df.isin(right_df) & ~df.isin(asp_df) & ~df.isin(pro_df)]

    # series
    plot_series = [{
        'name': contrast,
        'data': list(bottom_df.dropna().T.to_dict().values()),
        'turboThreshold': len(bottom_df),
        'marker': {
            'symbol': 'circle',
            'radius': 5,
        },
        'color': 'grey',
    },
        {
            'name': contrast,
            'data': list(left_df.dropna().T.to_dict().values()),
            'turboThreshold': len(left_df),
            'color': 'blue',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            },
        },
        {
            'name': contrast,
            'data': list(right_df.dropna().T.to_dict().values()),
            'turboThreshold': len(right_df),
            'color': 'red',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            },
        },
        {
            'name': 'ASP',
            'data': list(asp_df.dropna().T.to_dict().values()),
            'turboThreshold': len(asp_df),
            'color': '#99ffcc',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            }
        },
        {
            'name': 'PRO',
            'data': list(pro_df.dropna().T.to_dict().values()),
            'turboThreshold': len(pro_df),
            'color': '#ff6699',
            'marker': {
                'symbol': 'circle',
                'radius': 5,
            }

        }
    ]

    return render_template('volcano_plot.html', contrasts=contrasts, selected_contrast=contrast, plot_series=plot_series,
                           right=right_line, left=left_line, bottom=bottom_line, selected_thresholds={
                               'left': left,
                               'right': right,
                               'bottom': bottom,
                           })






