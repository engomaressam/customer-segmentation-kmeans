"""Build the unsupervised-learning final project report (.docx) from the notebook results; export_pdf.ps1 makes the PDF.

usage: python build_report.py
"""
from pathlib import Path

import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH

from docx_helpers import (DARK_BLUE, MUTED, NAVY, SECONDARY, bullets, callout, figure, footer, heading, new_document,
                          page_break, para, stat_row, table, table_of_contents)

SOURCE = Path(__file__).resolve().parent
PROJECT = SOURCE.parent
RESULTS, FIGURES = PROJECT / "results", PROJECT / "figures"
OUTPUT = PROJECT / "Unsupervised ML - Final Project Report.docx"

AUTHOR = "Omar Essam"
DATE = "October 24, 2026"
L, R, C = WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.CENTER

ACTIONS = {
    "Fiber newcomers": "Priority retention: move them to 12- or 24-month contracts early, bundle tech support and security into fiber plans, switch electronic-check payers to autopay, and fix fiber quality issues.",
    "Budget newcomers": "Low-cost onboarding: a first-year welcome journey, entry-level bundles and digital nudges towards longer contracts.",
    "Premium fiber loyalists": "Protect the most valuable base: loyalty rewards, proactive service-quality monitoring and contract renewals before expiry.",
    "Loyal DSL bundlers": "Grow carefully: fiber upgrade offers that keep their protection bundle and contract; avoid disrupting a loyal group.",
    "Phone-only veterans": "Low touch: cross-sell internet to a stable base; little retention spend is needed.",
}


def csv(name):
    return pd.read_csv(RESULTS / name)


def pct(x, digits=0):
    return f"{x:.{digits}%}"


