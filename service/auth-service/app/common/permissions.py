"""
권한 시스템 상수 및 유틸리티
"""

# 사용자 역할 정의
USER_ROLES = {
    "super_admin": {
        "display_name": "최고 관리자",
        "description": "시스템 전체 관리 권한",
        "permissions": ["*"]  # 모든 권한
    },
    "company_admin": {
        "display_name": "기업 관리자",
        "description": "기업 내 모든 권한",
        "permissions": ["manage_users", "view_reports", "edit_data", "export_data"]
    },
    "manager": {
        "display_name": "매니저",
        "description": "팀 관리 및 데이터 편집 권한",
        "permissions": ["view_reports", "edit_data", "export_data"]
    },
    "user": {
        "display_name": "일반 사용자",
        "description": "기본 데이터 조회 및 편집 권한",
        "permissions": ["view_reports", "edit_data"]
    },
    "viewer": {
        "display_name": "조회 전용",
        "description": "데이터 조회만 가능",
        "permissions": ["view_reports"]
    }
}

# 권한 정의
PERMISSIONS = {
    "manage_users": {
        "name": "사용자 관리",
        "description": "사용자 추가/수정/삭제 권한"
    },
    "view_reports": {
        "name": "리포트 조회",
        "description": "데이터 리포트 조회 권한"
    },
    "edit_data": {
        "name": "데이터 편집",
        "description": "데이터 수정/삭제 권한"
    },
    "export_data": {
        "name": "데이터 내보내기",
        "description": "데이터를 파일로 내보내기 권한"
    }
}

def get_role_permissions(role: str) -> list:
    """역할에 따른 권한 목록 반환"""
    role_info = USER_ROLES.get(role, {})
    return role_info.get("permissions", [])

def has_permission(user_permissions: dict, required_permission: str) -> bool:
    """사용자가 특정 권한을 가지고 있는지 확인"""
    if not user_permissions:
        return False
    
    # 모든 권한을 가진 경우
    if "*" in user_permissions.get("permissions", []):
        return True
    
    # 특정 권한 확인
    return user_permissions.get(required_permission, False)

def get_role_display_name(role: str) -> str:
    """역할의 표시명 반환"""
    role_info = USER_ROLES.get(role, {})
    return role_info.get("display_name", role)

def get_role_description(role: str) -> str:
    """역할의 설명 반환"""
    role_info = USER_ROLES.get(role, {})
    return role_info.get("description", "")

def is_valid_role(role: str) -> bool:
    """유효한 역할인지 확인"""
    return role in USER_ROLES

def get_available_roles() -> list:
    """사용 가능한 역할 목록 반환"""
    return list(USER_ROLES.keys())
