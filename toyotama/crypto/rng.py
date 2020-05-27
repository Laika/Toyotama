def lcg_crack(X, A=None, B=None, M=None):
    if A and B:
        M = gcd(X[2]-A*X[1]-B, X[1]-A*X[0]-B)

    Y = [X[i+1]-X[i] for i in range(len(X)-1)]
    print(Y)
    Z = [Y[i]*Y[i+3] - Y[i+1]*Y[i+2] for i in range(len(X)-4)]
    M = reduce(gcd, Z)

    if M and len(X) >= 3:
        A = (X[2]-X[1]) * pow(X[1]-X[0], -1, M) % M

    if A and M and len(X) >= 2:
        B = (X[1]-A*X[0]) % M

    assert [(A*X[i]+B)%M == X[i+1] for i in range(len(X)-1)]

    return A, B, M

