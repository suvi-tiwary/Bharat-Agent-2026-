
from typing import Optional, List
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    category: Optional[str] = None


class LocationInfo(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    village: Optional[str] = None
    pincode: Optional[str] = None


class LandInfo(BaseModel):
    ownership_type: Optional[str] = None
    total_land_acres: Optional[float] = None
    irrigated_land_acres: Optional[float] = None
    cultivated_land_acres: Optional[float] = None


class FarmingInfo(BaseModel):
    farmer_type: Optional[str] = None
    crops: List[str] = Field(default_factory=list)
    cropping_season: List[str] = Field(default_factory=list)
    livestock: List[str] = Field(default_factory=list)
    farming_activities: List[str] = Field(default_factory=list)


class FinancialInfo(BaseModel):
    annual_income: Optional[float] = None
    income_source: List[str] = Field(default_factory=list)
    has_bank_account: Optional[bool] = None
    has_kisan_credit_card: Optional[bool] = None


class DocumentInfo(BaseModel):
    aadhaar: Optional[bool] = None
    land_record: Optional[bool] = None
    bank_details: Optional[bool] = None
    income_certificate: Optional[bool] = None
    caste_certificate: Optional[bool] = None


class FarmerProfile(BaseModel):
    personal: PersonalInfo = Field(default_factory=PersonalInfo)
    location: LocationInfo = Field(default_factory=LocationInfo)
    land: LandInfo = Field(default_factory=LandInfo)
    farming: FarmingInfo = Field(default_factory=FarmingInfo)
    financial: FinancialInfo = Field(default_factory=FinancialInfo)
    documents: DocumentInfo = Field(default_factory=DocumentInfo)


class ProfileResponse(BaseModel):
    updated_profile: FarmerProfile
    extracted_fields: List[str]
    missing_information: List[str]
    next_question: Optional[str] = None