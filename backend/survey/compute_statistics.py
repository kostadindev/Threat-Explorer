#!/usr/bin/env python3
"""
Statistical Analysis for Threat Explorer Design Experiment
Performs Wilcoxon Signed-Rank Test on paired survey data comparing Text vs Chart versions
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

def determine_significance(p_value, alpha=0.05):
    """Determine significance level based on p-value."""
    if p_value < alpha:
        return "Significant"
    elif p_value < 0.10:
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
    print()

    md_lines.append("## Study Parameters\n")
    md_lines.append(f"- **Sample Size (N):** {n_participants}\n")
    md_lines.append(f"- **Significance Level (α):** 0.05\n")
    md_lines.append(f"- **Statistical Test:** Wilcoxon Signed-Rank Test (one-sided)\n")
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

    # Analyze each dimension
    print("LIKERT SCALE ANALYSIS (1-5):")
    print("-" * 80)
    print(f"{'Dimension':<30} {'Text Avg':<12} {'Chart Avg':<12} {'Diff':<10} {'p-value':<12} {'Significance':<20}")
    print("-" * 80)

    md_lines.append("## Likert Scale Analysis (1-5)\n")
    md_lines.append("| Dimension | Text Avg | Chart Avg | Difference | p-value | Significance |\n")
    md_lines.append("|-----------|----------|-----------|------------|---------|-------------|\n")

    results = []
    for dim in dimensions:
        text_scores, chart_scores = extract_dimension_data(df, dim['text_col'], dim['chart_col'])
        stats = compute_statistics(text_scores, chart_scores)
        significance = determine_significance(stats['p_value'])

        results.append({
            'dimension': dim['name'],
            'description': dim['description'],
            'mean_text': stats['mean_text'],
            'mean_chart': stats['mean_chart'],
            'difference': stats['difference'],
            'p_value': stats['p_value'],
            'significance': significance
        })

        # Print row
        print(f"{dim['name']:<30} {stats['mean_text']:<12.2f} {stats['mean_chart']:<12.2f} "
              f"{stats['difference']:<+10.2f} {stats['p_value']:<12.4f} {significance:<20}")

        # Format for markdown
        sig_emoji = "✅" if significance == "Significant" else ("⚠️" if significance == "Approaches Signif." else "")
        md_lines.append(f"| **{dim['name']}** ({dim['description']}) | {stats['mean_text']:.2f} | **{stats['mean_chart']:.2f}** | {stats['difference']:+.2f} | {stats['p_value']:.4f} | {significance} {sig_emoji} |\n")

    print("-" * 80)
    print()

    md_lines.append("\n")

    # LaTeX table output
    print("LATEX TABLE FOR PAPER:")
    print("-" * 80)
    latex_table = []
    latex_table.append("\\begin{table}[h]")
    latex_table.append("    \\centering")
    latex_table.append("    \\caption{Design Experiment Results and Statistical Analysis (1--5 Likert Scale)}")
    latex_table.append("    \\label{tab:design_results}")
    latex_table.append("    \\begin{tabular}{lccccc}")
    latex_table.append("        \\toprule")
    latex_table.append("        \\textbf{Dimension / Survey Question} & Text Avg. & Chart Avg. & Difference & $\\mathbf{p}$-value & Significance ($\\mathbf{\\alpha=0.05}$) \\\\")
    latex_table.append("        \\midrule")

    for result in results:
        dim_name = result['dimension']
        desc = result['description']
        text_avg = result['mean_text']
        chart_avg = result['mean_chart']
        diff = result['difference']
        p_val = result['p_value']
        sig = result['significance']

        # Format p-value
        if p_val < 0.001:
            p_str = "< 0.001"
        else:
            p_str = f"$\\approx {p_val:.3f}$"

        # Bold significant results
        sig_str = f"\\textbf{{{sig}}}" if sig == "Significant" else sig
        chart_avg_str = f"\\textbf{{{chart_avg:.2f}}}" if chart_avg > text_avg else f"{chart_avg:.2f}"

        latex_line = f"        \\textbf{{{dim_name}}} ({desc}) & {text_avg:.2f} & {chart_avg_str} & {diff:+.2f} & {p_str} & {sig_str} \\\\"
        latex_table.append(latex_line)
        print(latex_line)

    latex_table.append("        \\bottomrule")
    latex_table.append("    \\end{tabular}")
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
    significant_count = sum(1 for r in results if r['significance'] == "Significant")
    print(f"Significant improvements (p < 0.05): {significant_count}/{len(results)}")
    print(f"Average improvement across all dimensions: {np.mean([r['difference'] for r in results]):.2f} points")
    max_improvement = max(results, key=lambda x: x['difference'])
    print(f"Largest improvement: {max_improvement['dimension']} ({max_improvement['description']}) with +{max_improvement['difference']:.2f} points")
    print()

    md_lines.append("## Summary\n")
    md_lines.append(f"- **Significant improvements (p < 0.05):** {significant_count}/{len(results)}\n")
    md_lines.append(f"- **Average improvement across all dimensions:** {np.mean([r['difference'] for r in results]):.2f} points\n")
    md_lines.append(f"- **Largest improvement:** {max_improvement['dimension']} ({max_improvement['description']}) with +{max_improvement['difference']:.2f} points\n")
    md_lines.append("\n")

    # Effect sizes (optional)
    print("DETAILED STATISTICS PER DIMENSION:")
    print("-" * 80)

    md_lines.append("## Detailed Statistics Per Dimension\n")

    for dim in dimensions:
        text_scores, chart_scores = extract_dimension_data(df, dim['text_col'], dim['chart_col'])
        differences = chart_scores - text_scores

        print(f"\n{dim['name']} ({dim['description']}):")
        print(f"  Text Version:  Mean={np.mean(text_scores):.2f}, SD={np.std(text_scores, ddof=1):.2f}, Median={np.median(text_scores):.1f}")
        print(f"  Chart Version: Mean={np.mean(chart_scores):.2f}, SD={np.std(chart_scores, ddof=1):.2f}, Median={np.median(chart_scores):.1f}")
        print(f"  Differences:   Mean={np.mean(differences):.2f}, SD={np.std(differences, ddof=1):.2f}")
        print(f"  Positive improvements: {np.sum(differences > 0)}/{n_participants}")
        print(f"  No change: {np.sum(differences == 0)}/{n_participants}")
        print(f"  Negative changes: {np.sum(differences < 0)}/{n_participants}")

        md_lines.append(f"### {dim['name']} ({dim['description']})\n")
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
