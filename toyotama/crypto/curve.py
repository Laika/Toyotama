from collections import namedtuple

Curve = namedtuple("Curve", ["name", "p", "a", "b", "order", "gx", "gy"])

P192 = Curve(
    name="P192",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF,
    a=-3,
    b=0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831,
    gx=0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
    gy=0x7192B95FFC8DA78631011ED6B24CDD573F977A11E794811,
)


P224 = Curve(
    name="P224",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF000000000000000000000001,
    a=-3,
    b=0xB4050A850C04B3ABF54132565044B0B7D7BFD8BA270B39432355FFB4,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFF16A2E0B8F03E13DD29455C5C2A3D,
    gx=0xB70E0CBD6BB4BF7F321390B94A03C1D356C21122343280D6115C1D21,
    gy=0xBD376388B5F723FB4C22DFE6CD4375A05A07476444D5819985007E34,
)
P256 = Curve(
    name="P256",
    p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
    a=-3,
    b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
    order=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
    gx=0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
    gy=0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
)
P384 = Curve(
    name="P384",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFF0000000000000000FFFFFFFF,
    a=-3,
    b=0xB3312FA7E23EE7E4988E056BE3F82D19181D9C6EFE8141120314088F5013875AC656398D8A2ED19D2A85C8EDD3EC2AEF,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFC7634D81F4372DDF581A0DB248B0A77AECEC196ACCC52973,
    gx=0xAA87CA22BE8B05378EB1C71EF320AD746E1D3B628BA79B9859F741E082542A385502F25DBF55296C3A545E3872760AB7,
    gy=0x3617DE4A96262C6F5D9E98BF9292DC29F8F41DBD289A147CE9DA3113B5F0B8C00A60B1CE1D7E819D7A431D7C90EA0E5F,
)
P521 = Curve(
    name="P521",
    p=0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
    a=-3,
    b=0x51953EB9618E1C9A1F929A21A0B68540EEA2DA725B99B315F3B8B489918EF109E156193951EC7E937B1652C0BD3BB1BF073573DF883D2C34F1EF451FD46B503F00,
    order=0x1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFA51868783BF2F966B7FCC0148F709A5D03BB5C9B8899C47AEBB6FB71E91386409,
    gx=0xC6858E06B70404E9CD9E3ECB662395B4429C648139053FB521F828AF606B4D3DBAA14B5E77EFE75928FE1DC127A2FFA8DE3348B3C1856A429BF97E7E31C2E5BD66,
    gy=0x11839296A789A3BC0045C8A5FB42C7D1BD998F54449579B446817AFBD17273E662C97EE72995EF42640C550B9013FAD0761353C7086A272C24088BE94769FD16650,
)
W25519 = Curve(
    name="W25519",
    p=0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFED,
    a=0x2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA984914A144,
    b=0x7B425ED097B425ED097B425ED097B425ED097B425ED097B4260B5E9C7710C864,
    order=0x1000000000000000000000000000000014DEF9DEA2F79CD65812631A5CF5D3ED,
    gx=0x2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD245A,
    gy=0x5F51E65E475F794B1FE122D388B72EB36DC2B28192839E4DD6163A5D81312C14,
)
W448 = Curve(
    name="W448",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
    a=0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA9FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE1A76D41F,
    b=0x5ED097B425ED097B425ED097B425ED097B425ED097B425ED097B425E71C71C71C71C71C71C71C71C71C71C71C71C71C71C72C87B7CC69F70,
    order=0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7CCA23E9C44EDB49AED63690216CC2728DC58F552378C292AB5844F3,
    gx=0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0000000000000000000000000000000000000000000000000000CB91,
    gy=0x7D235D1295F5B1F66C98AB6E58326FCECBAE5D34F55545D060F75DC28DF3F6EDB8027E2346430D211312C4B150677AF76FD7223D457B5B1A,
)

secp192k1 = Curve(
    name="secp192k1",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFEE37,
    a=0x0,
    b=0x3,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFE26F2FC170F69466A74DEFD8D,
    gx=0xDB4FF10EC057E9AE26B07D0280B7F4341DA5D1B1EAE06C7D,
    gy=0x9B2F2F6D9C5628A7844163D015BE86344082AA88D95E2F9D,
)

