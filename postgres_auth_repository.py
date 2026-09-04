from __future__ import annotations
from uuid import UUID
from user_schema import User
from auth_security import hash_password, verify_password
from pydantic import EmailStr


class PostgresAuthRepository:
    def __init__(self, conn):
        self.conn = conn

    def ping(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

    def create_user(self, email: str, password: str, display_name: str = "") -> User:
        password_hash = hash_password(password)
        user_id = UUID(str(__import__('uuid').uuid4()))
        with self.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO users (id, email, password_hash, display_name, role, status)
                   VALUES (%s, %s, %s, 'user', 'active')
                   RETURNING id, email, display_name, role, status""",
                (user_id, email, password_hash, display_name),
            )
            row = cur.fetchone()
        return User(user_id=row[0], email=EmailStr(row[1]), display_name=row[2] or "", role=row[3], status=row[4])

    def get_user_by_email(self, email: str) -> User | None:
        with self.conn.cursor() as cur:
            cur.execute("SELECT id, email, display_name, role, status, password_hash FROM users WHERE lower(email)=lower(%s)", (email,))
            row = cur.fetchone()
        if not row:
            return None
        return User(user_id=row[0], email=EmailStr(row[1]), display_name=row[2] or "", role=row[3], status=row[4], password_hash=row[5])

    def verify_user(self, email: str, password: str) -> User | None:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_session(self, user_id: UUID, token_hash: str, expires_at):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO user_sessions (id, user_id, token_hash, expires_at) VALUES (%s, %s, %s, %s)",
                (__import__('uuid').uuid4(), user_id, token_hash, expires_at),
            )

    def resolve_session(self, token_hash: str):
        with self.conn.cursor() as cur:
            cur.execute(
                """SELECT u.id, u.email, u.display_name, u.role, u.status
                   FROM user_sessions s JOIN users u ON u.id=s.user_id
                   WHERE s.token_hash=%s AND s.expires_at > NOW()""",
                (token_hash,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return User(user_id=row[0], email=EmailStr(row[1]), display_name=row[2] or "", role=row[3], status=row[4])
