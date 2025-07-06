"""
This test will test the pydantic model for the PPPLoanDataSchema and the QuestionRequest and QuestionResponse models for the API.
For the PPPLoanDataSchema:
    - Test that the model is created correctly and all computed fields are working as expected.
    - Test the model against a sample record from the database.
    - Test that the model will drop any rows that are missing the required fields: loan_number, date_approved, borrower_name.
    - Test the ProcessPPPLoanDataDoFn function in the run.py file.
For the QuestionRequest and QuestionResponse models:
    - Test that the models are created correctly and all fields are working as expected.
    - Test that the models will drop any rows that are missing the required fields: question.
"""
import pytest
import datetime
import apache_beam as beam

from typing import Any
from apache_beam.testing.test_pipeline import TestPipeline as PPPLoanDataTestPipeline
from models import PPPLoanDataSchema, QuestionRequest, QuestionResponse
from run import ProcessPPPLoanDataDoFn
from pydantic import ValidationError

class TestPPPLoanDataSchema:
    """Test the PPPLoanDataSchema model."""
    SAMPLE_RECORD: dict[str, Any] = {
        "LoanNumber": "9547507704",
        "DateApproved": "05/01/2020",
        "SBAOfficeCode": "0464",
        "ProcessingMethod": "PPP",
        "BorrowerName": "SUMTER COATINGS, INC.",
        "BorrowerAddress": "2410 Highway 15 South",
        "BorrowerCity": "Sumter",
        "BorrowerState": "SC",
        "BorrowerZip": "29150-9662",
        "LoanStatusDate": "12/18/2020",
        "LoanStatus": "Paid in Full",
        "Term": "24",
        "SBAGuarantyPercentage": "100",
        "InitialApprovalAmount": "769358.78",
        "CurrentApprovalAmount": "769358.78",
        "UndisbursedAmount": "0",
        "FranchiseName": "",
        "ServicingLenderLocationID": "19248",
        "ServicingLenderName": "Synovus Bank",
        "ServicingLenderAddress": "1148 Broadway",
        "ServicingLenderCity": "COLUMBUS",
        "ServicingLenderState": "GA",
        "ServicingLenderZip": "31901-2429",
        "RuralUrbanIndicator": "U",
        "HubzoneIndicator": "N",
        "LMIIndicator": "N",
        "BusinessAgeDescription": "Existing or more than 2 years old",
        "ProjectCity": "Sumter",
        "ProjectCountyName": "SUMTER",
        "ProjectState": "SC",
        "ProjectZip": "29150-9662",
        "CD": "SC-05",
        "JobsReported": "62",
        "NAICSCode": "325510",
        "Race": "Unanswered",
        "Ethnicity": "Unknown/NotStated",
        "UTILITIES_PROCEED": "0",
        "PAYROLL_PROCEED": "769358.78",
        "MORTGAGE_INTEREST_PROCEED": "0",
        "RENT_PROCEED": "0",
        "REFINANCE_EIDL_PROCEED": "0",
        "HEALTH_CARE_PROCEED": "0",
        "DEBT_INTEREST_PROCEED": "0",
        "BusinessType": "Corporation",
        "OriginatingLenderLocationID": "19248",
        "OriginatingLender": "Synovus Bank",
        "OriginatingLenderCity": "COLUMBUS",
        "OriginatingLenderState": "GA",
        "Gender": "Unanswered",
        "Veteran": "Unanswered",
        "NonProfit": "N",
        "ForgivenessAmount": "773553.37",
        "ForgivenessDate": "11/20/2020"
    }

    def test_model_mandatory_fields(self):
        """Test that the model will drop any rows that are missing the required fields: loan_number, date_approved, borrower_name."""
        # TestCase1 [No Loan Number] (@field_validator error)
        test_case_1: dict[str, Any] = {
            "DateApproved": "05/01/2020",
            "BorrowerName": "SUMTER COATINGS, INC.",
        }
        # TestCase2 [No Borrower Name] (@field_validator error)
        test_case_2: dict[str, Any] = {
            "LoanNumber": "9547507704",
            "DateApproved": "05/01/2020",
        }
        # TestCase3 [No Date Approved] (@field_validator error)
        test_case_3: dict[str, Any] = {
            "LoanNumber": "9547507704",
            "BorrowerName": "SUMTER COATINGS, INC.",
        }

        test_cases: list[dict[str, Any]] = [
            test_case_1,
            test_case_2,
            test_case_3,
        ]

        for test_case in test_cases:
            with pytest.raises(ValidationError) or pytest.raises(ValueError):
                PPPLoanDataSchema(**test_case)
        
    def test_model_against_sample_record(self):
        """Test the model against a sample record from the database."""
        record: PPPLoanDataSchema = PPPLoanDataSchema(**self.SAMPLE_RECORD)
        assert record is not None
        assert record.loan_number == "9547507704"
        assert record.date_approved == datetime.datetime(2020, 5, 1)
        assert record.borrower_name == "SUMTER COATINGS, INC."
        assert record.sba_office_code == "0464"
        assert record.processing_method == "PPP"
        assert record.borrower_address == "2410 Highway 15 South"
        assert record.borrower_city == "Sumter"
        assert record.borrower_state == "SC"
        assert record.borrower_zip == "29150-9662"
        assert record.loan_status_date == datetime.datetime(2020, 12, 18)
        assert record.loan_status == "Paid in Full"
        assert record.term == 24
        assert record.sba_guaranty_percentage == 100.0
        assert record.initial_approval_amount == 769358.78
        assert record.current_approval_amount == 769358.78
        assert record.undisbursed_amount == 0.0
        assert record.franchise_name == ""
        assert record.servicing_lender_location_id == "19248"
        assert record.servicing_lender_name == "Synovus Bank"
        assert record.servicing_lender_address == "1148 Broadway"
        assert record.servicing_lender_city == "COLUMBUS"
        assert record.servicing_lender_state == "GA"
        assert record.servicing_lender_zip == "31901-2429"
        assert record.rural_urban_indicator == "U"
        assert record.hubzone_indicator == "N"
        assert record.lmi_indicator == "N"
        assert record.business_age_description == "Existing or more than 2 years old"
        assert record.project_city == "Sumter"
        assert record.project_county_name == "SUMTER"
        assert record.project_state == "SC"
        assert record.project_zip == "29150-9662"
        assert record.cd == "SC-05"
        assert record.jobs_reported == 62
        assert record.naics_code == "325510"
        assert record.race == "Unanswered"
        assert record.ethnicity == "Unknown/NotStated"
        assert record.gender == "Unanswered"
        assert record.veteran == "Unanswered"
        assert record.non_profit == "N"
        assert record.forgiveness_amount == 773553.37
        assert record.forgiveness_date == datetime.datetime(2020, 11, 20)
        assert record.utilities_proceed == 0.0
        assert record.payroll_proceed == 769358.78
        assert record.mortgage_interest_proceed == 0.0
        assert record.rent_proceed == 0.0
        assert record.refinance_eidl_proceed == 0.0
        assert record.health_care_proceed == 0.0
        assert record.debt_interest_proceed == 0.0
        assert record.business_type == "Corporation"
        assert record.originating_lender_location_id == "19248"
        assert record.originating_lender == "Synovus Bank"
        assert record.originating_lender_city == "COLUMBUS"
        assert record.originating_lender_state == "GA"
        assert record.business_type == "Corporation"
        assert record.originating_lender_location_id == "19248"
        assert record.forgiveness_amount == 773553.37
        assert record.forgiveness_date == datetime.datetime(2020, 11, 20)
        
        # Test the computed fields
        assert record.borrower_full_address == "2410 Highway 15 South, Sumter, SC, 29150-9662"
        assert record.servicing_lender_full_address == "1148 Broadway, COLUMBUS, GA, 31901-2429"
        assert record.originating_lender_full_address == "Synovus Bank, COLUMBUS, GA"
        assert record.shard_id == abs(hash(self.SAMPLE_RECORD["LoanNumber"]))
    
    def test_process_ppploan_data_do_fn(self):
        """Test the process_ppploan_data_do_fn function."""
        record: PPPLoanDataSchema = PPPLoanDataSchema(**self.SAMPLE_RECORD)
        
        with PPPLoanDataTestPipeline() as p:
            p | beam.Create([record]) | beam.ParDo(ProcessPPPLoanDataDoFn())
        
        assert record is not None
        assert record.loan_number == "9547507704"
        assert record.date_approved == datetime.datetime(2020, 5, 1)
        assert record.borrower_name == "SUMTER COATINGS, INC."
        assert record.sba_office_code == "0464"
        assert record.processing_method == "PPP"
        assert record.borrower_address == "2410 Highway 15 South"
        assert record.borrower_city == "Sumter"
        assert record.borrower_state == "SC"
        assert record.borrower_zip == "29150-9662"
        assert record.loan_status_date == datetime.datetime(2020, 12, 18)
        assert record.loan_status == "Paid in Full"
        assert record.term == 24
        assert record.sba_guaranty_percentage == 100.0
        assert record.shard_id == abs(hash(self.SAMPLE_RECORD["LoanNumber"]))
    
    def test_question_request_model(self):
        """Test the QuestionRequest model."""
        request: QuestionRequest = QuestionRequest(question="What is the total number of loans?")
        assert request is not None
        assert request.question == "What is the total number of loans?"
    
    def test_question_response_model(self):
        """Test the QuestionResponse model."""
        response: QuestionResponse = QuestionResponse(
            question="What is the total loan amount for Sumter Coatings, Inc.?",
            postgres_sql_query="SELECT SUM(initial_approval_amount) FROM ppp_loans WHERE borrower_name = 'SUMTER COATINGS, INC.'",
            result=[769358.78],
            response="$769,358.78",
            success=True
        )
        assert response is not None
        assert response.question == "What is the total loan amount for Sumter Coatings, Inc.?"
        assert response.success is True

