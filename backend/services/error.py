from fastapi import HTTPException, status
from typing import Dict, Any

class APIError:
    """Custom API error handling"""
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> HTTPException:
        """401 Unauthorized error"""
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message
        )
    
    @staticmethod
    def bad_request(message: str = "Bad Request") -> HTTPException:
        """400 Bad Request error"""
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    @staticmethod
    def not_found(message: str = "Not Found") -> HTTPException:
        """404 Not Found error"""
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    
    @staticmethod
    def validation_error(field: str, message: str) -> Dict[str, Any]:
        """422 Validation error response"""
        return {
            "error": "validation_error",
            "field": field,
            "message": message
        }
