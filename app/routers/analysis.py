from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from app.analysis.call_analyzer import analyze_call_data
import os
import tempfile
import shutil
from typing import Dict, Any

router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"],
    responses={404: {"description": "Not found"}},
)

# Store results temporarily
analysis_results = {}

@router.post("/upload-and-analyze")
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload a call data CSV file and analyze it.
    Returns analysis results including shift counts, resource distribution, and non-repetitive calls.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        # Save uploaded file to temp file
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Analyze the data
        result = analyze_call_data(temp_file_path)
        
        # Store the result with a unique ID
        file_id = os.path.splitext(file.filename)[0]
        analysis_results[file_id] = result
        
        return {
            "file_id": file_id,
            "message": "Analysis completed successfully",
            "result": result
        }
    except Exception as e:
        # Log the error for backend debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"Analysis error: {str(e)}\n{error_details}")
        
        # Return more useful error information
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

@router.get("/results/{file_id}")
async def get_results(file_id: str):
    """
    Retrieve analysis results by file ID.
    """
    if file_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return {"file_id": file_id, "result": analysis_results[file_id]}

@router.get("/sample-data")
async def get_sample_data():
    """
    Return sample data structure for frontend development.
    """
    sample_data = {
        "shift_counts": {
            "Shift 1": 6072,
            "Shift 2": 7241,
            "Shift 3": 6385,
            "Shift 4": 2229
        },
        "resource_counts": {
            "5 AM - 9 AM": {"total_calls": 1623, "resources": 1, "calls_per_resource": 1623},
            "9 AM - 11 AM": {"total_calls": 2153, "resources": 2, "calls_per_resource": 1076.5},
            "11 AM - 2 PM": {"total_calls": 2296, "resources": 3, "calls_per_resource": 765.33},
            "2 PM - 6 PM": {"total_calls": 2792, "resources": 2, "calls_per_resource": 1396},
            "6 PM - 8 PM": {"total_calls": 1297, "resources": 2, "calls_per_resource": 648.5},
            "8 PM - 5 AM": {"total_calls": 933, "resources": 1, "calls_per_resource": 933}
        },
        "non_repetitive_counts": {
            "Shift 1": 3464.83,
            "Shift 2": 3237.83,
            "Shift 3": 2809.83,
            "Shift 4": 1581.5
        },
        "hourly_counts": {
            "1 AM": 85,
            "2 AM": 64,
            "3 AM": 42,
            "4 AM": 57,
            "5 AM": 124,
            "6 AM": 256,
            "7 AM": 387,
            "8 AM": 513,
            "9 AM": 856,
            "10 AM": 1072,
            "11 AM": 934,
            "12 PM": 785,
            "1 PM": 684,
            "2 PM": 827,
            "3 PM": 975,
            "4 PM": 1073,
            "5 PM": 745,
            "6 PM": 642,
            "7 PM": 528,
            "8 PM": 380,
            "9 PM": 246,
            "10 PM": 184,
            "11 PM": 132,
            "12 AM": 98
        }
    }
    
    return sample_data 