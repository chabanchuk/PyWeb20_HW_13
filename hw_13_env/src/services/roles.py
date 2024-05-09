from fastapi import Request, Depends, HTTPException, status
from typing import List

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        # Виведемо інформацію про роль користувача та дозволені ролі для доступу
        print(f"User Role: {user.role}, Allowed Roles: {self.allowed_roles}")

        # Перевірка чи має користувач необхідну роль для доступу
        if user.role not in self.allowed_roles:
            # Якщо роль не відповідає дозволеним ролям, піднімемо HTTPException з кодом 403 (FORBIDDEN)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access forbidden: User does not have required role"
            )
