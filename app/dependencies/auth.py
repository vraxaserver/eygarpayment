from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import jwt_handler
from app.schemas.common import UserInfo, HostInfo
import httpx
from app.core.config import settings

# Security scheme for JWT Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInfo:
    """
    Validate JWT token with Django auth service and return user info.
    """
    token = credentials.credentials

    # Verify token with Django auth service
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/profile/",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user_data = response.json()
            print("==========user_data==============")
            print(f"{settings.AUTH_SERVICE_URL}")
            print(user_data)

            # Map Django user response to UserInfo
            return UserInfo(
                id=user_data.get("id"),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                is_active=user_data.get("is_active", True),
                is_verified=user_data.get("is_verified", False),
                is_staff=user_data.get("is_staff", False),
                is_superuser=user_data.get("is_superuser", False)
            )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service timeout"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserInfo = Depends(get_current_user),
) -> UserInfo:
    """
    Ensure the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# async def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ) -> int:
#     """
#     Dependency to get current authenticated user from JWT token.
    
#     Args:
#         credentials: HTTP Bearer credentials
        
#     Returns:
#         int: User ID from token
        
#     Raises:
#         HTTPException: If token is invalid or missing
#     """
#     token = credentials.credentials
    
#     if not token:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not authenticated",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     try:
#         user_id = jwt_handler.get_user_id_from_token(token)
#         return user_id
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
