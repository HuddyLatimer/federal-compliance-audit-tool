import os
import re
import json
import pandas as pd
from datetime import datetime

# =================================================================
# PROJECT: Federal Compliance Audit Tool
# AUTHOR: NSCC IT Programming Student (Year 2)
# CLIENT: Laty's Foundation
# PURPOSE: Automate compliance verification for internal documents.
# =================================================================

def load_rules(config_path):
    """Loads compliance rules from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            return data.get('compliance_rules', [])
    except Exception as e:
        print(f"Error loading rules: {e}")
        return []

def run_audit(target_dir, rules):
    """
    Scans files in the target directory and checks them against rules.
    Returns a list of audit results.
    """
    audit_results = []
    
    # Ensure the target directory exists
    if not os.path.exists(target_dir):
        print(f"Directory {target_dir} not found.")
        return []

    print(f"\n--- Starting Compliance Audit on: {target_dir} ---")
    
    # Gather files
    files = [f for f in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, f))]
    
    for filename in files:
        file_status = {
            "Filename": filename,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Overall_Status": "COMPLIANT"
        }
        
        failed_mandatory = []
        
        # Check each rule
        for rule in rules:
            rule_id = rule['id']
            pattern = rule['regex']
            is_mandatory = rule['mandatory']
            
            # Use Regex to search the filename
            if re.search(pattern, filename, re.IGNORECASE):
                file_status[f"{rule_id}_Match"] = "PASS"
            else:
                file_status[f"{rule_id}_Match"] = "FAIL"
                if is_mandatory:
                    failed_mandatory.append(rule['name'])
        
        # Determine overall status
        if failed_mandatory:
            file_status["Overall_Status"] = "NON-COMPLIANT"
            file_status["Notes"] = f"Missing mandatory: {', '.join(failed_mandatory)}"
        else:
            file_status["Notes"] = "All mandatory checks passed."
            
        audit_results.append(file_status)
        print(f"[{file_status['Overall_Status']}] Checked: {filename}")

    return audit_results

def generate_report(results, output_path):
    """Uses Pandas to process results and save as a CSV report."""
    if not results:
        print("No results to report.")
        return

    df = pd.DataFrame(results)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\nAudit complete. Executive report generated at: {output_path}")
    
    # Minimalist Stats for business value
    total = len(df)
    compliant = len(df[df['Overall_Status'] == 'COMPLIANT'])
    non_compliant = total - compliant
    compliance_rate = (compliant / total) * 100 if total > 0 else 0
    
    print("-" * 40)
    print(f"Audit Summary:")
    print(f"Total Files Audited: {total}")
    print(f"Compliant:           {compliant}")
    print(f"Non-Compliant:       {non_compliant}")
    print(f"Compliance Rate:     {compliance_rate:.2f}%")
    print("-" * 40)

def main():
    # Paths
    RULES_FILE = "rules.json"
    DATA_DIR = "data"
    REPORT_FILE = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # 1. Load configuration
    rules = load_rules(RULES_FILE)
    
    if not rules:
        print("No rules found. Please check rules.json.")
        return

    # 2. Run the audit engine
    results = run_audit(DATA_DIR, rules)
    
    # 3. Generate the Pandas-powered CSV report
    generate_report(results, REPORT_FILE)
    
    # Keep the window open for the user to see results
    print("\n" + "="*40)
    input("Audit finished. Press [ENTER] to close...")

if __name__ == "__main__":
    main()
