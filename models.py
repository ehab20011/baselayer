import re
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime
import pandas as pd

def camel_to_snake(name: str) -> str:
    """Convert CamelCase (or PascalCase) to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

class PPPLoanDataSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

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
    HubzoneIndicator: Optional[bool] = Field(None, alias="hubzone_indicator")
    LMIIndicator: Optional[bool] = Field(None, alias="lmi_indicator")
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
    UtilitiesProceed: Optional[float] = Field(None, alias="utilities_proceed")
    PayrollProceed: Optional[float] = Field(None, alias="payroll_proceed")
    MortgageInterestProceed: Optional[float] = Field(None, alias="mortgage_interest_proceed")
    RentProceed: Optional[float] = Field(None, alias="rent_proceed")
    RefinanceEidlProceed: Optional[float] = Field(None, alias="refinance_eidl_proceed")
    HealthCareProceed: Optional[float] = Field(None, alias="health_care_proceed")
    DebtInterestProceed: Optional[float] = Field(None, alias="debt_interest_proceed")
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

    @model_validator(mode='before')
    @classmethod
    def clean_null_values(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert common null representations to None."""
        if not isinstance(data, dict):
            return data

        null_values = {'', 'nan', 'none', 'null', 'na', 'n/a'}
        cleaned_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                value = value.strip()
                if value.lower() in null_values:
                    cleaned_data[key] = None
                    continue
            if pd.isna(value):
                cleaned_data[key] = None
                continue
            cleaned_data[key] = value
            
        return cleaned_data

    @field_validator("LoanNumber", "SBAOfficeCode", "ServicingLenderLocationID", 
                    "NAICSCode", "OriginatingLenderLocationID", mode="before")
    @classmethod
    def convert_to_string(cls, value: Any) -> Optional[str]:
        """Convert fields that must be strings to proper string format."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        return str(value)

    @field_validator("DateApproved", "LoanStatusDate", "ForgivenessDate", mode="before")
    @classmethod
    def parse_date(cls, value: Any) -> Optional[datetime]:
        """Parse date fields from various formats."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return None
        if isinstance(value, datetime):
            return value
        for fmt in ("%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(str(value).strip(), fmt)
            except ValueError:
                continue
        return None

    @field_validator("LoanNumber", mode="before")
    @classmethod
    def validate_loan_number(cls, value: Any) -> str:
        """Ensure loan number is not empty and is a string."""
        if value is None or str(value).strip() == "":
            raise ValueError("LoanNumber field cannot be empty")
        return str(value)
