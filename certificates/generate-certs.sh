# Create a directory for certificates:
mkdir certs my-safe-dir

# Generate the CA (Certificate Authority) certificate:
cockroach cert create-ca --certs-dir=certs --ca-key=my-safe-dir/ca.key

# Generate node certificates for cock1, cock2, and cock3:
cockroach cert create-node eu1 eu2 us1 us2 asia1 asia2 afr1 afr2 localhost 127.0.0.1 --certs-dir=certs --ca-key=my-safe-dir/ca.key

# Generate a client certificate for the root user:
cockroach cert create-client root --certs-dir=certs --ca-key=my-safe-dir/ca.key
