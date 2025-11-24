                    <p><strong>Impact:</strong> <span style="color: #e74c3c; font-weight: bold;">CRITICAL - Data loss detected, requires immediate investigation</span></p>"""
                
                html += """
                </div>"""
        else:
            html += """
            <p>No differences found in this endpoint.</p>"""
        
        html += """
        </div>"""
        
        return html
    
    def run_verification(self):
        """Run the complete verification process"""
        print("🚀 STARTING COMPREHENSIVE MIGRATION VERIFICATION")
        print("=" * 50)
        
        # Load capture data
        print("📥 Loading capture data...")
        old_data = self.load_complete_capture(self.old_capture_dir)
        new_data = self.load_complete_capture(self.new_capture_dir)
        
        if not old_data or not new_data:
            print("❌ Failed to load capture data. Exiting.")
            return
        
        # Extract responses
        old_responses = old_data.get("responses", []) if isinstance(old_data, dict) else []
        new_responses = new_data.get("responses", []) if isinstance(new_data, dict) else []
        
        print(f"📊 Loaded {len(old_responses)} responses from old site")
        print(f"📊 Loaded {len(new_responses)} responses from new site")
        
        # Compare endpoints by path
        print("🔍 Comparing endpoints by path...")
        endpoint_differences = self.compare_endpoints_by_path(old_responses, new_responses)
        
        # Analyze site-specific data
        print("🏢 Analyzing site-specific data...")
        site_analysis = self.analyze_site_specific_data(old_responses, new_responses)
        
        # Compare screenshots
        print("📸 Comparing screenshots...")
        screenshot_analysis = self.compare_screenshots()
        
        # Store results
        self.results["endpoint_differences"] = endpoint_differences
        self.results["site_analysis"] = site_analysis
        self.results["screenshot_analysis"] = screenshot_analysis
        
        # Generate statistics
        self.generate_statistics(endpoint_differences, site_analysis)
        
        # Generate HTML report
        print("📄 Generating comprehensive HTML report...")
        report_path = self.generate_comprehensive_html_report()
        
        # Print summary
        summary = self.results["summary"]
        print("\n" + "=" * 50)
        print("✅ VERIFICATION COMPLETE")
        print("=" * 50)
        print(f"📈 Sites Analyzed: {len(summary['sites_analyzed'])}")
        print(f"🚨 Critical Issues: {summary['critical_issues']}")
        print(f"⚠️  Major Differences: {summary['major_differences']}")
        print(f"ℹ️  Minor Differences: {summary['minor_differences']}")
        print(f"✅ Identical Endpoints: {summary['identical_endpoints']}")
        print(f"📊 Report Generated: {report_path}")
        print("=" * 50)
        
        return self.results

def main():
    """Main function to run the comprehensive migration verification"""
    # Use the directories with the most complete data
    old_capture_dir = "complete_captures_20251121_201827"
    new_capture_dir = "complete_tab_captures_20251121_202444"
    
    # Verify directories exist
    if not os.path.exists(old_capture_dir):
        print(f"❌ Old capture directory not found: {old_capture_dir}")
        return
    
    if not os.path.exists(new_capture_dir):
        print(f"❌ New capture directory not found: {new_capture_dir}")
        return
    
    # Create verifier and run verification
    verifier = ComprehensiveMigrationVerifier(old_capture_dir, new_capture_dir)
    results = verifier.run_verification()
    
    return results

if __name__ == "__main__":
    main()