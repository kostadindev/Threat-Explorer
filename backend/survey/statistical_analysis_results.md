# Threat Explorer Design Experiment - Statistical Analysis
**Analysis Date:** 2025-12-12 16:05:02

## Study Parameters
- **Sample Size (N):** 12
- **Significance Level (α):** 0.05
- **Statistical Test:** Wilcoxon Signed-Rank Test (one-sided)
- **Multiple Comparison Correction:** Holm-Bonferroni

## Preference Results
- **Chart Version:** 12/12 (100.0%)
- **Text Version:** 0/12 (0.0%)

## Likert Scale Analysis (1-5) with Holm-Bonferroni Correction
| Dimension | Text Avg | Chart Avg | Diff | p-value | p-adjusted | Significance |
|-----------|----------|-----------|------|---------|------------|-------------|
| **A. Usability** (Well-organized) | 3.42 | **4.67** | +1.25 | 0.0020 | 0.0078 | Significant ✅ |
| **B. Helpfulness** (Right level of detail) | 3.50 | **4.42** | +0.92 | 0.0449 | 0.0781 | Approaches Signif. ⚠️ |
| **C. Clarity** (Identify key evidence) | 3.17 | **4.50** | +1.33 | 0.0020 | 0.0078 | Significant ✅ |
| **D. Trust** (Trust output) | 3.83 | **4.58** | +0.75 | 0.0391 | 0.0781 | Approaches Signif. ⚠️ |
| **E. Efficiency** (Understand quickly) | 2.58 | **4.75** | +2.17 | 0.0010 | 0.0049 | Significant ✅ |

## Holm-Bonferroni Correction Details
| Rank | Dimension | p-value | Holm Threshold (α/(n-rank+1)) | p-adjusted | Reject H₀? |
|------|-----------|---------|-------------------------------|------------|------------|
| 1 | E. Efficiency | 0.0010 | 0.0100 | 0.0049 | Yes ✅ |
| 2 | A. Usability | 0.0020 | 0.0125 | 0.0078 | Yes ✅ |
| 3 | C. Clarity | 0.0020 | 0.0167 | 0.0078 | Yes ✅ |
| 4 | D. Trust | 0.0391 | 0.0250 | 0.0781 | No |
| 5 | B. Helpfulness | 0.0449 | 0.0500 | 0.0781 | No |

## LaTeX Table for Paper
```latex
\begin{table}[h]
    \centering
    \caption{Design Experiment Results with Holm-Bonferroni Correction (1--5 Likert Scale)}
    \label{tab:design_results}
    \begin{tabular}{lcccccc}
        \toprule
        \textbf{Dimension} & Text & Chart & Diff & $p$-value & $p_{adj}$ & Signif. \\
        \midrule
        \textbf{A. Usability} (Well-organized) & 3.42 & \textbf{4.67} & +1.25 & 0.002 & 0.008 & \textbf{Yes} \\
        \textbf{B. Helpfulness} (Right level of detail) & 3.50 & 4.42 & +0.92 & 0.045 & 0.078 & No \\
        \textbf{C. Clarity} (Identify key evidence) & 3.17 & \textbf{4.50} & +1.33 & 0.002 & 0.008 & \textbf{Yes} \\
        \textbf{D. Trust} (Trust output) & 3.83 & 4.58 & +0.75 & 0.039 & 0.078 & No \\
        \textbf{E. Efficiency} (Understand quickly) & 2.58 & \textbf{4.75} & +2.17 & < .001 & 0.005 & \textbf{Yes} \\
        \bottomrule
    \end{tabular}
    \\[0.5em]
    \footnotesize{Note: $p_{adj}$ = Holm-Bonferroni adjusted p-value. Significance at $\alpha = 0.05$.}
\end{table}
```

## Summary
- **Significant improvements (uncorrected, p < 0.05):** 5/5
- **Significant improvements (Holm-corrected, p_adj < 0.05):** 3/5
- **Average improvement across all dimensions:** 1.28 points
- **Largest improvement:** E. Efficiency (Understand quickly) with +2.17 points

## Detailed Statistics Per Dimension
### A. Usability (Well-organized)
- **Text Version:** Mean=3.42, SD=0.79, Median=4.0
- **Chart Version:** Mean=4.67, SD=0.49, Median=5.0
- **Differences:** Mean=1.25, SD=1.06
- **Positive improvements:** 9/12
- **No change:** 3/12
- **Negative changes:** 0/12

### B. Helpfulness (Right level of detail)
- **Text Version:** Mean=3.50, SD=1.09, Median=4.0
- **Chart Version:** Mean=4.42, SD=0.67, Median=4.5
- **Differences:** Mean=0.92, SD=1.51
- **Positive improvements:** 8/12
- **No change:** 2/12
- **Negative changes:** 2/12

### C. Clarity (Identify key evidence)
- **Text Version:** Mean=3.17, SD=0.83, Median=3.0
- **Chart Version:** Mean=4.50, SD=0.67, Median=5.0
- **Differences:** Mean=1.33, SD=1.07
- **Positive improvements:** 9/12
- **No change:** 3/12
- **Negative changes:** 0/12

### D. Trust (Trust output)
- **Text Version:** Mean=3.83, SD=0.94, Median=4.0
- **Chart Version:** Mean=4.58, SD=0.67, Median=5.0
- **Differences:** Mean=0.75, SD=1.14
- **Positive improvements:** 6/12
- **No change:** 5/12
- **Negative changes:** 1/12

### E. Efficiency (Understand quickly)
- **Text Version:** Mean=2.58, SD=1.31, Median=2.0
- **Chart Version:** Mean=4.75, SD=0.45, Median=5.0
- **Differences:** Mean=2.17, SD=1.27
- **Positive improvements:** 10/12
- **No change:** 2/12
- **Negative changes:** 0/12

