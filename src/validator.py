import os
import pandas as pd

class SubmissionValidator:
    REQUIRED_COLUMNS = [
        "candidate_id",
        "rank",
        "final_score",
        "skill_score",
        "experience_score",
        "semantic_score",
        "recommendation"
    ]

    @classmethod
    def validate_submission(cls, csv_path: str) -> dict:
        """
        Validates the submission CSV file for format, missing values, duplicates, and ranges.
        Returns:
            dict: {
                "valid": bool,
                "errors": list of str,
                "warnings": list of str,
                "candidate_count": int
            }
        """
        errors = []
        warnings = []
        
        # 1. File existence check
        if not os.path.exists(csv_path):
            errors.append(f"File '{csv_path}' does not exist.")
            return {"valid": False, "errors": errors, "warnings": warnings, "candidate_count": 0}
            
        # 2. Try loading
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            errors.append(f"Failed to read CSV file: {e}")
            return {"valid": False, "errors": errors, "warnings": warnings, "candidate_count": 0}
            
        candidate_count = len(df)
        if candidate_count == 0:
            errors.append("Submission CSV is empty.")
            return {"valid": False, "errors": errors, "warnings": warnings, "candidate_count": 0}
            
        # 3. Column presence check
        missing_cols = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            
        # 4. Duplicate candidates check
        if "candidate_id" in df.columns:
            duplicates = df["candidate_id"].duplicated().sum()
            if duplicates > 0:
                errors.append(f"Found {duplicates} duplicate candidate_id entries.")
                
        # 5. Null values check
        nulls = df.isnull().sum()
        for col, count in nulls.items():
            if count > 0:
                if col in ["candidate_id", "rank", "final_score"]:
                    errors.append(f"Column '{col}' has {count} null values. Nulls are prohibited in this column.")
                else:
                    warnings.append(f"Column '{col}' has {count} null values.")
                    
        # 6. Rank correctness check
        if "rank" in df.columns:
            # Check if ranks are consecutive integers starting from 1
            sorted_ranks = df["rank"].tolist()
            expected_ranks = list(range(1, len(df) + 1))
            if sorted_ranks != expected_ranks:
                errors.append("Ranks are not consecutive integers starting from 1 or are not sorted correctly.")
                
        # 7. Score ranges check
        score_cols = ["final_score", "skill_score", "experience_score", "semantic_score"]
        for col in score_cols:
            if col in df.columns:
                out_of_bounds = df[(df[col] < 0.0) | (df[col] > 1.0)]
                if len(out_of_bounds) > 0:
                    errors.append(f"Column '{col}' has {len(out_of_bounds)} values outside the valid range [0.0, 1.0]. Example: {out_of_bounds.iloc[0][col]}")
                    
        # 8. Recommendation check
        if "recommendation" in df.columns:
            empty_recs = df[df["recommendation"].astype(str).str.strip() == ""]
            if len(empty_recs) > 0:
                warnings.append(f"Found {len(empty_recs)} candidates with empty recommendations.")
                
        is_valid = len(errors) == 0
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "candidate_count": candidate_count
        }

    @classmethod
    def print_report(cls, csv_path: str):
        """
        Runs validation and prints a formatted report to the console.
        """
        report = cls.validate_submission(csv_path)
        print("\n" + "="*50)
        print("          SUBMISSION VALIDATION REPORT          ")
        print("="*50)
        print(f"File: {csv_path}")
        print(f"Total Candidates: {report['candidate_count']}")
        print(f"Status: {'PASSED' if report['valid'] else 'FAILED'}")
        print("-"*50)
        
        if report['errors']:
            print(f"Errors ({len(report['errors'])}):")
            for err in report['errors']:
                print(f"  [ERROR] {err}")
        else:
            print("  [OK] No formatting or structure errors found.")
            
        if report['warnings']:
            print(f"\nWarnings ({len(report['warnings'])}):")
            for warn in report['warnings']:
                print(f"  [WARNING] {warn}")
        else:
            print("  [OK] No warnings found.")
        print("="*50 + "\n")
        return report['valid']

if __name__ == "__main__":
    import sys
    path = "outputs/submission.csv"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    cls = SubmissionValidator()
    cls.print_report(path)
