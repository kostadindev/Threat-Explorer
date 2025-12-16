#!/usr/bin/env python3
"""
Statistical Analysis for Threat Explorer Design Experiment
Performs Wilcoxon Signed-Rank Test on paired survey data comparing Text vs Chart versions
With Holm-Bonferroni correction for multiple comparisons
"""

import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def load_survey_data(filepath):
    """Load and parse the survey CSV data."""
    df = pd.read_csv(filepath)
    return df

def extract_dimension_data(df, text_col, chart_col):
    """Extract paired data for a specific dimension."""
    text_scores = df[text_col].values
    chart_scores = df[chart_col].values
    return text_scores, chart_scores

def compute_statistics(text_scores, chart_scores):
    """
    Compute descriptive statistics and Wilcoxon Signed-Rank Test.

    Returns:
        dict with mean_text, mean_chart, difference, p_value
    """
    mean_text = np.mean(text_scores)
    mean_chart = np.mean(chart_scores)
    difference = mean_chart - mean_text

    # Wilcoxon Signed-Rank Test (one-sided: chart > text)
    # We pass chart first, text second, with alternative='greater' to test if chart > text
    # This tests the hypothesis that the distribution underlying chart_scores
    # is stochastically greater than the distribution underlying text_scores
    statistic, p_value = wilcoxon(chart_scores, text_scores, alternative='greater')

    return {
        'mean_text': mean_text,
        'mean_chart': mean_chart,
        'difference': difference,
        'p_value': p_value,
        'statistic': statistic
    }

def holm_bonferroni_correction(p_values, alpha=0.05):
    """
    Apply Holm-Bonferroni correction for multiple comparisons.
    
    Args:
        p_values: list of (index, p_value) tuples
        alpha: family-wise error rate (default 0.05)
    
    Returns:
        dict mapping original index to (adjusted_p, is_significant)
    """
    n = len(p_values)
    
    # Sort p-values in ascending order, keeping track of original indices
    sorted_pvals = sorted(enumerate(p_values), key=lambda x: x[1])
    
    results = {}
    
    # Holm-Bonferroni: compare p[i] to alpha / (n - i)
    # where i is the rank (0-indexed) in sorted order
    rejected_so_far = True  # Once we fail to reject, all subsequent are not rejected
    
    for rank, (orig_idx, p_val) in enumerate(sorted_pvals):
        # Holm threshold: alpha / (n - rank)
        holm_threshold = alpha / (n - rank)
        
        # Adjusted p-value: p * (n - rank), but capped at 1.0
        # and must be at least as large as the previous adjusted p-value
        adjusted_p = min(p_val * (n - rank), 1.0)
        
        # Determine significance
        if rejected_so_far and p_val <= holm_threshold:
            is_significant = True
        else:
            is_significant = False
            rejected_so_far = False  # Once we fail to reject, stop rejecting
        
        results[orig_idx] = {
            'adjusted_p': adjusted_p,
            'is_significant': is_significant,
            'holm_threshold': holm_threshold,
            'rank': rank + 1  # 1-indexed for display
        }
    
    # Enforce monotonicity of adjusted p-values (step-up)
    # Adjusted p-values should be non-decreasing in the original sorted order
    sorted_indices = [x[0] for x in sorted_pvals]
    for i in range(1, n):
        curr_idx = sorted_indices[i]
        prev_idx = sorted_indices[i - 1]
        if results[curr_idx]['adjusted_p'] < results[prev_idx]['adjusted_p']:
            results[curr_idx]['adjusted_p'] = results[prev_idx]['adjusted_p']
    
    return results

def determine_significance(p_value, alpha=0.05):
    """Determine significance level based on p-value (uncorrected)."""
    if p_value < alpha:
        return "Significant"
    elif p_value < 0.10:
        return "Approaches Signif."
    else:
        return "Not Significant"

def determine_significance_corrected(is_significant, adjusted_p, alpha=0.05):
    """Determine significance level after Holm correction."""
    if is_significant:
        return "Significant"
    elif adjusted_p < 0.10:
        return "Approaches Signif."
    else:
        return "Not Significant"

