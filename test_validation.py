import pandas as pd
from models import PPPLoanDataSchema
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_validation():
    # Sample data that covers different field types and edge cases
    test_data = [
        {
            "LoanNumber": "1234567890",
            "DateApproved": "01/15/2021",
            "SBAOfficeCode": "123",
            "ProcessingMethod": "PPP",
            "BorrowerName": "Test Company",
            "InitialApprovalAmount": "100000.50",
            "CurrentApprovalAmount": "100000.50",
            "Term": "24",
            "SBAGuarantyPercentage": "75",
            "JobsReported": "10",
            "UtilitiesProceed": "1000.00",
            "PayrollProceed": "80000.00",
            "MortgageInterestProceed": "5000.00",
            "RentProceed": "5000.00",
            "HealthCareProceed": "2000.00",
            "DebtInterestProceed": "1000.00",
            "ForgivenessAmount": "100000.50",
            "ForgivenessDate": "01/15/2022",
            "HubzoneIndicator": "Y",
            "LMIIndicator": "Y",
            "NonProfit": "N"
        },
        {
            "LoanNumber": "",  # Should fail validation
            "DateApproved": "invalid_date",  # Should be None
            "SBAOfficeCode": None,
            "ProcessingMethod": "",
            "BorrowerName": None,
            "InitialApprovalAmount": "invalid",  # Should be None
            "CurrentApprovalAmount": "",
            "Term": "invalid",  # Should be None
            "SBAGuarantyPercentage": "",
            "JobsReported": "invalid",  # Should be None
            "UtilitiesProceed": "",
            "PayrollProceed": None,
            "MortgageInterestProceed": "",
            "RentProceed": None,
            "HealthCareProceed": "",
            "DebtInterestProceed": None,
            "ForgivenessAmount": "",
            "ForgivenessDate": None,
            "HubzoneIndicator": "",
            "LMIIndicator": None,
            "NonProfit": ""
        }
    ]

    logger.info("Starting validation tests...")
    
    # Test valid data
    try:
        validated_row = PPPLoanDataSchema(**test_data[0])
        logger.info("✅ Valid data test passed")
        logger.info(f"Validated data: {validated_row.model_dump()}")
    except Exception as e:
        logger.error(f"❌ Valid data test failed: {e}")

    # Test invalid data
    try:
        validated_row = PPPLoanDataSchema(**test_data[1])
        logger.error("❌ Invalid data test failed - should have raised an error")
    except Exception as e:
        logger.info("✅ Invalid data test passed - caught expected error")
        logger.info(f"Error message: {str(e)}")

    # Test with pandas DataFrame
    try:
        df = pd.DataFrame(test_data)
        logger.info("\nTesting with pandas DataFrame...")
        
        for idx, row in df.iterrows():
            try:
                row_dict = {k: None if pd.isna(v) else v for k, v in row.to_dict().items()}
                validated_row = PPPLoanDataSchema(**row_dict)
                logger.info(f"✅ Row {idx} validation passed")
            except Exception as e:
                logger.error(f"❌ Row {idx} validation failed: {e}")
                logger.error(f"Problematic data: {row_dict}")
    except Exception as e:
        logger.error(f"❌ DataFrame test failed: {e}")

if __name__ == "__main__":
    test_data_validation() 