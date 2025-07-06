import csv
import os
import tempfile
import pytest
from models import PPPLoanDataSchema
from pydantic import ValidationError

def clean_row(row):
    """Clean row data by converting empty strings to None"""
    return {k: (v if v.strip() != "" else None) for k, v in row.items()}

@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing"""
    return [
        {
            "LoanNumber": "12345",
            "DateApproved": "04/01/2020",
            "SBAOfficeCode": "123",
            "ProcessingMethod": "PPP",
            "BorrowerName": "Test Company",
            "BorrowerAddress": "123 Test St",
            "BorrowerCity": "Test City",
            "BorrowerState": "CA",
            "BorrowerZip": "12345",
            "LoanStatusDate": "04/01/2020",
            "LoanStatus": "Paid in Full",
            "Term": "24",
            "SBAGuarantyPercentage": "100",
            "InitialApprovalAmount": "10000",
            "CurrentApprovalAmount": "10000",
            "UndisbursedAmount": "0",
            "FranchiseName": "",
            "ServicingLenderLocationID": "123",
            "ServicingLenderName": "Test Bank",
            "ServicingLenderAddress": "456 Bank St",
            "ServicingLenderCity": "Bank City",
            "ServicingLenderState": "CA",
            "ServicingLenderZip": "54321",
            "RuralUrbanIndicator": "U",
            "HubzoneIndicator": "N",
            "LMIIndicator": "N",
            "BusinessAgeDescription": "Existing or more than 2 years old",
            "ProjectCity": "Test City",
            "ProjectCountyName": "Test County",
            "ProjectState": "CA",
            "ProjectZip": "12345",
            "CD": "12",
            "JobsReported": "5",
            "NAICSCode": "123456",
            "Race": "",
            "Ethnicity": "",
            "UTILITIES_PROCEED": "1000",
            "PAYROLL_PROCEED": "8000",
            "MORTGAGE_INTEREST_PROCEED": "1000",
            "RENT_PROCEED": "0",
            "REFINANCE_EIDL_PROCEED": "0",
            "HEALTH_CARE_PROCEED": "0",
            "DEBT_INTEREST_PROCEED": "0",
            "BusinessType": "Corporation",
            "OriginatingLenderLocationID": "123",
            "OriginatingLender": "Test Bank",
            "OriginatingLenderCity": "Bank City",
            "OriginatingLenderState": "CA",
            "Gender": "",
            "Veteran": "",
            "NonProfit": "N",
            "ForgivenessAmount": "10000",
            "ForgivenessDate": "01/01/2021"
        }
    ]

@pytest.fixture
def sample_csv_file(sample_csv_data):
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        if sample_csv_data:
            fieldnames = sample_csv_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_csv_data)
        
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)

def test_pydantic_model_validation_success(sample_csv_file):
    """Test that valid CSV data passes pydantic validation"""
    success_count = 0
    error_count = 0
    
    with open(sample_csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader, 1):
            try:
                cleaned_row = clean_row(row)
                model = PPPLoanDataSchema(**cleaned_row)
                success_count += 1
                
                # Basic assertions
                assert model is not None, f"Model should not be None for row {i}"
                assert hasattr(model, 'loan_number'), "Model should have loan_number attribute"
                
            except ValidationError as e:
                error_count += 1
                print(f"Row {i} validation error: {e}")
    
    assert success_count > 0, "At least one row should pass validation"
    assert error_count == 0, f"No validation errors expected, but got {error_count}"

def test_pydantic_model_with_invalid_data():
    """Test that invalid data fails pydantic validation"""
    invalid_data = {
        "LoanNumber": "",  # Empty required field
        "DateApproved": "invalid-date",  # Invalid date format
        "InitialApprovalAmount": "not-a-number",  # Invalid number
    }
    
    with pytest.raises(ValidationError):
        PPPLoanDataSchema(**invalid_data)

def test_clean_row_function():
    """Test the clean_row helper function"""
    test_row = {
        "field1": "value1",
        "field2": "",
        "field3": "   ",
        "field4": "value4"
    }
    
    cleaned = clean_row(test_row)
    
    assert cleaned["field1"] == "value1"
    assert cleaned["field2"] is None
    assert cleaned["field3"] is None
    assert cleaned["field4"] == "value4"

def test_pydantic_model_validation_with_real_csv():
    """Test validation with actual CSV file if it exists"""
    csv_paths = ["ppp.csv", "ppp_csvs/ppp.csv"]
    
    for csv_path in csv_paths:
        if os.path.exists(csv_path):
            success_count = 0
            error_count = 0
            max_rows_to_test = 10  # Limit to first 10 rows for CI speed
            
            with open(csv_path, newline='', encoding='cp1252') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, 1):
                    if i > max_rows_to_test:
                        break
                        
                    try:
                        cleaned_row = clean_row(row)
                        model = PPPLoanDataSchema(**cleaned_row)
                        success_count += 1
                    except ValidationError as e:
                        error_count += 1
                        print(f"Row {i} validation error: {e}")
            
            print(f"Real CSV validation: Success: {success_count}, Errors: {error_count}")
            assert success_count > 0, "At least one row should pass validation from real CSV"
            break
    else:
        # If no real CSV found, skip this test
        pytest.skip("No real CSV file found for testing")