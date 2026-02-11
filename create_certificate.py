from datetime import datetime, timedelta, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_self_signed_cert():
    # 1. Genera la chiave privata
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        
    )

    # 2. Configura i dettagli del certificato (Subject e Issuer)
    # Essendo auto-firmato, "Chi lo emette" (Issuer) e "A chi è intestato" (Subject) sono uguali.
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"IT"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Italia"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Sardegna"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Progetto Network Security"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"), # <--- FONDAMENTALE per il client
    ])
    
    # Configura le estensioni (Subject Alternative Name - SAN)
    # I browser e i client moderni guardano qui invece del Common Name
    alt_names = x509.SubjectAlternativeName([
        x509.DNSName(u"localhost"),
        x509.DNSName(u"127.0.0.1"),
    ])

    # 3. Costruisci il certificato
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365)) # Valido 1 anno
        .add_extension(alt_names, critical=False)
        .sign(key, hashes.SHA256())
    )

    # 4. Scrivi la chiave privata su file (key.pem)
    password = b"password123"  # Password per proteggere la chiave privata
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        ))

    # 5. Scrivi il certificato pubblico su file (cert.pem)
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("File 'cert.pem' e 'key.pem' generati con successo!")

if __name__ == "__main__":
    generate_self_signed_cert()