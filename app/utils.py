# Import the CryptContext class from passlib's context module
# This class provides methods for password hashing and verification
from passlib.context import CryptContext

# Create a password context using bcrypt hashing algorithm
# The "deprecated='auto'" parameter allows the use of older hashing schemes
# when verifying passwords while preferring newer schemes by default
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Function to verify if a plain text password matches a hashed password
def verify_password(plain_password, hashed_password):
    # Use the verify method of the password context to check the password
    # Returns True if the plain_password matches the hashed_password
    return pwd_context.verify(plain_password, hashed_password)


# Function to generate a hashed password from a plain text password
def get_password_hash(password):
    # Use the hash method of the password context to create a password hash
    # Returns the hashed version of the input password
    return pwd_context.hash(password)