def main():
    # File path (relative to script location)
    filepath = 'threat_explorer_survey.csv'
    output_md_file = 'statistical_analysis_results.md'

    # Collect markdown output
    md_lines = []

    print("=" * 80)
    print("THREAT EXPLORER DESIGN EXPERIMENT - STATISTICAL ANALYSIS")
    print("=" * 80)
    print()

    md_lines.append("# Threat Explorer Design Experiment - Statistical Analysis\n")
    md_lines.append("**Analysis Date:** " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    md_lines.append("\n")

    # Load data
    df = load_survey_data(filepath)
    n_participants = len(df)
    print(f"Sample Size (N): {n_participants}")
    print(f"Significance Level (α): 0.05")
    print(f"Multiple Comparison Correction: Holm-Bonferroni")
    print()

    md_lines.append("## Study Parameters\n")
    md_lines.append(f"- **Sample Size (N):** {n_participants}\n")
    md_lines.append(f"- **Significance Level (α):** 0.05\n")
    md_lines.append(f"- **Statistical Test:** Wilcoxon Signed-Rank Test (one-sided)\n")
    md_lines.append(f"- **Multiple Comparison Correction:** Holm-Bonferroni\n")
    md_lines.append("\n")

    # Get all column names from CSV
    columns = df.columns.tolist()
    print(f"CSV Columns: {columns}\n")

    # Define dimensions using actual column names from CSV
    dimensions = [
        {
            'name': 'A. Usability',
            'description': 'Well-organized',
            'text_col': columns[1],
            'chart_col': columns[2]
        },
        {
            'name': 'B. Helpfulness',
            'description': 'Right level of detail',
            'text_col': columns[3],
            'chart_col': columns[4]
        },
        {
            'name': 'C. Clarity',
            'description': 'Identify key evidence',
            'text_col': columns[5],
            'chart_col': columns[6]
        },
        {
            'name': 'D. Trust',
            'description': 'Trust output',
            'text_col': columns[7],
            'chart_col': columns[8]
        },
        {
            'name': 'E. Efficiency',
            'description': 'Understand quickly',
            'text_col': columns[9],
            'chart_col': columns[10]
        }
    ]

    # Analyze preference
    preference_col = 'Which version do you prefer?'
    preference_counts = df[preference_col].value_counts()
    chart_preference_pct = (preference_counts.get('Chart Version', 0) / n_participants) * 100
    text_preference_pct = (preference_counts.get('Text Version', 0) / n_participants) * 100

    print("PREFERENCE RESULTS:")
    print("-" * 80)
    print(f"Chart Version Preference: {preference_counts.get('Chart Version', 0)}/{n_participants} ({chart_preference_pct:.1f}%)")
    print(f"Text Version Preference: {preference_counts.get('Text Version', 0)}/{n_participants} ({text_preference_pct:.1f}%)")
    print()

    md_lines.append("## Preference Results\n")
    md_lines.append(f"- **Chart Version:** {preference_counts.get('Chart Version', 0)}/{n_participants} ({chart_preference_pct:.1f}%)\n")
    md_lines.append(f"- **Text Version:** {preference_counts.get('Text Version', 0)}/{n_participants} ({text_preference_pct:.1f}%)\n")
    md_lines.append("\n")

    # First pass: compute all statistics and collect p-values
    raw_results = []
    p_values = []
    
    for i, dim in enumerate(dimensions):
        text_scores, chart_scores = extract_dimension_data(df, dim['text_col'], dim['chart_col'])
        stats = compute_statistics(text_scores, chart_scores)
        raw_results.append({
            'dimension': dim['name'],
            'description': dim['description'],
            'mean_text': stats['mean_text'],
            'mean_chart': stats['mean_chart'],
            'difference': stats['difference'],
            'p_value': stats['p_value'],
            'statistic': stats['statistic'],
            'text_scores': text_scores,
            'chart_scores': chart_scores
        })
        p_values.append(stats['p_value'])
    
    # Apply Holm-Bonferroni correction
    holm_results = holm_bonferroni_correction(p_values, alpha=0.05)
    
    # Add corrected values to results
    results = []
    for i, raw in enumerate(raw_results):
        corrected = holm_results[i]
        results.append({
            **raw,
            'p_adjusted': corrected['adjusted_p'],
            'holm_significant': corrected['is_significant'],
            'holm_threshold': corrected['holm_threshold'],
            'holm_rank': corrected['rank'],
            'significance_uncorrected': determine_significance(raw['p_value']),
            'significance_corrected': determine_significance_corrected(
                corrected['is_significant'], 
                corrected['adjusted_p']
            )
        })

    # Print results table
    print("LIKERT SCALE ANALYSIS (1-5) WITH HOLM-BONFERRONI CORRECTION:")
    print("-" * 120)
    print(f"{'Dimension':<25} {'Text':<8} {'Chart':<8} {'Diff':<8} {'p-value':<10} {'p-adj':<10} {'Signif. (corrected)':<20}")
    print("-" * 120)

    md_lines.append("## Likert Scale Analysis (1-5) with Holm-Bonferroni Correction\n")
    md_lines.append("| Dimension | Text Avg | Chart Avg | Diff | p-value | p-adjusted | Significance |\n")
    md_lines.append("|-----------|----------|-----------|------|---------|------------|-------------|\n")

    for result in results:
        # Print row
        print(f"{result['dimension']:<25} {result['mean_text']:<8.2f} {result['mean_chart']:<8.2f} "
              f"{result['difference']:<+8.2f} {result['p_value']:<10.4f} {result['p_adjusted']:<10.4f} "
              f"{result['significance_corrected']:<20}")

        # Format for markdown
        sig_emoji = "✅" if result['significance_corrected'] == "Significant" else ("⚠️" if result['significance_corrected'] == "Approaches Signif." else "")
        md_lines.append(f"| **{result['dimension']}** ({result['description']}) | {result['mean_text']:.2f} | **{result['mean_chart']:.2f}** | {result['difference']:+.2f} | {result['p_value']:.4f} | {result['p_adjusted']:.4f} | {result['significance_corrected']} {sig_emoji} |\n")

    print("-" * 120)
    print()

    md_lines.append("\n")

    # Holm correction details
    print("HOLM-BONFERRONI CORRECTION DETAILS:")
    print("-" * 80)
    print(f"{'Rank':<6} {'Dimension':<25} {'p-value':<12} {'Threshold':<12} {'p-adjusted':<12} {'Reject H0?':<10}")
    print("-" * 80)
    
    # Sort results by p-value for Holm display
    sorted_results = sorted(results, key=lambda x: x['p_value'])
    for result in sorted_results:
        reject = "Yes" if result['holm_significant'] else "No"
        print(f"{result['holm_rank']:<6} {result['dimension']:<25} {result['p_value']:<12.4f} "
              f"{result['holm_threshold']:<12.4f} {result['p_adjusted']:<12.4f} {reject:<10}")
    print()
    
    md_lines.append("## Holm-Bonferroni Correction Details\n")
    md_lines.append("| Rank | Dimension | p-value | Holm Threshold (α/(n-rank+1)) | p-adjusted | Reject H₀? |\n")
    md_lines.append("|------|-----------|---------|-------------------------------|------------|------------|\n")
    for result in sorted_results:
        reject = "Yes ✅" if result['holm_significant'] else "No"
        md_lines.append(f"| {result['holm_rank']} | {result['dimension']} | {result['p_value']:.4f} | {result['holm_threshold']:.4f} | {result['p_adjusted']:.4f} | {reject} |\n")
    md_lines.append("\n")

    # LaTeX table output
    print("LATEX TABLE FOR PAPER:")
    print("-" * 80)
    latex_table = []
    latex_table.append("\\begin{table}[h]")
    latex_table.append("    \\centering")
    latex_table.append("    \\caption{Design Experiment Results with Holm-Bonferroni Correction (1--5 Likert Scale)}")
    latex_table.append("    \\label{tab:design_results}")
    latex_table.append("    \\begin{tabular}{lcccccc}")
    latex_table.append("        \\toprule")
    latex_table.append("        \\textbf{Dimension} & Text & Chart & Diff & $p$-value & $p_{adj}$ & Signif. \\\\")
    latex_table.append("        \\midrule")

    for result in results:
        dim_name = result['dimension']
        desc = result['description']
        text_avg = result['mean_text']
        chart_avg = result['mean_chart']
        diff = result['difference']
        p_val = result['p_value']
        p_adj = result['p_adjusted']
        sig = result['significance_corrected']

        # Format p-values
        if p_val < 0.001:
            p_str = "< .001"
        else:
            p_str = f"{p_val:.3f}"
        
        if p_adj < 0.001:
            p_adj_str = "< .001"
        else:
            p_adj_str = f"{p_adj:.3f}"

        # Bold significant results
        if sig == "Significant":
            sig_str = "\\textbf{Yes}"
            chart_avg_str = f"\\textbf{{{chart_avg:.2f}}}"
        else:
            sig_str = "No"
            chart_avg_str = f"{chart_avg:.2f}"

        latex_line = f"        \\textbf{{{dim_name}}} ({desc}) & {text_avg:.2f} & {chart_avg_str} & {diff:+.2f} & {p_str} & {p_adj_str} & {sig_str} \\\\"
        latex_table.append(latex_line)
        print(latex_line)

    latex_table.append("        \\bottomrule")
    latex_table.append("    \\end{tabular}")
    latex_table.append("    \\\\[0.5em]")
    latex_table.append("    \\footnotesize{Note: $p_{adj}$ = Holm-Bonferroni adjusted p-value. Significance at $\\alpha = 0.05$.}")
    latex_table.append("\\end{table}")

    print("        \\bottomrule")
    print("    \\end{tabular}")
    print("\\end{table}")
    print()

    md_lines.append("## LaTeX Table for Paper\n")
    md_lines.append("```latex\n")
    md_lines.extend([line + "\n" for line in latex_table])
    md_lines.append("```\n\n")

    # Summary statistics
    print("SUMMARY:")
    print("-" * 80)
    significant_count_uncorrected = sum(1 for r in results if r['significance_uncorrected'] == "Significant")
    significant_count_corrected = sum(1 for r in results if r['significance_corrected'] == "Significant")
    print(f"Significant improvements (uncorrected, p < 0.05): {significant_count_uncorrected}/{len(results)}")
    print(f"Significant improvements (Holm-corrected, p_adj < 0.05): {significant_count_corrected}/{len(results)}")
    print(f"Average improvement across all dimensions: {np.mean([r['difference'] for r in results]):.2f} points")
    max_improvement = max(results, key=lambda x: x['difference'])
    print(f"Largest improvement: {max_improvement['dimension']} ({max_improvement['description']}) with +{max_improvement['difference']:.2f} points")
    print()

    md_lines.append("## Summary\n")
    md_lines.append(f"- **Significant improvements (uncorrected, p < 0.05):** {significant_count_uncorrected}/{len(results)}\n")
    md_lines.append(f"- **Significant improvements (Holm-corrected, p_adj < 0.05):** {significant_count_corrected}/{len(results)}\n")
    md_lines.append(f"- **Average improvement across all dimensions:** {np.mean([r['difference'] for r in results]):.2f} points\n")
    md_lines.append(f"- **Largest improvement:** {max_improvement['dimension']} ({max_improvement['description']}) with +{max_improvement['difference']:.2f} points\n")
    md_lines.append("\n")

    # Effect sizes (optional)
    print("DETAILED STATISTICS PER DIMENSION:")
    print("-" * 80)

    md_lines.append("## Detailed Statistics Per Dimension\n")

    for result in results:
        text_scores = result['text_scores']
        chart_scores = result['chart_scores']
        differences = chart_scores - text_scores

        print(f"\n{result['dimension']} ({result['description']}):")
        print(f"  Text Version:  Mean={np.mean(text_scores):.2f}, SD={np.std(text_scores, ddof=1):.2f}, Median={np.median(text_scores):.1f}")
        print(f"  Chart Version: Mean={np.mean(chart_scores):.2f}, SD={np.std(chart_scores, ddof=1):.2f}, Median={np.median(chart_scores):.1f}")
        print(f"  Differences:   Mean={np.mean(differences):.2f}, SD={np.std(differences, ddof=1):.2f}")
        print(f"  Positive improvements: {np.sum(differences > 0)}/{n_participants}")
        print(f"  No change: {np.sum(differences == 0)}/{n_participants}")
        print(f"  Negative changes: {np.sum(differences < 0)}/{n_participants}")

        md_lines.append(f"### {result['dimension']} ({result['description']})\n")
        md_lines.append(f"- **Text Version:** Mean={np.mean(text_scores):.2f}, SD={np.std(text_scores, ddof=1):.2f}, Median={np.median(text_scores):.1f}\n")
        md_lines.append(f"- **Chart Version:** Mean={np.mean(chart_scores):.2f}, SD={np.std(chart_scores, ddof=1):.2f}, Median={np.median(chart_scores):.1f}\n")
        md_lines.append(f"- **Differences:** Mean={np.mean(differences):.2f}, SD={np.std(differences, ddof=1):.2f}\n")
        md_lines.append(f"- **Positive improvements:** {np.sum(differences > 0)}/{n_participants}\n")
        md_lines.append(f"- **No change:** {np.sum(differences == 0)}/{n_participants}\n")
        md_lines.append(f"- **Negative changes:** {np.sum(differences < 0)}/{n_participants}\n")
        md_lines.append("\n")

    print()
    print("=" * 80)
    print("Analysis complete!")
    print("=" * 80)

    # Write markdown file
    with open(output_md_file, 'w') as f:
        f.writelines(md_lines)

    print(f"\n✅ Results saved to: {output_md_file}")

if __name__ == "__main__":
    main()