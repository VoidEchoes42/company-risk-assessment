import pandas as pd
import re

# 1. Load the file from your processed data folder
df = pd.read_csv('data/processed/business_summaries.csv')

# Temporarily store the old classification to track changes
if 'classification' in df.columns:
    df['old_classification'] = df['classification'].fillna('NONE')
else:
    df['old_classification'] = 'NONE'


def classify_row(row):
    text = str(row['summary_snippet']).lower()
    name = str(row['company_name']).lower()

    # Map for missing, boilerplate, or manually reviewed S-1 summaries
    overrides = {
        # --- NEW MANUAL OVERRIDES FROM IMAGES ---
        'spero therapeutics': 'THERAPEUTICS',
        'biocardia': 'THERAPEUTICS',
        'ovascience': 'THERAPEUTICS',
        'scpharmaceuticals': 'THERAPEUTICS',
        'pds biotechnology': 'THERAPEUTICS',
        'cempra': 'THERAPEUTICS',
        'contrafect': 'THERAPEUTICS',
        'kythera biopharmaceuticals': 'THERAPEUTICS',
        'ruthigen': 'THERAPEUTICS',
        'adaptive biotechnologies': 'DIAGNOSTICS',
        'jaguar animal health': 'SERVICES',
        'gelesis': 'DEVICES',
        'replimune': 'THERAPEUTICS',
        'cabaletta bio': 'THERAPEUTICS',
        'precision biosciences': 'THERAPEUTICS',
        'tff pharmaceuticals': 'THERAPEUTICS',
        'kaleido biosciences': 'THERAPEUTICS',
        'tesaro': 'THERAPEUTICS',
        'hemispherx biopharma': 'THERAPEUTICS',

        # --- PREVIOUS OVERRIDES ---
        'verastem inc': 'THERAPEUTICS', 'liquidia technologies inc': 'THERAPEUTICS',
        'entera bio ltd': 'THERAPEUTICS', 'genprex': 'THERAPEUTICS',
        'evolus inc': 'THERAPEUTICS', 'sol-gel technologies ltd': 'THERAPEUTICS',
        'inflarx nv': 'THERAPEUTICS', 'biontech se': 'THERAPEUTICS',
        'inmune bio inc': 'THERAPEUTICS', 'china sxt pharms inc': 'THERAPEUTICS',
        'moderna inc': 'THERAPEUTICS', 'nucana plc': 'THERAPEUTICS',
        'zai lab ltd': 'THERAPEUTICS', 'uniqure bv': 'THERAPEUTICS',
        'ardelyx inc': 'THERAPEUTICS', 'zoetis inc': 'THERAPEUTICS',
        'atossa genetics inc': 'THERAPEUTICS', 'zymeworks inc': 'THERAPEUTICS',
        'beyondspring inc': 'THERAPEUTICS', 'ac immune sa': 'THERAPEUTICS',
        'moleculin biotech inc': 'THERAPEUTICS', 'dandrit biotech usa, inc.': 'THERAPEUTICS',
        'lipocine inc.': 'THERAPEUTICS', 'stellar biotechnologies, inc.': 'THERAPEUTICS',
        'oncolix, inc.': 'THERAPEUTICS', 'antriabio, inc.': 'THERAPEUTICS',
        'cardax, inc.': 'THERAPEUTICS', 'neurotrope, inc.': 'THERAPEUTICS',
        'ignyta, inc.': 'THERAPEUTICS', 'cel sci corp': 'THERAPEUTICS',
        'advaxis, inc.': 'THERAPEUTICS', 'retrophin, inc.': 'THERAPEUTICS',
        'catalent, inc.': 'CRO', 'axcella health inc.': 'THERAPEUTICS',
        'puma biotechnology, inc.': 'THERAPEUTICS', 'beigene, ltd.': 'THERAPEUTICS',
        'adgero biopharmaceuticals': 'THERAPEUTICS', 'hoverink biotechnologies, inc.': 'THERAPEUTICS',
        'tyme technologies, inc.': 'THERAPEUTICS', 'biomx inc.': 'THERAPEUTICS',
        'alkermes plc.': 'THERAPEUTICS', 'cell source, inc.': 'THERAPEUTICS',
        'kannalife inc': 'THERAPEUTICS', 'enumeral biomedical holdings': 'THERAPEUTICS',
        'fibrogen inc': 'THERAPEUTICS', 'microlin bio, inc.': 'THERAPEUTICS',
        'cerecor inc.': 'THERAPEUTICS', 'angion biomedica corp.': 'THERAPEUTICS',
        'bluebird bio, inc.': 'THERAPEUTICS', 'abbvie inc.': 'THERAPEUTICS',
        'unity biotechnology, inc.': 'THERAPEUTICS', 'vaccinogen inc': 'THERAPEUTICS',
        'avedro inc': 'DEVICES', 'phaserx, inc.': 'THERAPEUTICS',
        'vital therapies inc': 'THERAPEUTICS', 'chimerix inc': 'THERAPEUTICS',
        'green meadow products, inc.': 'SERVICES', 'health-right discoveries, inc.': 'THERAPEUTICS',
        'dynamic nutra enterprises': 'THERAPEUTICS', 'global green inc.': 'UNCLEAR',
        'bio essence corp': 'SERVICES', 'xstelos holdings, inc.': 'UNCLEAR',
        'biolabmart inc.': 'TOOLS', 'premier biomedical inc': 'THERAPEUTICS',
        'earth science tech, inc.': 'THERAPEUTICS', 'gridiron bionutrients, inc.': 'THERAPEUTICS',
        'oxygen therapy, inc.': 'DEVICES', 'sunset island group': 'THERAPEUTICS',
        'cellular dynamics international': 'TOOLS', 'solid biosciences': 'THERAPEUTICS'
    }

    # Check overrides first (using substring match for robustness)
    for key in overrides:
        if key in name:
            return overrides[key]

    # Combine text for keyword scoring
    combined_text = text + " " + name + " " + name

    keywords = {
        'THERAPEUTICS': ['therapeutics', 'pharma', 'pharmaceutical', 'drug discovery', 'clinical stage',
                         'biopharmaceutical', 'gene therapy', 'vaccine', 'medicines', 'oncology', 'clinical programs',
                         'antibody', 'small molecule', 'protein therapeutics', 'bioscience', 'biopharma'],
        'DEVICES': ['medical device', 'medical equipment', 'surgical', 'implant', 'wearable', 'catheter', 'stent',
                    'orthopedic', 'aesthetics', 'neurostimulation'],
        'DIAGNOSTICS': ['diagnostics', 'diagnostic', 'biomarker', 'assay', 'in vitro diagnostic', 'screening test',
                        'detection', 'blood test'],
        'CRO': ['contract research', 'cro', 'clinical trial management', 'contract manufacturing', 'cdmo', 'cmo'],
        'TOOLS': ['life science tools', 'research tools', 'reagents', 'sequencing platform', 'laboratory equipment',
                  'instrumentation', 'analytical instrument', 'spectrometry', 'microscopy', 'cell culture media',
                  'genomics platform'],
        'SERVICES': ['animal health', 'healthcare services', 'digital health', 'telemedicine', 'software',
                     'platform as a service', 'laboratory services', 'healthcare provider', 'clinic', 'hospital',
                     'care network']
    }

    # Score each category based on keyword occurrences
    scores = {category: sum(len(re.findall(r'\b' + kw + r'\b', combined_text)) for kw in kws)
              for category, kws in keywords.items()}

    max_score = max(scores.values())
    if max_score == 0:
        return 'UNCLEAR'

    return max(scores, key=scores.get)


# 2. Apply classification to the dataframe
df['classification'] = df.apply(classify_row, axis=1)

# 3. Print out the changes to the terminal
print("\n" + "=" * 50)
print("CLASSIFICATION CHANGES DETECTED")
print("=" * 50)

# Filter for rows where the new classification doesn't match the old one
changes = df[df['classification'] != df['old_classification']]
if not changes.empty:
    for index, row in changes.iterrows():
        old_val = row['old_classification'] if row['old_classification'] != 'NONE' else 'Blank/NaN'
        print(f"[{row['company_name']}]")
        print(f"   Changed: {old_val}  -->  {row['classification']}\n")
    print(f"Total rows modified: {len(changes)}")
else:
    print("No changes were made. All rows already match the target classifications.")

print("=" * 50 + "\n")

# 4. Clean up the temporary tracking column and save the rewritten file
df = df.drop(columns=['old_classification'])
output_path = 'data/processed/business_summaries_updated.csv'
df.to_csv(output_path, index=False)

print(f"File successfully saved to: {output_path}")