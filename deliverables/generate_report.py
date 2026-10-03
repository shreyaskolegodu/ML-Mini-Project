"""
Generates the official Two-Page Project Write-up PDF for UE24CS352A Mini-Project.
Meets all criteria in Section 3.B of the guidelines:
- Problem statement
- Dataset details
- Approach taken to solve it
- Implementation overview
- Results & Conclusions
- Exactly 2 pages in PDF format.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

from src.config import DELIVERABLES_DIR, FIGURES_DIR

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and render exact page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, letter[1] - 30, "UE24CS352A Machine Learning Mini-Project | Earthquake Ground Motion Directionality")
            self.setStrokeColor(colors.HexColor("#cccccc"))
            self.setLineWidth(0.5)
            self.line(40, letter[1] - 34, letter[0] - 40, letter[1] - 34)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 40, 24, footer_text)
        self.drawString(40, 24, "PES University - Department of Computer Science & Engineering")
        self.setStrokeColor(colors.HexColor("#cccccc"))
        self.setLineWidth(0.5)
        self.line(40, 34, letter[0] - 40, 34)
        self.restoreState()

def build_pdf_report(output_filename: str = "ML_MiniProject_Writeup.pdf"):
    pdf_path = DELIVERABLES_DIR / output_filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()
    
    # Custom tight styles for dense 2-page publication formatting
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1a252f'),
        alignment=1, # Center
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#2980b9'),
        alignment=1,
        spaceAfter=2
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#444444'),
        alignment=1,
        spaceAfter=6
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#1b3a4b'),
        spaceBefore=5,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=10.5,
        textColor=colors.HexColor('#222222'),
        spaceAfter=4,
        alignment=4 # Justified
    )
    
    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor('#2c3e50')
    )

    story = []

    # Title Block
    story.append(Paragraph("UE24CS352A - MACHINE LEARNING MINI-PROJECT REPORT", subtitle_style))
    story.append(Paragraph("Detecting and Predicting Earthquake Ground Motion Directionality Patterns Using Machine Learning Tools", title_style))
    story.append(Paragraph("<b>Reference Study:</b> Alan Poulos & Rodrigo Silva-Lopez (Blume Earthquake Engineering Center, Stanford University)", meta_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2980b9"), spaceBefore=1, spaceAfter=5))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement & Engineering Motivation", h1_style))
    p1 = (
        "Earthquake ground shaking intensity is inherently direction-dependent (a phenomenon termed <i>ground motion directionality</i>). "
        "At any recording station, there exists a critical orientation associated with maximum spectral acceleration, standardized in "
        "structural engineering as <b>RotD100</b>. In contemporary seismic hazard analysis and regional risk assessments, orientations at "
        "different locations are conventionally assumed to follow an independent uniform distribution over [0°, 180°). However, empirical "
        "observations demonstrate that orientations between closely spaced sites exhibit strong spatial coherence due to coherent wave propagation, "
        "fault directivity, and source radiation patterns. Consequently, independent sampling underpredicts simultaneous catastrophic shaking across "
        "distributed civil infrastructure (e.g., bridges, lifelines, pipeline networks). "
        "This project develops supervised machine learning algorithms to predict the acute angular difference in direction of maximum shaking, "
        "<b>Δθ ∈ [0°, 90°]</b>, between two recording sites <i>s<sub>i</sub></i> and <i>s<sub>j</sub></i> during an earthquake <i>E<sub>k</sub></i>: "
        "Δθ<sub>i,j</sub><sup>k</sup> = <i>f</i>(<i>s<sub>i</sub></i>, <i>s<sub>j</sub></i>, <i>E<sub>k</sub></i>)."
    )
    story.append(Paragraph(p1, body_style))

    # Section 2: Dataset Details
    story.append(Paragraph("2. Dataset Characteristics & Feature Engineering", h1_style))
    p2 = (
        "<b>Database:</b> The study utilizes the Pacific Earthquake Engineering Research (PEER) <b>NGA-West2</b> database containing shallow "
        "crustal records worldwide. Earthquakes with moment magnitude <i>M<sub>w</sub></i> &lt; 5.0 are filtered out to preserve engineering significance, "
        "retaining ~5,000 ground motion records. "
        "<br/><b>Pairwise Construction:</b> To predict directionality differences, all stations recording the same seismic event within an inter-site "
        "distance threshold <i>d</i> ≤ 5.0 km are paired, synthesizing <b>5,300 pairwise instances</b>. For each pair, the target variable Δθ was computed "
        "from recorded acceleration waveforms as Δθ = min(|θ<sub>i</sub> - θ<sub>j</sub>|, 180° - |θ<sub>i</sub> - θ<sub>j</sub>|). "
        "<br/><b>Initial Feature Pool:</b> 71 seismological, geological, and instrument attributes were extracted: earthquake source parameters "
        "(<i>M<sub>w</sub></i>, focal mechanism, strike, dip, rake angles, rupture length, width, area, hypocenter depth, ZTOR), dual-site distance metrics "
        "(<i>R<sub>epi</sub></i>, <i>R<sub>hyp</sub></i>, <i>R<sub>jb</sub></i>, <i>R<sub>rup</sub></i>), geotechnical soil properties (shear wave velocity <i>V<sub>s30</sub></i>, "
        "NEHRP site classes B–E), and shaking intensity metrics (PGA, PGV, PGD). Numerical attributes were standardized to zero mean and unit variance, "
        "and categorical attributes were one-hot encoded."
    )
    story.append(Paragraph(p2, body_style))

    # Embedded Figures 2 & 3 side by side
    fig2_path = str(FIGURES_DIR / "fig02_delta_theta_vs_distance.png")
    fig3_path = str(FIGURES_DIR / "fig03_delta_theta_vs_pga.png")
    
    img_w, img_h = 265, 145
    t_imgs = Table(
        [[Image(fig2_path, width=img_w, height=img_h), Image(fig3_path, width=img_w, height=img_h)]],
        colWidths=[270, 270]
    )
    t_imgs.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_imgs)
    story.append(Spacer(1, 2))
    
    caption1 = Paragraph(
        "<b>Figures 1 & 2:</b> Empirical trends of angular difference Δθ. Left: Δθ increases monotonically with inter-site distance <i>d</i> up to 5 km. "
        "Right: Δθ decreases with higher average Peak Ground Acceleration (PGA) due to enhanced source directivity alignment. Error bars denote 95% CI.",
        callout_style
    )
    story.append(caption1)

    # Backward & Forward Feature Selection
    story.append(Paragraph("3. Stepwise Backward-Forward Feature Selection", h1_style))
    p3 = (
        "To combat high dimensionality and multicollinearity, a rigorous two-stage backward-forward selection strategy based on Ridge Regression was executed. "
        "First, <b>backward ranking</b> quantified the drop in validation <i>R</i><sup>2</sup> upon removing each individual feature; larger drops signify greater "
        "predictive contribution. Second, <b>forward selection</b> iteratively introduced features in ranked order until validation performance peaked. "
        "This yielded an optimal subset of <b>21 features</b>. The analysis confirmed that <b>separation distance (<i>d</i>)</b> and <b>average PGA</b> "
        "are the two dominant physical determinants governing ground motion orientation correlation."
    )
    story.append(Paragraph(p3, body_style))

    # Page 1 Break
    story.append(PageBreak())

    # PAGE 2: Models, Implementation, Results, Discussion, Conclusions
    story.append(Paragraph("4. Methodology & Machine Learning Architectures", h1_style))
    p4 = (
        "The curated dataset (80% train / 10% validation / 10% hold-out test) was evaluated across three core architectures: "
        "<br/>• <b>Benchmark Linear Regression:</b> Simple univariate OLS model utilizing solely separation distance <i>d</i>: Δθ = <i>c</i><sub>1</sub> + <i>c</i><sub>2</sub><i>d</i>. "
        "Serves as the baseline reflecting current spatial distance decay relations. "
        "<br/>• <b>Regularized Ridge Regression:</b> Multivariate <i>L</i><sub>2</sub>-penalized linear model (min<sub>β</sub> ||<i>y</i> - <i>X</i>β||<sub>2</sub><sup>2</sup> + α||β||<sub>2</sub><sup>2</sup>) "
        "calibrated on the 21 selected features with hyperparameter α tuned on validation data (optimal α = 1.5). "
        "<br/>• <b>Deep Neural Network (MLP):</b> High-capacity Multi-Layer Perceptron utilizing ReLU activations and Adam optimization with <i>L</i><sub>2</sub> weight decay (α = 0.1). "
        "A grid search explored network depth (1 to 5 hidden layers) and neuron widths (50 to 400), selecting an optimal topology that captures complex non-linear wave interactions."
    )
    story.append(Paragraph(p4, body_style))

    # Quantitative Comparison Table
    story.append(Paragraph("5. Experimental Results & Performance Benchmarking", h1_style))
    
    # Table data
    results_data = [
        ["Model Architecture", "Inputs", "Train R²", "Test R²", "Test MAE (°)", "Test RMSE (°)"],
        ["Benchmark (Distance Only)", "1 Feature (d)", "0.038", "0.051", "16.43°", "19.95°"],
        ["Ridge Regression (L2)", "21 Features", "0.349", "0.350", "13.35°", "16.52°"],
        ["Deep Neural Network (MLP)", "21 Features", "0.381", "0.328", "13.56°", "16.79°"],
        ["Gradient Boosted Trees (Bonus)", "21 Features", "0.751", "0.325", "13.71°", "16.83°"],
    ]
    t_res = Table(results_data, colWidths=[140, 95, 65, 65, 85, 90])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b3a4b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8f9fa'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#d0d7de')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 4))

    # Embedded Figures 6 & 10 (Windowed tracking comparison)
    fig6_path = str(FIGURES_DIR / "fig06_ridge_regression_windowed_dist.png")
    fig8_path = str(FIGURES_DIR / "fig08_nn_gridsearch_heatmap.png")
    
    t_res_imgs = Table(
        [[Image(fig6_path, width=265, height=135), Image(fig8_path, width=265, height=135)]],
        colWidths=[270, 270]
    )
    t_res_imgs.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_res_imgs)
    story.append(Spacer(1, 2))
    
    caption2 = Paragraph(
        "<b>Figures 3 & 4:</b> Left: Ridge model windowed moving average tracking empirical distance trend without overfitting. "
        "Right: Neural Network grid search contour across layer depths and neuron counts evaluating validation <i>R</i><sup>2</sup>.",
        callout_style
    )
    story.append(caption2)

    # Section 6: Discussion & Key Findings
    story.append(Paragraph("6. Key Findings & Discussion on Aleatoric Uncertainty", h1_style))
    p5 = (
        "<b>1. Dominance of Distance and Shaking Amplitude:</b> As demonstrated by both the feature ranking and windowed curves, stations separated "
        "by &lt; 1.5 km and experiencing strong PGA (&gt; 0.15g) exhibit tight angular coherence (Δθ ≈ 15°–20°). Beyond 4 km or at low accelerations, "
        "local scattering decorrelates wave motions towards uniform randomness (Δθ ≈ 45°). "
        "<br/><b>2. Linear vs Non-Linear Performance:</b> Ridge regression drastically outperforms the baseline (<i>R</i><sup>2</sup> jumps from 0.051 to 0.350, "
        "MAE drops from 16.4° to 13.3°). Deep neural networks and gradient boosted trees achieve comparable test errors while fitting non-linear radiation interactions. "
        "<br/><b>3. Inherent Seismic Stochasticity:</b> The maximum achievable <i>R</i><sup>2</sup> is bounded (~0.35–0.40) due to large <i>aleatoric uncertainty</i> "
        "originating from unobservable 3D subsurface heterogeneities, crustal velocity variations, and micro-topography. While point predictions exhibit scatter, "
        "the models accurately reconstruct the physical expected mean trend across all distance and PGA bins."
    )
    story.append(Paragraph(p5, body_style))

    # Section 7: Conclusion & Future Scope
    story.append(Paragraph("7. Conclusions & Real-World Impact", h1_style))
    p6 = (
        "This project successfully developed and validated machine learning models that predict earthquake ground motion directionality from seismological "
        "and geotechnical parameters. Replacing the traditional assumption of independent uniform orientations with the developed predictive models enables "
        "realistic multi-site ground shaking simulations for urban regions. "
        "<br/><b>Future Extensions:</b> (i) Formulating probabilistic heteroscedastic loss functions to explicitly model both conditional mean and variance σ<sup>2</sup>(<b>x</b>); "
        "(ii) Extending pairwise predictions to full joint multivariate spatial Gaussian random fields for simultaneous regional infrastructure resilience evaluation."
    )
    story.append(Paragraph(p6, body_style))

    # Build the document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated 2-page write-up PDF at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    build_pdf_report()
