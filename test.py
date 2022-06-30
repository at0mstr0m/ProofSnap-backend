from main import generate_key_pair

private_key, public_key = '', ''

while not "123456789" in public_key:
    private_key, public_key = generate_key_pair()

print(private_key, public_key)