secp224k1 = Curve(
    name="secp224k1",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFE56D,
    a=0x0,
    b=0x5,
    order=0x10000000000000000000000000001DCE8D2EC6184CAF0A971769FB1F7,
    gx=0xA1455B334DF099DF30FC28A169A467E9E47075A90F7E650EB6B7A45C,
    gy=0x7E089FED7FBA344282CAFBD6F7E319F7C0B0BD59E2CA4BDB556D61A5,
)

secp256k1 = Curve(
    name="secp256k1",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
    a=0x0,
    b=0x7,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
    gx=0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    gy=0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

secp192r1 = Curve(
    name="secp192r1",
    p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFF,
    a=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFFFFFFFFFFFC,
    b=0x64210519E59C80E70FA7E9AB72243049FEB8DEECC146B9B1,
    order=0xFFFFFFFFFFFFFFFFFFFFFFFF99DEF836146BC9B1B4D22831,
    gx=0x188DA80EB03090F67CBF20EB43A18800F4FF0AFD82FF1012,
    gy=0x07192B95FFC8DA78631011ED6B24CDD573F977A11E794811,
)

brainpoolP160r1 = Curve(  # noqa: N816
    name="brainpoolP160r1",
    p=0xE95E4A5F737059DC60DFC7AD95B3D8139515620F,
    a=0x340E7BE2A280EB74E2BE61BADA745D97E8F7C300,
    b=0x1E589A8595423412134FAA2DBDEC95C8D8675E58,
    order=0xE95E4A5F737059DC60DF5991D45029409E60FC09,
    gx=0xBED5AF16EA3F6A4F62938C4631EB5AF7BDBCDBC3,
    gy=0x1667CB477A1A8EC338F94741669C976316DA6321,
)

brainpoolP192r1 = Curve(  # noqa: N816
    name="brainpoolP192r1",
    p=0xC302F41D932A36CDA7A3463093D18DB78FCE476DE1A86297,
    a=0x6A91174076B1E0E19C39C031FE8685C1CAE040E5C69A28EF,
    b=0x469A28EF7C28CCA3DC721D044F4496BCCA7EF4146FBF25C9,
    order=0xC302F41D932A36CDA7A3462F9E9E916B5BE8F1029AC4ACC1,
    gx=0xC0A0647EAAB6A48753B033C56CB0F0900A2F5C4853375FD6,
    gy=0x14B690866ABD5BB88B5F4828C1490002E6773FA2FA299B8F,
)

brainpoolP224r1 = Curve(  # noqa: N816
    name="brainpoolP224r1",
    p=0xD7C134AA264366862A18302575D1D787B09F075797DA89F57EC8C0FF,
    a=0x68A5E62CA9CE6C1C299803A6C1530B514E182AD8B0042A59CAD29F43,
    b=0x2580F63CCFE44138870713B1A92369E33E2135D266DBB372386C400B,
    order=0xD7C134AA264366862A18302575D0FB98D116BC4B6DDEBCA3A5A7939F,
    gx=0x0D9029AD2C7E5CF4340823B2A87DC68C9E4CE3174C1E6EFDEE12C07D,
    gy=0x58AA56F772C0726F24C6B89E4ECDAC24354B9E99CAA3F6D3761402CD,
)

brainpoolP256r1 = Curve(  # noqa: N816
    name="brainpoolP256r1",
    p=0xA9FB57DBA1EEA9BC3E660A909D838D726E3BF623D52620282013481D1F6E5377,
    a=0x7D5A0975FC2C3057EEF67530417AFFE7FB8055C126DC5C6CE94A4B44F330B5D9,
    b=0x26DC5C6CE94A4B44F330B5D9BBD77CBF958416295CF7E1CE6BCCDC18FF8C07B6,
    order=0xA9FB57DBA1EEA9BC3E660A909D838D718C397AA3B561A6F7901E0E82974856A7,
    gx=0x8BD2AEB9CB7E57CB2C4B482FFC81B7AFB9DE27E1E3BD23C23A4453BD9ACE3262,
    gy=0x547EF835C3DAC4FD97F8461A14611DC9C27745132DED8E545C1D54C72F046997,
)

brainpoolP320r1 = Curve(  # noqa: N816
    name="brainpoolP320r1",
    p=0xD35E472036BC4FB7E13C785ED201E065F98FCFA6F6F40DEF4F92B9EC7893EC28FCD412B1F1B32E27,
    a=0x3EE30B568FBAB0F883CCEBD46D3F3BB8A2A73513F5EB79DA66190EB085FFA9F492F375A97D860EB4,
    b=0x520883949DFDBC42D3AD198640688A6FE13F41349554B49ACC31DCCD884539816F5EB4AC8FB1F1A6,
    order=0xD35E472036BC4FB7E13C785ED201E065F98FCFA5B68F12A32D482EC7EE8658E98691555B44C59311,
    gx=0x43BD7E9AFB53D8B85289BCC48EE5BFE6F20137D10A087EB6E7871E2A10A599C710AF8D0D39E20611,
    gy=0x14FDD05545EC1CC8AB4093247F77275E0743FFED117182EAA9C77877AAAC6AC7D35245D1692E8EE1,
)

brainpoolP384r1 = Curve(  # noqa: N816
    name="brainpoolP384r1",
    p=0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B412B1DA197FB71123ACD3A729901D1A71874700133107EC53,
    a=0x7BC382C63D8C150C3C72080ACE05AFA0C2BEA28E4FB22787139165EFBA91F90F8AA5814A503AD4EB04A8C7DD22CE2826,
    b=0x04A8C7DD22CE28268B39B55416F0447C2FB77DE107DCD2A62E880EA53EEB62D57CB4390295DBC9943AB78696FA504C11,
    order=0x8CB91E82A3386D280F5D6F7E50E641DF152F7109ED5456B31F166E6CAC0425A7CF3AB6AF6B7FC3103B883202E9046565,
    gx=0x1D1C64F068CF45FFA2A63A81B7C13F6B8847A3E77EF14FE3DB7FCAFE0CBD10E8E826E03436D646AAEF87B2E247D4AF1E,
    gy=0x8ABE1D7520F9C2A45CB1EB8E95CFD55262B70B29FEEC5864E19C054FF99129280E4646217791811142820341263C5315,
)

brainpoolP512r1 = Curve(  # noqa: N816
    name="brainpoolP512r1",
    p=0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA703308717D4D9B009BC66842AECDA12AE6A380E62881FF2F2D82C68528AA6056583A48F3,
    a=0x7830A3318B603B89E2327145AC234CC594CBDD8D3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CA,
    b=0x3DF91610A83441CAEA9863BC2DED5D5AA8253AA10A2EF1C98B9AC8B57F1117A72BF2C7B9E7C1AC4D77FC94CADC083E67984050B75EBAE5DD2809BD638016F723,
    order=0xAADD9DB8DBE9C48B3FD4E6AE33C9FC07CB308DB3B3C9D20ED6639CCA70330870553E5C414CA92619418661197FAC10471DB1D381085DDADDB58796829CA90069,
    gx=0x81AEE4BDD82ED9645A21322E9C4C6A9385ED9F70B5D916C1B43B62EEF4D0098EFF3B1F78E2D0D48D50D1687B93B97D5F7C6D5047406A5E688B352209BCB9F822,
    gy=0x7DDE385D566332ECC0EABFA9CF7822FDF209F70024A57B1AA000C55B881F8111B2DCDE494A5F485E5BCA4BD88A2763AED1CA2B2FA8F0540678CD1E0F3AD80892,
)


__all__ = [
    "Curve",
    "P192",
    "P224",
    "P256",
    "P384",
    "P521",
    "W25519",
    "W448",
    "secp192k1",
    "secp224k1",
    "secp256k1",
    "secp192r1",
    "brainpoolP160r1",
    "brainpoolP192r1",
    "brainpoolP224r1",
    "brainpoolP256r1",
    "brainpoolP320r1",
    "brainpoolP384r1",
    "brainpoolP512r1",
]
