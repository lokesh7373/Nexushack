import operator
from pydantic import BaseModel, Field
from typing import Annotated,Literal, TypedDict, List, Set, Optional




class PlannerStepSchema(BaseModel):
        step_no : int = Field(description='Denotes the current step number')
        robot_type : Literal["QUADRUPED"] = Field(description='Robot needed for navigating to target location')
        action : str = Field(description='The action to perform')
        dependencies : Optional[List[int]] = Field(description='Any dependency with previous step')
        
class PlannerSchema(BaseModel):
    plan : List[PlannerStepSchema]