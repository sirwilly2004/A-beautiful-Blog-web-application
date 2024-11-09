from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def create_token(secret_key, expiration):
    s = Serializer(secret_key, expires_in=expiration)
    token = s.dumps({'user_id': 123}).decode('utf-8')
    return token

def verify_token(secret_key, token):
    s = Serializer(secret_key)
    try:
        data = s.loads(token)
        return data
    except Exception as e:
        print("Token is invalid:", e)
        return None

if __name__ == "__main__":
    secret_key = "my_secret_key"
    expiration = 3600  # Token valid for 1 hour

    token = create_token(secret_key, expiration)
    print("Generated Token:", token)

    # Verify the token
    data = verify_token(secret_key, token)
    print("Decoded Data:", data)