import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.config import FIREAUTH_CREDENTIALS_PATH


class FireAuth:
    """Initialize Firebase Authentication for server-side use."""

    def __init__(self) -> None:
        credential = credentials.Certificate(FIREAUTH_CREDENTIALS_PATH)
        self.app = self._create_app(credential)

    def sign_up_user(self, email: str, password: str):
        """Create a Firebase user and return its user record."""
        return firebase_auth.create_user(
            email=email,
            password=password,
            email_verified=False,
            app=self.app,
        )

    def get_user_uid_from_email(self, email: str) -> str:
        """Return the Firebase UID associated with an email address."""
        user_record = firebase_auth.get_user_by_email(email, app=self.app)
        return user_record.uid

    def delete_user(self, uid: str) -> None:
        """Delete a Firebase user by UID."""
        firebase_auth.delete_user(uid, app=self.app)

    def _create_app(self, credential):
        try:
            return firebase_admin.get_app()
        except ValueError:
            return firebase_admin.initialize_app(credential)
