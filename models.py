from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
import pandas as pd

#Pydantic Model for the PPP Data
class PPPDataRow(BaseModel):
    loan_number: str = Field(..., alias="LoanNumber")
    date_approved: Optional[datetime] = Field(None, alias="DateApproved")
    sba_office_code: Optional[str] = Field(None, alias="SBAOfficeCode")
    processing_method: Optional[str] = Field(None, alias="ProcessingMethod")
    borrower_name: Optional[str] = Field(None, alias="BorrowerName")
    borrower_address: Optional[str] = Field(None, alias="BorrowerAddress")
    borrower_city: Optional[str] = Field(None, alias="BorrowerCity")
    borrower_state: Optional[str] = Field(None, alias="BorrowerState")
    borrower_zip: Optional[str] = Field(None, alias="BorrowerZip")
    loan_status_date: Optional[datetime] = Field(None, alias="LoanStatusDate")
    loan_status: Optional[str] = Field(None, alias="LoanStatus")
    term: Optional[int] = Field(None, alias="Term")
    sba_guaranty_percentage: Optional[int] = Field(None, alias="SBAGuarantyPercentage")
    initial_approval_amount: Optional[float] = Field(None, alias="InitialApprovalAmount")
    current_approval_amount: Optional[float] = Field(None, alias="CurrentApprovalAmount")
    undisbursed_amount: Optional[float] = Field(None, alias="UndisbursedAmount")
    franchise_name: Optional[str] = Field(None, alias="FranchiseName")
    servicing_lender_location_id: Optional[str] = Field(None, alias="ServicingLenderLocationID")
    servicing_lender_name: Optional[str] = Field(None, alias="ServicingLenderName")
    servicing_lender_address: Optional[str] = Field(None, alias="ServicingLenderAddress")
    servicing_lender_city: Optional[str] = Field(None, alias="ServicingLenderCity")
    servicing_lender_state: Optional[str] = Field(None, alias="ServicingLenderState")
    servicing_lender_zip: Optional[str] = Field(None, alias="ServicingLenderZip")
    rural_urban_indicator: Optional[str] = Field(None, alias="RuralUrbanIndicator")
    hubzone_indicator: Optional[str] = Field(None, alias="HubzoneIndicator")
    lmi_indicator: Optional[str] = Field(None, alias="LMIIndicator")
    business_age_description: Optional[str] = Field(None, alias="BusinessAgeDescription")
    project_city: Optional[str] = Field(None, alias="ProjectCity")
    project_county_name: Optional[str] = Field(None, alias="ProjectCountyName")
    project_state: Optional[str] = Field(None, alias="ProjectState")
    project_zip: Optional[str] = Field(None, alias="ProjectZip")
    cd: Optional[str] = Field(None, alias="CD")
    jobs_reported: Optional[int] = Field(None, alias="JobsReported")
    naics_code: Optional[str] = Field(None, alias="NAICSCode")
    race: Optional[str] = Field(None, alias="Race")
    ethnicity: Optional[str] = Field(None, alias="Ethnicity")
    utilities_proceed: Optional[float] = Field(None, alias="UTILITIES_PROCEED")
    payroll_proceed: Optional[float] = Field(None, alias="PAYROLL_PROCEED")
    mortgage_interest_proceed: Optional[float] = Field(None, alias="MORTGAGE_INTEREST_PROCEED")
    rent_proceed: Optional[float] = Field(None, alias="RENT_PROCEED")
    refinance_eidl_proceed: Optional[float] = Field(None, alias="REFINANCE_EIDL_PROCEED")
    health_care_proceed: Optional[float] = Field(None, alias="HEALTH_CARE_PROCEED")
    debt_interest_proceed: Optional[float] = Field(None, alias="DEBT_INTEREST_PROCEED")
    business_type: Optional[str] = Field(None, alias="BusinessType")
    originating_lender_location_id: Optional[str] = Field(None, alias="OriginatingLenderLocationID")
    originating_lender: Optional[str] = Field(None, alias="OriginatingLender")
    originating_lender_city: Optional[str] = Field(None, alias="OriginatingLenderCity")
    originating_lender_state: Optional[str] = Field(None, alias="OriginatingLenderState")
    gender: Optional[str] = Field(None, alias="Gender")
    veteran: Optional[str] = Field(None, alias="Veteran")
    non_profit: Optional[bool] = Field(None, alias="NonProfit")
    forgiveness_amount: Optional[float] = Field(None, alias="ForgivenessAmount")
    forgiveness_date: Optional[datetime] = Field(None, alias="ForgivenessDate")

    @model_validator(mode='before')
    @classmethod
    def clean_data(cls, data):
        if not isinstance(data, dict):
            return data
            
        # Convert empty strings and various null representations to None
        null_values = {'', 'nan', 'none', 'null', 'na', 'n/a'}
        
        # Fields that should be strings even if they come as numbers
        string_fields = ['LoanNumber', 'SBAOfficeCode', 'ServicingLenderLocationID', 
                        'NAICSCode', 'OriginatingLenderLocationID']
        
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

    @field_validator("loan_number")
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
            
        date_fields = ["DateApproved", "LoanStatusDate", "ForgivenessDate"]
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

    @field_validator("term", "sba_guaranty_percentage", "jobs_reported")
    @classmethod
    def convert_to_int(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            # First convert to float to handle decimal strings, then to int
            return int(float(str(value).replace(',', '')))
        except (ValueError, TypeError):
            return None

    @field_validator("initial_approval_amount", "current_approval_amount", "undisbursed_amount", 
               "utilities_proceed", "payroll_proceed", "mortgage_interest_proceed", 
               "rent_proceed", "refinance_eidl_proceed", "health_care_proceed", 
               "debt_interest_proceed", "forgiveness_amount")
    @classmethod
    def convert_to_float(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        try:
            # Remove commas and convert to float
            return round(float(str(value).replace(',', '')), 2)
        except (ValueError, TypeError):
            return None

    @field_validator("non_profit")
    @classmethod
    def convert_to_bool(cls, value):
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        if isinstance(value, bool):
            return value
        return str(value).lower() in ["true", "yes", "1", "y"]