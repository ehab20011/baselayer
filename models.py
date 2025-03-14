from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import pandas as pd

#Pydantic Model for the PPP Data
class PPPDataRow(BaseModel):
    LoanNumber: str = Field(..., alias="loan_number")
    DateApproved: Optional[datetime] = Field(None, alias="date_approved")
    SBAOfficeCode: Optional[str] = Field(None, alias="sba_office_code")
    ProcessingMethod: Optional[str] = Field(None, alias="processing_method")
    BorrowerName: Optional[str] = Field(None, alias="borrower_name")
    BorrowerAddress: Optional[str] = Field(None, alias="borrower_address")
    BorrowerCity: Optional[str] = Field(None, alias="borrower_city")
    BorrowerState: Optional[str] = Field(None, alias="borrower_state")
    BorrowerZip: Optional[str] = Field(None, alias="borrower_zip")
    LoanStatusDate: Optional[datetime] = Field(None, alias="loan_status_date")
    LoanStatus: Optional[str] = Field(None, alias="loan_status")
    Term: Optional[int] = Field(None, alias="term")
    SBAGuarantyPercentage: Optional[int] = Field(None, alias="sba_guaranty_percentage")
    InitialApprovalAmount: Optional[float] = Field(None, alias="initial_approval_amount")
    CurrentApprovalAmount: Optional[float] = Field(None, alias="current_approval_amount")
    UndisbursedAmount: Optional[float] = Field(None, alias="undisbursed_amount")
    FranchiseName: Optional[str] = Field(None, alias="franchise_name")
    ServicingLenderLocationID: Optional[str] = Field(None, alias="servicing_lender_location_id")
    ServicingLenderName: Optional[str] = Field(None, alias="servicing_lender_name")
    ServicingLenderAddress: Optional[str] = Field(None, alias="servicing_lender_address")
    ServicingLenderCity: Optional[str] = Field(None, alias="servicing_lender_city")
    ServicingLenderState: Optional[str] = Field(None, alias="servicing_lender_state")
    ServicingLenderZip: Optional[str] = Field(None, alias="servicing_lender_zip")
    RuralUrbanIndicator: Optional[str] = Field(None, alias="rural_urban_indicator")
    HubzoneIndicator: Optional[str] = Field(None, alias="hubzone_indicator")
    LMIIndicator: Optional[str] = Field(None, alias="lmi_indicator")
    BusinessAgeDescription: Optional[str] = Field(None, alias="business_age_description")
    ProjectCity: Optional[str] = Field(None, alias="project_city")
    ProjectCountyName: Optional[str] = Field(None, alias="project_county_name")
    ProjectState: Optional[str] = Field(None, alias="project_state")
    ProjectZip: Optional[str] = Field(None, alias="project_zip")
    CD: Optional[str] = Field(None, alias="cd")
    JobsReported: Optional[int] = Field(None, alias="jobs_reported")
    NAICSCode: Optional[str] = Field(None, alias="naics_code")
    Race: Optional[str] = Field(None, alias="race")
    Ethnicity: Optional[str] = Field(None, alias="ethnicity")
    UTILITIES_PROCEED: Optional[float] = Field(None, alias="utilities_proceed")
    PAYROLL_PROCEED: Optional[float] = Field(None, alias="payroll_proceed")
    MORTGAGE_INTEREST_PROCEED: Optional[float] = Field(None, alias="mortgage_interest_proceed")
    RENT_PROCEED: Optional[float] = Field(None, alias="rent_proceed")
    REFINANCE_EIDL_PROCEED: Optional[float] = Field(None, alias="refinance_eidl_proceed")
    HEALTH_CARE_PROCEED: Optional[float] = Field(None, alias="health_care_proceed")
    DEBT_INTEREST_PROCEED: Optional[float] = Field(None, alias="debt_interest_proceed")
    BusinessType: Optional[str] = Field(None, alias="business_type")
    OriginatingLenderLocationID: Optional[str] = Field(None, alias="originating_lender_location_id")
    OriginatingLender: Optional[str] = Field(None, alias="originating_lender")
    OriginatingLenderCity: Optional[str] = Field(None, alias="originating_lender_city")
    OriginatingLenderState: Optional[str] = Field(None, alias="originating_lender_state")
    Gender: Optional[str] = Field(None, alias="gender")
    Veteran: Optional[str] = Field(None, alias="veteran")
    NonProfit: Optional[bool] = Field(None, alias="non_profit")
    ForgivenessAmount: Optional[float] = Field(None, alias="forgiveness_amount")
    ForgivenessDate: Optional[datetime] = Field(None, alias="forgiveness_date")

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def clean_data(cls, data):
        if not isinstance(data, dict):
            return data
            
        # Convert empty strings and various null representations to None
        null_values = {'', 'nan', 'none', 'null', 'na', 'n/a'}
        
        # Fields that should be strings even if they come as numbers
        string_fields = ['loan_number', 'sba_office_code', 'servicing_lender_location_id', 
                        'naics_code', 'originating_lender_location_id']
        
        for key, value in data.items():
            # Handle null values
            if isinstance(value, str):
                value_lower = value.lower().strip()
                if value_lower in null_values:
                    data[key] = None
                    continue
            
            # Convert float 'nan' to None
            if pd.isna(value):
                data[key] = None
                continue
                
            # Convert numeric fields that should be strings
            if key in string_fields and value is not None:
                if isinstance(value, (int, float)):
                    # Remove .0 from float numbers when converting to string
                    data[key] = str(int(value) if float(value).is_integer() else value)
                else:
                    data[key] = str(value)
                    
        return data

    @field_validator("LoanNumber")
    @classmethod
    def loan_Number_must_not_be_empty(cls, value):
        if not value or str(value).strip() == "":
            raise ValueError("LoanNumber field cannot be empty")
        return str(value)

    @model_validator(mode='before')
    @classmethod
    def parse_dates(cls, data):
        if not isinstance(data, dict):
            return data
            
        date_fields = ["date_approved", "loan_status_date", "forgiveness_date"]
        for field in date_fields:
            if field in data and data[field] is not None:
                try:
                    # First try the original format
                    data[field] = datetime.strptime(str(data[field]), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Then try the alternative format
                        data[field] = datetime.strptime(str(data[field]), "%m/%d/%Y")
                    except ValueError:
                        data[field] = None  # Set to None if both formats fail
        return data

    @field_validator("Term", "SBAGuarantyPercentage", "JobsReported")
    @classmethod
    def convert_to_int(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            # First convert to float to handle decimal strings, then to int
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return None

    @field_validator("InitialApprovalAmount", "CurrentApprovalAmount", "UndisbursedAmount", 
               "UTILITIES_PROCEED", "PAYROLL_PROCEED", "MORTGAGE_INTEREST_PROCEED", 
               "RENT_PROCEED", "REFINANCE_EIDL_PROCEED", "HEALTH_CARE_PROCEED", 
               "DEBT_INTEREST_PROCEED", "ForgivenessAmount")
    @classmethod
    def convert_to_float(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            # Remove commas and convert to float
            return round(float(str(value).replace(',', '')), 2)
        except (ValueError, TypeError):
            return None

    @field_validator("NonProfit")
    @classmethod
    def convert_to_bool(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() in ["true", "yes", "1", "y"]