def main():
    summary = csv("summary.csv").set_index("metric")["value"]
    comp = csv("model_comparison.csv").set_index("model")
    prof = csv("segment_profiles.csv")
    ksel = csv("k_selection.csv")
    sup = csv("supervised_by_segment.csv").set_index("approach")
    load = csv("pca_behaviour_loadings.csv").set_index("feature")
    K = int(summary["k"])
    best = comp.loc["K-means, engineered features"]
    raw = comp.loc["K-means, raw features via PCA"]
    ward = comp.loc["Hierarchical (Ward), engineered features"]
    gmm = comp.loc["Gaussian mixture, engineered features"]
    dbs = comp.loc["DBSCAN, engineered features"]
    seg = prof.set_index("name")
    top = prof.iloc[0]  # highest churn
    eng = ksel[ksel["features"] == "Engineered (6)"].set_index("k")
    churn_rate = summary["churn_rate"]

    doc = new_document()

    # ------------------------------------------------------------------ cover
    para(doc, [("IBM Machine Learning Professional Certificate  |  Unsupervised Machine Learning - Final Project", {"color": MUTED, "size": 9.5})], after=60)
    para(doc, [("Customer Segmentation", {"bold": True, "color": NAVY, "size": 30})], after=2)
    para(doc, [("Five customer segments that show where churn and revenue risk sit", {"color": DARK_BLUE, "size": 15})], after=18)
    para(doc, [("A stakeholder report that compares five unsupervised learning variations - clustering algorithms, feature sets and "
                "PCA-based dimensionality reduction - on IBM's Telco Customer Churn data, recommends one segmentation and turns it into "
                "segment-specific actions.", {"color": SECONDARY, "size": 11})], after=26)
    stat_row(doc, [(f"{K}", f"customer segments, stable across resamples (adjusted Rand index {best['stability_ari']:.2f})"),
                   (pct(top["churned_revenue_share"]), f"of the revenue lost to churn comes from one segment holding {pct(top['share'])} of customers"),
                   (f"{best['churn_min']:.0%}-{best['churn_max']:.0%}", "churn rate range across segments, although churn was not used to build them")])
    para(doc, "", after=30)
    table(doc, [["Prepared for", "Chief Data Officer and Head of Analytics"],
                ["Prepared by", f"{AUTHOR}, Data Scientist"],
                ["Date", DATE],
                ["Analysis behind this report", "Final Project/Unsupervised ML - Customer Segmentation.ipynb"]],
          [4.4, 12.2], header=False, size=10, bold_first_col=True)
    page_break(doc)

    # ------------------------------------------------------------------ contents + executive summary
    para(doc, [("Contents", {"bold": True, "color": NAVY, "size": 15})], after=4)
    table_of_contents(doc)
    heading(doc, "Executive summary", 1)
    para(doc, f"The {int(summary['customers']):,} customers of the provider were grouped by how they behave - how long they have stayed, how committed "
              f"they are, what they buy and what they pay - using clustering. Five model variations were compared; K-means with {K} clusters on six "
              "engineered behavioural features gives the clearest, most stable and most actionable segmentation.")
    para(doc, [("Key insights", {"bold": True, "color": DARK_BLUE})], after=2, keep_next=True)
    names = list(prof["name"])
    bullets(doc, [
        [(f"{top['name']} are the problem segment. ", {"bold": True}),
         (f"{pct(top['share'])} of customers, but {pct(top['Churn'])} of them churn and they account for {pct(top['churned_revenue_share'])} of the "
          f"monthly revenue lost to churn: new ({top['tenure']:.0f} months on average), almost all month-to-month, fiber, ${top['MonthlyCharges']:.0f} a month "
          f"with few protection add-ons, and {pct(top['ElectronicCheck'])} pay by electronic check.", {})],
        [("Commitment and bundles separate loyal from at-risk customers. ", {"bold": True}),
         (f"The three long-tenure segments ({', '.join(names[2:])}) churn at {pct(prof['Churn'].iloc[2:].min())}-{pct(prof['Churn'].iloc[2:].max())} "
          "and carry multi-year contracts or rich service bundles.", {})],
        [("Not all newcomers are equal. ", {"bold": True}),
         (f"{names[1]} are just as new ({seg.loc[names[1], 'tenure']:.0f} months) but spend less (${seg.loc[names[1], 'MonthlyCharges']:.0f}) and churn at "
          f"{pct(seg.loc[names[1], 'Churn'])}, half the rate of {top['name']} - their risk is cheaper to manage.", {})],
        [("The most valuable customers are not the riskiest. ", {"bold": True}),
         (f"Premium fiber loyalists pay the most (${seg.loc['Premium fiber loyalists', 'MonthlyCharges']:.0f}) and bring "
          f"{pct(seg.loc['Premium fiber loyalists', 'revenue_share'])} of revenue with {pct(seg.loc['Premium fiber loyalists', 'Churn'])} churn.", {})],
        [("Segments guide strategy, not prediction. ", {"bold": True}),
         (f"Churn models trained per segment do not beat one global model (test ROC AUC {sup.loc['Separate model per segment', 'test_auc']:.3f} vs "
          f"{sup.loc['One global model', 'test_auc']:.3f}); the value of the segmentation lies in targeting and communication.", {})],
    ])
    callout(doc, "Recommendation", [
        [("Adopt the K-means segmentation (k = 5) on the six behavioural features ", {"bold": True}),
         (f"- best on every quality metric (silhouette {best['silhouette']:.2f}, Davies-Bouldin {best['davies_bouldin']:.2f}), stable (adjusted Rand "
          f"index {best['stability_ari']:.2f}), simple to explain through segment averages and easy to apply to new customers.", {})],
        [("Run one playbook per segment: ", {"bold": True}),
         (f"concentrate retention budget on {top['name']}, onboard {names[1]} cheaply, protect Premium fiber loyalists, and cross-sell to the "
          "low-churn segments.", {})],
    ])
    page_break(doc)

    # ------------------------------------------------------------------ 1. objective
    heading(doc, "1. Main objective of the analysis", 1)
    para(doc, [("The objective is to segment the customer base with clustering so that marketing, retention and product teams can treat "
                "different kinds of customers differently. ", {"bold": True}),
               ("The analysis focuses on clustering; dimensionality reduction (PCA) supports it, to compress the raw service flags and to map the "
                "segments in two dimensions. The segmentation should group customers who behave alike, be stable enough to use month after month, and "
                "be easy to describe in business language.", {})])
    para(doc, "The benefits for the business are:")
    bullets(doc, [
        [("Focused retention spend: ", {"bold": True}), ("know which group produces most of the churned revenue and act there first.", {})],
        [("Segment-specific offers: ", {"bold": True}), ("onboarding, upgrades, bundles and loyalty rewards matched to each group's needs.", {})],
        [("A shared language: ", {"bold": True}), ("a handful of named segments that finance, marketing and customer care can all track over time.", {})],
        [("Better analytics downstream: ", {"bold": True}), ("segments can be added to dashboards and tested as inputs to predictive models (section 7).", {})],
    ])

    # ------------------------------------------------------------------ 2. data description
    heading(doc, "2. Data description", 1)
    para(doc, [("The data is IBM's ", {}), ("Telco Customer Churn", {"bold": True}),
               (f" sample dataset: one record for each of {int(summary['customers']):,} customers of a fictional telecom provider, with 19 attributes "
                f"and a churn flag ({pct(churn_rate, 1)} of customers left in the last month). It was chosen because customer segmentation is a "
                "common, high-value business question and the same data was used for the churn classification project, so segments and churn "
                "drivers can be compared.", {})])
    table(doc, [
        ["Group", "Attributes", "Type", "Role in this analysis"],
        ["Relationship", "tenure (months, 0-72), Contract (month-to-month, one year, two year)", "Numeric / categorical", "Clustering inputs (contract converted to months)"],
        ["Services", "InternetService (DSL, fiber, none), PhoneService, MultipleLines, 4 protection add-ons, 2 streaming services", "Binary / categorical",
         "Clustering inputs (fiber flag and add-on counts)"],
        ["Charges", "MonthlyCharges, TotalCharges", "Numeric", "MonthlyCharges is a clustering input; TotalCharges is dropped (tenure x monthly)"],
        ["Billing", "PaperlessBilling, PaymentMethod (4 methods)", "Categorical", "Used to describe segments, not to build them"],
        ["Household", "gender, SeniorCitizen, Partner, Dependents", "Binary", "Used to describe segments, not to build them"],
        ["Outcome", "Churn (Yes / No)", "Binary", "Never used to build segments; used to judge their business value"],
    ], [2.6, 6.2, 2.8, 5.0], size=9)
    para(doc, "The analysis aims to find a small number of behaviour-based customer groups that differ clearly in loyalty and value, so that each can "
              "receive its own strategy.")

    # ------------------------------------------------------------------ 3. exploration & preparation
    heading(doc, "3. Data exploration and preparation", 1)
    heading(doc, "Exploration and cleaning", 2)
    figure(doc, FIGURES / "fig1_exploration.png", "Figure 1 - Tenure is U-shaped (many new and many very long-standing customers), monthly charges are "
                                                  "multi-modal, and more than half of the customers are on month-to-month contracts.")
    bullets(doc, [
        f"TotalCharges was stored as text; its {int(summary['blank_total_charges'])} blanks belong to brand-new customers (tenure 0) and were set to 0. There are no duplicates and no other missing values.",
        "The distributions are lumpy rather than bell-shaped - a first sign that the customer base is made of distinct groups.",
        f"Relationship and spend variables are correlated (tenure vs contract length r = {summary['corr_tenure_contract']:.2f}; monthly charges vs fiber r = {summary['corr_charges_fiber']:.2f}), which PCA summarises well.",
    ])
    heading(doc, "Feature engineering: two candidate feature sets", 2)
    table(doc, [
        ["Feature set", "Features", "Why"],
        [f"Raw service profile ({int(summary['raw_feature_count'])})", "tenure, contract months, every internet, phone, add-on, billing, payment and household flag",
         f"Uses all the information; clustered on its first {int(summary['pca_raw_components_80'])} principal components ({pct(summary['pca_raw_variance_80'])} of the variance)"],
        [f"Engineered behaviour ({int(summary['behaviour_feature_count'])})", "tenure, contract months, monthly charges, number of protection add-ons, number of streaming services, fiber flag",
         "Summarises the relationship, spend and bundle depth; keeps demographics and billing out so they can describe the segments afterwards"],
    ], [3.6, 6.6, 6.4], size=9)
    bullets(doc, [
        "Contract type was converted to months (0, 12, 24) and the six add-ons were condensed into two counts, so that dozens of yes/no flags do not dominate the distances.",
        "All features were standardised (mean 0, standard deviation 1) so that tenure in months and charges in dollars count equally.",
        [("Dimensionality reduction: ", {"bold": True}),
         (f"on the 18 raw features the first principal component explains only {pct(csv('pca_raw_variance.csv')['raw_variance'].iloc[0])} of the variance and "
          f"{int(summary['pca_raw_components_80'])} components are needed for 80%. On the 6 behavioural features two components explain "
          f"{pct(summary['pca_beh_pc1'] + summary['pca_beh_pc2'])}: PC1 ({pct(summary['pca_beh_pc1'])}) is spend and bundle depth "
          f"(loadings: charges {load.loc['MonthlyCharges', 'PC1']:.2f}, streaming {load.loc['StreamingServices', 'PC1']:.2f}, protection "
          f"{load.loc['ProtectionServices', 'PC1']:.2f}) and PC2 ({pct(summary['pca_beh_pc2'])}) is commitment (contract {load.loc['ContractMonths', 'PC2']:.2f}, "
          f"tenure {load.loc['tenure', 'PC2']:.2f} against fiber {load.loc['Fiber', 'PC2']:.2f}).", {})],
    ])

    # ------------------------------------------------------------------ 4. model variations
    heading(doc, "4. Model variations", 1)
    heading(doc, "4.1 How the variations are compared", 2)
    bullets(doc, [
        [("Separation: ", {"bold": True}), ("silhouette score (from -1 to 1, higher means customers sit closer to their own segment than to the next one), Davies-Bouldin index (lower is better) and Calinski-Harabasz index (higher is better).", {})],
        [("Usability: ", {"bold": True}), ("size of the smallest segment (tiny segments cannot carry a campaign) and stability - the adjusted Rand index between the full fit and fits on 10 random 80% subsamples.", {})],
        [("Business value: ", {"bold": True}), ("how far apart the segments' churn rates are. Churn is not an input, so a wide range means the segments capture behaviour that matters.", {})],
    ])
    heading(doc, "4.2 Choosing the number of segments", 2)
    figure(doc, FIGURES / "fig2_choose_k.png", "Figure 2 - Elbow curve and silhouette scores for K-means with 2 to 8 clusters. The engineered features separate "
                                               "customers about twice as well as the raw flags at every k.")
    para(doc, f"The silhouette score of the engineered features plateaus at about {eng.loc[3, 'silhouette']:.2f}-{eng['silhouette'].max():.2f} from k = 3; "
              f"k = {K} is the smallest number of clusters within 0.005 of the best score ({eng.loc[K, 'silhouette']:.3f}) and sits where the elbow "
              f"flattens. More clusters mostly split existing segments without separating customers better, so {K} segments were used for every "
              "algorithm.")
    heading(doc, "4.3 Five variations compared", 2)
    rows = [["Variation", "Silhouette", "Davies-Bouldin", "Calinski-Harabasz", "Smallest segment", "Stability (ARI)", "Churn range"]]
    for name, r in comp.iterrows():
        label = f"{name} ({int(r['clusters'])} clusters, {pct(r['noise_share'], 1)} noise)" if name.startswith("DBSCAN") else name
        rows.append([label, f"{r['silhouette']:.3f}", f"{r['davies_bouldin']:.2f}", f"{r['calinski_harabasz']:,.0f}", pct(r["smallest_share"], 1),
                     "-" if pd.isna(r["stability_ari"]) else f"{r['stability_ari']:.2f}", f"{r['churn_min']:.0%}-{r['churn_max']:.0%}"])
    table(doc, rows, [5.2, 1.7, 1.9, 2.0, 2.0, 1.9, 1.9], aligns=[L, R, R, R, R, R, R], size=8.5,
          highlight_rows=(list(comp.index).index("K-means, engineered features") + 1,))
    figure(doc, FIGURES / "fig4_model_comparison.png", "Figure 3 - Silhouette and Davies-Bouldin scores of the five variations; the recommended variation is highlighted.")
    bullets(doc, [
        [("K-means on the raw flags (via PCA) ", {"bold": True}), (f"separates customers poorly (silhouette {raw['silhouette']:.2f}): many binary columns add noise to the distances.", {})],
        [("K-means on the engineered features ", {"bold": True}), (f"is best on all three quality scores, has balanced segments (smallest {pct(best['smallest_share'])}) and is almost perfectly stable ({best['stability_ari']:.2f}).", {})],
        [("Hierarchical clustering (Ward) ", {"bold": True}), (f"finds a similar structure (silhouette {ward['silhouette']:.2f}) and its dendrogram confirms {K} natural groups, but it is less stable ({ward['stability_ari']:.2f}) and cannot assign new customers without refitting.", {})],
        [("Gaussian mixture ", {"bold": True}), (f"gives soft memberships but overlapping, less separated segments (silhouette {gmm['silhouette']:.2f}).", {})],
        [("DBSCAN ", {"bold": True}), (f"breaks the customers into {int(dbs['clusters'])} density pockets, the smallest holding {pct(dbs['smallest_share'], 1)} of customers: the features take few distinct values, so density-based clusters follow artefacts rather than segments.", {})],
    ])
    figure(doc, FIGURES / "fig3_dendrogram.png", f"Figure 4 - Ward dendrogram (last 30 merges). The long vertical lines above the cut show that {K} groups are "
                                                 "well separated; merging further would join very different customers.", width_cm=15.5)

    # ------------------------------------------------------------------ 5. recommendation
    heading(doc, "5. Final model recommendation", 1)
    para(doc, [(f"Recommended: K-means with k = {K} on the six engineered behavioural features. ", {"bold": True}),
               ("It best fits the objective of a stable, explainable and actionable segmentation:", {})])
    bullets(doc, [
        [("Best separation: ", {"bold": True}), (f"silhouette {best['silhouette']:.2f}, Davies-Bouldin {best['davies_bouldin']:.2f} and Calinski-Harabasz {best['calinski_harabasz']:,.0f} - the best values of the five variations.", {})],
        [("Stable: ", {"bold": True}), (f"refitting on random 80% samples reproduces the same segments (adjusted Rand index {best['stability_ari']:.2f}), so the segments can be tracked over time.", {})],
        [("Interpretable: ", {"bold": True}), ("each segment is described by its average customer on six business-friendly features, which makes naming and communicating the segments easy.", {})],
        [("Actionable and deployable: ", {"bold": True}), (f"segment churn rates range from {best['churn_min']:.0%} to {best['churn_max']:.0%}, and new customers are assigned to the nearest centroid with a single calculation.", {})],
    ])

    # ------------------------------------------------------------------ 6. findings
    heading(doc, "6. Key findings and insights", 1)
    figure(doc, FIGURES / "fig5_segment_profiles.png", "Figure 5 - Average customer of each segment (segment share of customers in brackets). Colours compare each "
                                                       "value with the customer average; churn rate and billing were not used to build the segments.")
    rows = [["Segment", "Customers", "Churn", "Revenue", "Lost revenue", "Recommended action"]]
    for r in prof.itertuples():
        rows.append([[(r.name, {"bold": True})], pct(r.share), pct(r.Churn), pct(r.revenue_share), pct(r.churned_revenue_share), ACTIONS[r.name]])
    table(doc, rows, [3.4, 1.7, 1.4, 1.6, 1.8, 6.7], aligns=[L, R, R, R, R, L], size=8.5, highlight_rows=(1,))
    para(doc, [("Revenue", {"italic": True}), (" = share of all monthly charges; ", {"color": SECONDARY}), ("Lost revenue", {"italic": True}),
               (" = share of the monthly charges of customers who churned.", {"color": SECONDARY})], size=9)
    bullets(doc, [
        [(f"{top['name']} drive the churn problem: ", {"bold": True}),
         (f"{pct(top['share'])} of customers, {pct(top['Churn'])} churn, {pct(top['churned_revenue_share'])} of lost revenue. They sit on the low-commitment, "
          "high-spend side of the segment map (Figure 6). Retention money spent anywhere else has far less impact.", {})],
        [("Commitment is the dividing line: ", {"bold": True}),
         (f"the two month-to-month newcomer segments churn at {pct(prof['Churn'].iloc[1])} and {pct(prof['Churn'].iloc[0])}, the three committed, "
          f"long-tenure segments at {pct(prof['Churn'].iloc[2:].min())}-{pct(prof['Churn'].iloc[2:].max())} - even the highest-paying one - which supports "
          "contract-conversion offers as the main lever.", {})],
        [("Bundles signal loyalty: ", {"bold": True}),
         (f"Loyal DSL bundlers average {seg.loc['Loyal DSL bundlers', 'ProtectionServices']:.1f} protection add-ons and churn at {pct(seg.loc['Loyal DSL bundlers', 'Churn'])}, "
          f"against {top['ProtectionServices']:.1f} add-ons for {top['name']}.", {})],
        [("Segments line up with the churn drivers found in the classification project ", {"bold": True}),
         ("(contract, tenure, fiber, add-ons, electronic check), which gives the business one consistent story across both analyses.", {})],
    ])
    figure(doc, FIGURES / "fig6_segments_map_revenue.png", "Figure 6 - The segments on the first two principal components (left) and each segment's share of "
                                                            "customers versus its share of the revenue lost to churn (right).")

    # ------------------------------------------------------------------ 7. optional supervised
    heading(doc, "7. Do segment-specific churn models beat one global model?", 1)
    para(doc, "As an optional check, the churn model from the classification project (L2 logistic regression) was trained three ways on the same "
              "80/20 split, with the segmentation refitted on the training customers only:")
    rows = [["Approach", "Test ROC AUC", "95% interval"]]
    for name, r in sup.iterrows():
        rows.append([name, f"{r['test_auc']:.3f}", f"{r['ci_low']:.3f}-{r['ci_high']:.3f}"])
    table(doc, rows, [8.0, 3.2, 3.6], aligns=[L, R, R], size=9.5)
    para(doc, f"Separate models per segment perform the same as one global model (difference in ROC AUC between {sup.loc['Separate model per segment', 'delta_vs_global_ci']}, "
              "95% bootstrap interval) and adding the segment as a feature changes almost nothing. The segments are built from the same information the "
              "global model already uses, and splitting the data leaves less to train on in each segment. The conclusion: use the segments for strategy "
              "and targeting, and keep a single, simpler global model for individual churn scores.")

    # ------------------------------------------------------------------ 8. limitations
    heading(doc, "8. Limitations of the model", 1)
    bullets(doc, [
        [("Moderate separation: ", {"bold": True}), (f"a silhouette of {best['silhouette']:.2f} means segments touch at their borders; customers near a boundary could reasonably belong to either side, so assignments should be reviewed rather than treated as exact.", {})],
        [("K-means assumptions: ", {"bold": True}), ("it favours round clusters of similar spread and needs k chosen in advance; segments with other shapes are approximated.", {})],
        [("Feature choices drive the result: ", {"bold": True}), ("the six engineered features reflect a business view of behaviour; a different selection (for example usage data) would produce different segments.", {})],
        [("A snapshot of sample data: ", {"bold": True}), (f"{int(summary['customers']):,} fictional customers at one point in time; segments must be validated on real, current data and their movement over time is unknown.", {})],
        [("Descriptive, not causal: ", {"bold": True}), ("segments show where churn concentrates, not what will reduce it; actions must be tested before scaling.", {})],
    ])

    # ------------------------------------------------------------------ 9. next steps
    heading(doc, "9. Next steps", 1)
    bullets(doc, [
        [("Add data: ", {"bold": True}), ("usage trends, customer-care contacts, network quality and survey scores, to explain why Fiber newcomers leave and to sharpen the segment borders.", {})],
        [("Refine the features and model: ", {"bold": True}), ("test K-prototypes or Gower-distance clustering for mixed categorical data, and Gaussian mixture memberships to flag customers between segments.", {})],
        [("Track segments over time: ", {"bold": True}), ("re-score customers monthly, monitor migration between segments (for example newcomers becoming loyalists) and alert on drift.", {})],
        [("Test the playbooks: ", {"bold": True}), ("run controlled experiments of the recommended action for each segment and measure churn and revenue against a control group.", {})],
        [("Combine with prediction: ", {"bold": True}), ("use the global churn score inside each segment to rank customers for outreach, and survival analysis to time interventions.", {})],
    ])

    # ------------------------------------------------------------------ appendix
    heading(doc, "Appendix: method and reproducibility", 1).paragraph_format.page_break_before = True
    table(doc, [
        ["Variation", "Settings"],
        ["K-means, raw features via PCA", f"18 standardised features, {int(summary['pca_raw_components_80'])} principal components, k = {K}, 10 initialisations"],
        ["K-means, engineered features", f"6 standardised features, k = {K}, 10 initialisations"],
        ["Hierarchical (Ward)", f"Ward linkage on the 6 standardised features, cut at {K} clusters"],
        ["Gaussian mixture", f"{K} components, full covariance, 3 initialisations"],
        ["DBSCAN", f"eps = {summary['dbscan_eps']:.2f} (95th percentile of the 12-nearest-neighbour distance), min_samples = 12"],
    ], [5.0, 11.6], size=9.5, bold_first_col=True)
    bullets(doc, [
        "Data: IBM Telco Customer Churn sample (github.com/IBM/telco-customer-churn-on-icp4d), stored in Final Project/data.",
        "Analysis: Final Project/Unsupervised ML - Customer Segmentation.ipynb - every table and figure in this report is produced there and saved to the results and figures folders.",
        "Environment: Python 3.11, pandas 2.2, scikit-learn 1.5, SciPy 1.13, matplotlib 3.9; random seed 123.",
        "This report: Final Project/source/build_report.py builds it from the saved results; export_pdf.ps1 updates the contents and saves the PDF with Microsoft Word.",
    ])

    footer(doc, "Customer Segmentation - Unsupervised ML final project")
    doc.core_properties.author = AUTHOR
    doc.core_properties.title = "Customer Segmentation - Unsupervised Machine Learning Final Project"
    doc.save(OUTPUT)
    print("saved", OUTPUT)


if __name__ == "__main__":
    main()
