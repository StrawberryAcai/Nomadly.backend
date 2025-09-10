from pydantic import BaseModel, Field, confloat

class Origin(BaseModel):
    longitude: confloat(ge=-180, le=180) = Field(..., description="경도")
    latitude: confloat(ge=-90, le=90) = Field(..., description="위도")