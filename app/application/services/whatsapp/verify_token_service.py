from application.interfaces.service_interface import ServiceInterface
from typing import Any, Dict
from flask import jsonify


class VerifyTokenService(ServiceInterface):

    def execute(self, token: str, challenge: str) -> Dict[str, Any]:
        """
        Execute the service logic to verify a token.
        """
        print(
            f"Executing token verification with token: {token} and challenge: {challenge}"
        )

        # Just for test purposes, we will use a hardcoded access token
        accessToken = "Q84q92isAdchJITILc8o6xxwXPWeOW"

        if token is None or challenge is None or token != accessToken:
            raise Exception("Token verification failed.")

        return jsonify({"message": "Token verified successfully.", "status": 200}), 200

    
    def validate(self, token: str) -> bool:
        """
        Validate the input for the service.
        """
        # # Check if the token is a non-empty string
        # if not isinstance(token, str) or not token.strip():
        #     raise ValueError("Invalid token provided.")
        return True
