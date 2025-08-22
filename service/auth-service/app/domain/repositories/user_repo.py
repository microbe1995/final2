from sqlalchemy.orm import Session
from app.domain.entities.user import User
from app.domain.schemas.auth import UserCreate, UserUpdate

class UserRepository:
    """사용자 리포지토리"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> User:
        """ID로 사용자 조회"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> User:
        """사용자명으로 사용자 조회"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> User:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, user_data: UserCreate) -> User:
        """사용자 생성"""
        db_user = User(**user_data.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update(self, user_id: int, user_data: UserUpdate) -> User:
        """사용자 정보 업데이트"""
        db_user = self.get_by_id(user_id)
        if db_user:
            for field, value in user_data.dict(exclude_unset=True).items():
                setattr(db_user, field, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """사용자 삭제"""
        db_user = self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    def list_users(self, skip: int = 0, limit: int = 100):
        """사용자 목록 조회"""
        return self.db.query(User).offset(skip).limit(limit).all()
