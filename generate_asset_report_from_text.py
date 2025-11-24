"""
Generate Asset Comparison Report from captured text data
"""

from datetime import datetime

def generate_html_report():
    """Generate HTML report from the existing text data"""

    # Data from rnd_assets_text.txt and ai_assets_text.txt
    rnd_data = {
        "total_assets": 179,
        "required_fields": "365 of 847 completed",
        "completion": "43%",
        "visible_assets": [
            {"name": "CB 175", "qr": "—", "condition": "1", "class": "Circuit Breaker", "building": "—"},
            {"name": "CB 178", "qr": "—", "condition": "1", "class": "Circuit Breaker", "building": "—"},
            {"name": "Disconnect Switch 176", "qr": "—", "condition": "1", "class": "Disconnect Switch", "building": "—"},
            {"name": "DPH", "qr": "biq-hq-1", "condition": "1", "class": "Panelboard", "building": "—"},
            {"name": "DPH-01", "qr": "—", "condition": "—", "class": "Circuit Breaker", "building": "—"}
        ]
    }

    ai_data = {
        "total_assets": 180,
        "required_fields": "365 of 852 completed",
        "completion": "43%",
        "visible_assets": [
            {"name": "CB 175", "qr": "—", "condition": "1", "class": "Circuit Breaker", "building": "—"},
            {"name": "CB 178", "qr": "—", "condition": "1", "class": "Circuit Breaker", "building": "—"},
            {"name": "Disconnect Switch 176", "qr": "—", "condition": "1", "class": "Disconnect Switch", "building": "—"},
            {"name": "DPH", "qr": "biq-hq-1", "condition": "1", "class": "Panelboard", "building": "Building 1"},
            {"name": "DPH-01", "qr": "—", "condition": "—", "class": "Circuit Breaker", "building": "—"}
        ]
    }

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Super Caremark Asset Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }}
        .summary {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 32px; font-weight: bold; margin: 10px 0; }}
        .info {{ color: #0dcaf0; }}
        .warning {{ color: #fd7e14; }}
        .success {{ color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        th {{ background: #f8f9fa; font-weight: 600; text-transform: uppercase; font-size: 12px; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold; }}
        .badge-warning {{ background: #fff3cd; color: #fd7e14; }}
        .badge-success {{ background: #d1f2eb; color: #28a745; }}
        .section {{ background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
        .diff-row {{ background: #fff3cd; }}
        .comparison-table {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }}
        .comparison-column {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .alert {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .alert-info {{ background: #cfe2ff; border-left-color: #0dcaf0; }}
        .highlight {{ background: #fff3cd; padding: 2px 4px; border-radius: 3px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏢 Super Caremark - Complete Asset Comparison Report</h1>
        <p>Comprehensive comparison between RND and AI environments</p>
        <p style="opacity: 0.9; font-size: 14px;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p style="opacity: 0.9; font-size: 12px;">
            RND: <a href="https://acme.egalvanic-rnd.com" style="color: white;">https://acme.egalvanic-rnd.com</a> &nbsp;|&nbsp;
            AI: <a href="https://acme.egalvanic.ai" style="color: white;">https://acme.egalvanic.ai</a>
        </p>
    </div>

    <div class="summary">
        <h2>📊 Summary Statistics</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-number info">{rnd_data['total_assets']}</div>
                <div>RND Assets</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">{rnd_data['required_fields']}</div>
            </div>
            <div class="stat">
                <div class="stat-number info">{ai_data['total_assets']}</div>
                <div>AI Assets</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">{ai_data['required_fields']}</div>
            </div>
            <div class="stat">
                <div class="stat-number warning">+1</div>
                <div>Asset Difference</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">AI has 1 more asset</div>
            </div>
            <div class="stat">
                <div class="stat-number success">~179</div>
                <div>Common Assets</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">Estimated</div>
            </div>
            <div class="stat">
                <div class="stat-number">+5</div>
                <div>Field Difference</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">852 vs 847 fields</div>
            </div>
            <div class="stat">
                <div class="stat-number warning">1</div>
                <div>Building Mismatch</div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 5px;">DPH asset</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>🔍 Key Findings</h2>

        <div class="alert">
            <strong>⚠️ Asset Count Mismatch:</strong> AI website has <strong>1 additional asset</strong> compared to RND (180 vs 179). This new asset needs to be identified.
        </div>

        <div class="alert alert-info">
            <strong>📋 Required Fields Updated:</strong> The AI version shows 852 required fields vs 847 in RND. This indicates <strong>5 new required fields</strong> have been added to the asset data model.
        </div>

        <div class="alert">
            <strong>🏗️ Building Field Difference:</strong> Asset "DPH" shows building as "—" (empty) in RND but "Building 1" in AI. This field-level difference needs verification.
        </div>
    </div>

    <div class="section">
        <h2>📋 Visible Asset Comparison (First 25 assets)</h2>
        <p style="color: #6c757d; margin-bottom: 15px;">
            Based on captured data, here are the visible assets from both sites. Both sites show "1-25 of X" pagination.
        </p>

        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Asset Name</th>
                    <th>QR Code</th>
                    <th>Condition</th>
                    <th>Asset Class</th>
                    <th>Building (RND)</th>
                    <th>Building (AI)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
"""

    # Compare visible assets
    for idx, (rnd_asset, ai_asset) in enumerate(zip(rnd_data['visible_assets'], ai_data['visible_assets']), 1):
        building_match = rnd_asset['building'] == ai_asset['building']
        row_class = "" if building_match else "diff-row"
        status = "✓ Match" if building_match else "⚠️ Diff"
        badge_class = "badge-success" if building_match else "badge-warning"

        html += f"""
                <tr class="{row_class}">
                    <td>{idx}</td>
                    <td><strong>{rnd_asset['name']}</strong></td>
                    <td>{rnd_asset['qr']}</td>
                    <td>{rnd_asset['condition']}</td>
                    <td>{rnd_asset['class']}</td>
                    <td>{rnd_asset['building']}</td>
                    <td>{"<span class='highlight'>" + ai_asset['building'] + "</span>" if not building_match else ai_asset['building']}</td>
                    <td><span class="badge {badge_class}">{status}</span></td>
                </tr>
"""

    html += """
            </tbody>
        </table>

        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px;">
            <strong>Note:</strong> The above table shows only the first 5 assets that were visible in the captured data.
            Both sites indicate pagination (RND: "1-25 of 179", AI: "1-25 of 180"), meaning there are <strong>154-155 more assets</strong>
            that need to be captured through pagination.
        </div>
    </div>

    <div class="section">
        <h2>📊 Side-by-Side Comparison</h2>

        <div class="comparison-table">
            <div class="comparison-column">
                <h3 style="color: #667eea;">🔵 RND Website</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Total Assets:</strong> 179
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Arc Flash Readiness:</strong> 43% Complete
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Required Fields:</strong> 365 of 847 completed
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Platform Branding:</strong> Platform
                    </li>
                    <li style="padding: 10px 0;">
                        <strong>Asset Building Info:</strong> Mostly empty
                    </li>
                </ul>
            </div>

            <div class="comparison-column">
                <h3 style="color: #764ba2;">🟣 AI Website</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Total Assets:</strong> <span class="highlight">180 (+1)</span>
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Arc Flash Readiness:</strong> 43% Complete
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Required Fields:</strong> <span class="highlight">365 of 852 completed (+5 fields)</span>
                    </li>
                    <li style="padding: 10px 0; border-bottom: 1px solid #dee2e6;">
                        <strong>Platform Branding:</strong> Egalvanic
                    </li>
                    <li style="padding: 10px 0;">
                        <strong>Asset Building Info:</strong> <span class="highlight">Some fields populated</span>
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>⚠️ Detected Differences</h2>

        <table>
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Item</th>
                    <th>RND Value</th>
                    <th>AI Value</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>Count</code></td>
                    <td><strong>Total Assets</strong></td>
                    <td>179</td>
                    <td>180</td>
                    <td><span class="badge badge-warning">MINOR</span></td>
                </tr>
                <tr>
                    <td><code>Field</code></td>
                    <td><strong>Required Fields Count</strong></td>
                    <td>847 total fields</td>
                    <td>852 total fields</td>
                    <td><span class="badge badge-warning">MINOR</span></td>
                </tr>
                <tr class="diff-row">
                    <td><code>Building</code></td>
                    <td><strong>DPH Asset</strong></td>
                    <td>— (empty)</td>
                    <td>Building 1</td>
                    <td><span class="badge badge-warning">MINOR</span></td>
                </tr>
                <tr>
                    <td><code>Branding</code></td>
                    <td><strong>Platform Name</strong></td>
                    <td>Platform</td>
                    <td>Egalvanic</td>
                    <td><span class="badge badge-success">COSMETIC</span></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>✅ Verified Matches</h2>
        <p>The following assets exist in both RND and AI with identical data:</p>
        <ul style="columns: 2; column-gap: 20px;">
            <li>CB 175 - Circuit Breaker</li>
            <li>CB 178 - Circuit Breaker</li>
            <li>Disconnect Switch 176 - Disconnect Switch</li>
            <li>DPH-01 - Circuit Breaker</li>
        </ul>
        <p style="color: #6c757d; font-size: 14px; margin-top: 15px;">
            <strong>Note:</strong> These are verified from the first page only. ~174 more assets need verification through pagination.
        </p>
    </div>

    <div class="section">
        <h2>🔍 Investigation Needed</h2>
        <ol>
            <li>
                <strong>Identify the Additional Asset:</strong> The AI website has 1 more asset than RND.
                Need to identify which asset is new or missing from RND.
            </li>
            <li>
                <strong>Complete Asset List Capture:</strong> Only the first 25 assets (out of 179-180) have been captured.
                Need to implement pagination to capture all assets.
            </li>
            <li>
                <strong>Building Field Audit:</strong> The "DPH" asset shows a building in AI but not in RND.
                Verify if this is a data enhancement or migration issue.
            </li>
            <li>
                <strong>New Required Fields:</strong> Identify which 5 new required fields were added in the AI version
                (852 vs 847 fields).
            </li>
            <li>
                <strong>Data Completeness:</strong> Both sites show 43% completion (365 fields completed).
                Verify if the same 365 fields are completed or if there are differences.
            </li>
        </ol>
    </div>

    <div class="section">
        <h2>📝 Recommendations</h2>
        <ul>
            <li><strong>Priority 1:</strong> Implement proper pagination in the scraping script to capture all 179-180 assets for complete comparison.</li>
            <li><strong>Priority 2:</strong> Investigate the 1 asset difference between RND (179) and AI (180) - identify if it's a new asset or a missing asset.</li>
            <li><strong>Priority 3:</strong> Audit the Building field differences - verify if the "DPH" asset should have "Building 1" in RND as well.</li>
            <li><strong>Priority 4:</strong> Document the 5 new required fields added in the AI version (852 vs 847 fields).</li>
            <li><strong>Priority 5:</strong> Perform field-by-field comparison for all common assets to identify any data discrepancies.</li>
        </ul>
    </div>

    <div class="section" style="background: #e7f3ff; border-left: 4px solid #0dcaf0;">
        <h2>💡 Next Steps</h2>
        <p><strong>To get a complete comparison, you need to:</strong></p>
        <ol>
            <li>Fix the asset extraction logic in the script to properly parse the table rows</li>
            <li>Implement proper pagination handling to capture all pages</li>
            <li>Run the comparison again to get all 179-180 assets</li>
            <li>Generate a detailed field-by-field comparison report</li>
        </ol>
        <p style="margin-top: 15px;">
            <strong>Alternative:</strong> Use the browser developer tools to directly export the asset table data,
            or use the website's API endpoints (if available) to fetch complete asset data.
        </p>
    </div>

    <div style="text-align: center; padding: 20px; color: #6c757d; font-size: 12px;">
        <p>Report generated from captured text data</p>
        <p>For questions or issues, refer to the source capture files: rnd_assets_text.txt and ai_assets_text.txt</p>
    </div>
</body>
</html>
"""

    with open("super_caremark_asset_comparison_report.html", 'w', encoding='utf-8') as f:
        f.write(html)

    print("✓ Report generated: super_caremark_asset_comparison_report.html")
    print(f"\n{'='*60}")
    print("SUMMARY OF FINDINGS:")
    print(f"{'='*60}")
    print(f"RND Assets:        {rnd_data['total_assets']}")
    print(f"AI Assets:         {ai_data['total_assets']}")
    print(f"Difference:        +1 asset in AI")
    print(f"Field Differences: 1 (DPH building field)")
    print(f"New Fields:        +5 required fields in AI")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    generate_html_report()
